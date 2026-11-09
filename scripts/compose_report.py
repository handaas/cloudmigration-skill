#!/usr/bin/env python3
"""Compose a cloud-migration (上云) big-data report by orchestrating the cloudmigration MCP.

Calls the upstream cloudmigration-mcp-server tools and assembles a structured
JSON payload rendered into a professional HTML / Markdown report. Supports
``--dry-run`` which returns a well-formed skeleton from the bundled sample data
WITHOUT contacting the MCP.

Workflow (real run):
  1. Resolve the canonical enterprise name (fuzzy search if only a keyword).
  2. Query cloudmigration_cloud_assets (云资产概况) + cloudmigration_domain_info (备案域名明细).
  3. Build unified report JSON with domain sections (云资产概况 KV / 备案域名明细 表).

This file never prints secrets; MCP credentials live in the server's own .env.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
from typing import Any, Dict, List, Mapping, Optional, Sequence

from common import REPORT_BANNER, REPORT_TYPE, attach_pagination, call_tool_once, collect_detail_pages, die, json_dumps, load_json_file, paid_call_scope, print_json
import mcp_client
from semantic_review import prepare_draft
from render_report import render_html, render_markdown, html_to_pdf

from cloud_content_review import apply_content_review
from cloud_ratio import format_source_ratio, source_ratio_percent

SAMPLE_PATH = pathlib.Path(__file__).resolve().parent.parent / "assets" / "report.example.json"

# Cloudmigration MCP tools.
T_FUZZY = "cloudmigration_fuzzy_search"
T_CLOUD_ASSETS = "cloudmigration_cloud_assets"
T_DOMAIN_INFO = "cloudmigration_domain_info"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #




def _is_empty_signal(value: Any) -> bool:
    """Recognize documented no-data text without classifying it as an API failure."""
    if not isinstance(value, str):
        return False
    text = value.strip()
    return bool(text) and any(token in text for token in (
        "查询数据为空", "暂无数据", "未查询到", "未检索到", "查询结果为空",
    ))

def _is_api_error(value: Any) -> bool:
    """Recognize failures without treating a documented empty result as an error."""
    if value is None:
        return False
    if isinstance(value, str):
        text = value.strip()
        if any(s in text for s in ("查询数据为空", "暂无数据", "未查询到", "未检索到")):
            return False
        return any(s in text for s in (
            "接口调用失败", "查询失败", "Error executing tool", "validation error",
            "状态码：4", "状态码：5", "密钥错误", "签名错误", "未配置",
        ))
    if not isinstance(value, dict):
        return False
    if value.get("isError") is True or value.get("success") is False:
        return True
    if value.get("_error") or value.get("error") or value.get("error_message"):
        return True
    if "code" in value and value.get("code") not in (None, 0, 200, "0", "200", "SUCCESS", "success"):
        return True
    if set(value) == {"text"} and value.get("text"):
        return not any(s in str(value["text"]) for s in ("查询数据为空", "暂无数据", "未查询到", "未检索到"))
    return any(_is_api_error(v) for v in value.values() if isinstance(v, (dict, str)))


def _first_list(value: Any) -> List[Any]:
    if _is_api_error(value):
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        for key in ("resultList", "list", "items", "records", "data"):
            if isinstance(value.get(key), list):
                return value[key]
    return []


def _first_record(value: Any) -> Dict[str, Any]:
    for record in _first_list(value):
        if isinstance(record, dict) and _has_evidence(record):
            return record
    if isinstance(value, dict) and not _is_api_error(value) and _has_evidence(value):
        return value
    return {}


def _has_evidence(value: Any) -> bool:
    if value is None or value in ("", "-") or _is_empty_signal(value):
        return False
    if _is_api_error(value):
        return False
    if isinstance(value, dict):
        return any(_has_evidence(v) for k, v in value.items() if k not in {"sections", "_raw"})
    if isinstance(value, list):
        return any(_has_evidence(v) for v in value)
    return True


def _text(value: Any, limit: int = 0) -> str:
    if value is None or _is_empty_signal(value):
        return ""
    if isinstance(value, (dict, list)):
        t = json.dumps(value, ensure_ascii=False)
    else:
        t = str(value)
    t = " ".join(t.split())
    if limit and len(t) > limit:
        return t[: limit - 1].rstrip() + "…"
    return t


def _int(value: Any) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_call(tool: str, arguments: Dict[str, Any]) -> Any:
    try:
        result = call_tool_once(mcp_client.call_tool, tool, arguments)
        # Detect API error responses (405, etc.) and return error marker
        if _is_api_error(result):
            return {"_error": "API错误", "_raw": result}
        return result
    except Exception as exc:
        return {"_error": str(exc)}


def _safe_total(payload: Any) -> Any:
    if isinstance(payload, dict):
        if _is_api_error(payload):
            return None
        return payload.get("total")
    return None


def _bool01(value: Any) -> str:
    """0/1 flags to 否/是."""
    if value in (1, "1", True):
        return "是"
    if value in (0, "0", False):
        return "否"
    return _text(value) or "-"


# --------------------------------------------------------------------------- #
# Resolution
# --------------------------------------------------------------------------- #

def resolve_enterprise_name(raw: str) -> Dict[str, Any]:
    raw = (raw or "").strip()
    if not raw:
        return {"keyword": "", "enterprise": "", "resolved": False, "reason": "关键词为空"}
    if any(suffix in raw for suffix in ("公司", "集团", "有限", "院", "厂", "中心", "事务所", "合作社", "合伙")):
        return {"keyword": raw, "enterprise": raw, "resolved": True, "reason": "视为企业全称"}
    fuzzy = _safe_call(T_FUZZY, {"matchKeyword": raw, "pageSize": 1})
    record = _first_record(fuzzy)
    total = _int(_safe_total(fuzzy))
    name = str(record.get("name") or "").strip()
    if name and total == 1:
        return {"keyword": raw, "enterprise": name, "resolved": True, "reason": "模糊查询唯一候选补全", "fuzzy_total": total, "record": record}
    if name and total and total > 1:
        return {"keyword": raw, "enterprise": raw, "resolved": False, "reason": f"模糊查询返回 {total} 个候选，未静默采用首条", "fuzzy_total": total}
    return {"keyword": raw, "enterprise": raw, "resolved": False, "reason": "模糊查询未命中唯一企业全称，按原始关键词查询"}


# --------------------------------------------------------------------------- #
# Enterprise profile helpers (from fuzzy_search record)
# --------------------------------------------------------------------------- #

def _extract_profile(record: Dict[str, Any]) -> Dict[str, Any]:
    """Extract enterprise profile fields from a fuzzy_search record."""
    return {
        "name": _text(record.get("name")),
        "reg_capital": record.get("regCapitalValue"),
        "reg_capital_coin": _text(record.get("regCapitalCoinType")),
        "annual_turnover": _text(record.get("annualTurnover")),
        "oper_status": _text(record.get("operStatus")),
        "enterprise_type": _text(record.get("enterpriseType")),
        "found_time": _text(record.get("foundTime")),
        "legal_rep": _text(record.get("legalRepresentative")),
        "address": _text(record.get("address")),
        "homepage": _text(record.get("homepage")),
    }


def _format_capital(val: Any, coin: str = "") -> str:
    """Format capital value: 10995210218.0 -> '109.95 亿'."""
    try:
        v = float(val)
        if v >= 1e8:
            s = f"{v / 1e8:.2f} 亿"
        elif v >= 1e4:
            s = f"{v / 1e4:.2f} 万"
        else:
            s = f"{v:.0f}"
        if coin:
            s += f" {coin}"
        return s
    except (TypeError, ValueError):
        return _text(val) if val else "-"


def _enrich_metrics_with_profile(metrics: List[Dict[str, Any]], record: Any) -> List[Dict[str, Any]]:
    """Append enterprise profile metrics from a fuzzy_search record."""
    if not isinstance(record, dict):
        return metrics
    _prof = _extract_profile(record)
    if _prof.get("reg_capital") and _prof["reg_capital"] not in ("-", "", None):
        metrics.append({"label": "注册资本", "value": _format_capital(_prof["reg_capital"], _prof.get("reg_capital_coin", "")), "hint": "工商登记注册资本"})
    if _prof.get("found_time") and _prof["found_time"] != "-":
        metrics.append({"label": "成立时间", "value": _prof["found_time"], "hint": "工商登记成立日期"})
    if _prof.get("oper_status") and _prof["oper_status"] != "-":
        metrics.append({"label": "经营状态", "value": _prof["oper_status"], "hint": "工商登记经营状态"})
    if _prof.get("enterprise_type") and _prof["enterprise_type"] != "-":
        metrics.append({"label": "企业类型", "value": _prof["enterprise_type"], "hint": "工商登记企业类型"})
    if _prof.get("legal_rep") and _prof["legal_rep"] != "-":
        metrics.append({"label": "法定代表人", "value": _prof["legal_rep"], "hint": "工商登记法定代表人"})
    return metrics


def _derive_core_metrics(metrics: List[Dict[str, Any]], core: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Derive additional metrics from core analysis sections."""
    year_trend = core.get("domain_year_trend", []) if isinstance(core, dict) else []
    domains = core.get("domain_records", []) if isinstance(core, dict) else []
    if isinstance(year_trend, list) and year_trend:
        metrics.append({"label": "备案年份覆盖", "value": str(len(year_trend)), "hint": "有域名备案记录的年度数"})
        try:
            years = sorted([str(r.get("年份", "")) for r in year_trend if r.get("年份")], reverse=True)
            if years:
                metrics.append({"label": "最新备案年份", "value": years[0], "hint": "最近一次域名备案年份"})
        except Exception:
            pass
    if isinstance(domains, list) and domains:
        official = sum(1 for r in domains if "是" in str(r.get("是否官网", "")))
        if official:
            metrics.append({"label": "官网数", "value": str(official), "hint": "已标记为官网的域名数"})
    return metrics


# --------------------------------------------------------------------------- #
# Section builders
# --------------------------------------------------------------------------- #

def build_subject(raw: str, resolved: Mapping[str, Any], keyword_type: str) -> Dict[str, Any]:
    return {
        "enterprise": resolved.get("enterprise") or raw,
        "matchKeyword": resolved.get("enterprise") or raw,
        "keywordType": keyword_type,
        "match_raw": raw,
        "resolved": bool(resolved.get("resolved")),
        "resolve_reason": resolved.get("reason", ""),
        "fuzzy_total": resolved.get("fuzzy_total"),
        "requires_confirmation": bool((resolved.get("fuzzy_total") or 0) > 1),
    }


def build_caliber(subject: Mapping[str, Any]) -> Dict[str, Any]:
    total = subject.get("domain_total")
    returned = subject.get("domain_returned")
    pages = subject.get("domain_pages")
    size = subject.get("domain_page_size")
    page_note = ""
    if total is not None or returned is not None:
        page_note = f"备案域名上游总量 {total if total is not None else '未返回'}"
        if pages is not None:
            page_note += f"，遍历 {pages} 页"
        page_note += f"，归纳 {returned if returned is not None else 0} 条"
        if size is not None:
            page_note += f"（每页最多 {size} 条）"
    return {
        "match_target": subject.get("enterprise") or subject.get("match_raw"),
        "match_type": "云资产/备案域名按企业名称匹配；支持企业名称、统一社会信用代码、注册号和企业 ID",
        "data_scope": "企业云资产概况（域名/云厂商/云支出占比/云用量）、备案域名明细与年度趋势",
        "products": ["企业云资产", "备案域名信息"],
        "limit": "；".join(p for p in (
            "数据来自云上资产探测公开数据源，不同产品返回的域名总体不可直接相除",
            page_note,
            "字段可能存在探测覆盖与更新延迟",
        ) if p) + "。",
    }


def build_metrics(assets: Any, domain: Any) -> List[Dict[str, Any]]:
    metrics: List[Dict[str, Any]] = []
    a = assets if isinstance(assets, dict) else {}
    eff_domain = a.get("effectiveSubDomainNum")
    sub_domain = a.get("subDomainNum")
    cloud_consumption = a.get("cloudConsumptionScale")
    domain_total = _int(_safe_total(domain)) if isinstance(domain, dict) else None

    metrics.append({"label": "有效域名数", "value": (_text(eff_domain) if eff_domain is not None else "-"), "hint": "企业云上有效域名数量"})
    eff_n = _int(eff_domain)
    sub_n = _int(sub_domain)
    if eff_n and sub_n:
        metrics.append({"label": "子域名数", "value": (_text(sub_domain) if sub_domain is not None else "-"), "hint": "子域名数量", "delta": f"子域/有效 {sub_n / eff_n:.1f}"})
    else:
        metrics.append({"label": "子域名数", "value": (_text(sub_domain) if sub_domain is not None else "-"), "hint": "子域名数量"})
    metrics.append({"label": "上云资产等级", "value": (_text(cloud_consumption) or "-"), "hint": "云资产规模等级"})
    metrics.append({"label": "备案域名数", "value": (_text(domain_total) if domain_total is not None else "-"), "hint": "备案域名条数"})
    return [m for m in metrics if m.get("value") not in ("", None, "-")]


def _assets_kv(assets: Any) -> Dict[str, Any]:
    a = assets if isinstance(assets, dict) else {}
    kv: Dict[str, Any] = {}
    if a.get("effectiveSubDomainNum") is not None:
        kv["有效域名数量"] = _text(a.get("effectiveSubDomainNum"))
    if a.get("subDomainNum") is not None:
        kv["子域名数量"] = _text(a.get("subDomainNum"))
    if isinstance(a.get("effectiveSubDomainList"), list) and a["effectiveSubDomainList"]:
        kv["有效域名示例"] = "、".join(_text(t) for t in a["effectiveSubDomainList"][:10] if t)
    if isinstance(a.get("cloudServerList"), list) and a["cloudServerList"]:
        kv["云服务厂商"] = "、".join(_text(t) for t in a["cloudServerList"] if t)
    if a.get("cloudServerNumInterval"):
        kv["云用量范围"] = _text(a.get("cloudServerNumInterval"))
    if a.get("cloudConsumptionScale"):
        kv["上云资产等级"] = _text(a.get("cloudConsumptionScale"))
    # 真实云支出占比（cloudServiceProviderRatio: [{cloudService, ratio}]）
    if isinstance(a.get("cloudServiceProviderRatio"), list) and a["cloudServiceProviderRatio"]:
        spend_parts = []
        for item in a["cloudServiceProviderRatio"]:
            if isinstance(item, dict) and item.get("cloudService"):
                ratio = item.get("ratio")
                spend_parts.append(f"{_text(item.get('cloudService'))} {format_source_ratio(ratio)}")
        if spend_parts:
            kv["云支出占比"] = "、".join(spend_parts)
    # CDN 节点规模（cdnServerNum 是真实字段；上游无 hasCdn/cdnServerList，已移除避免渲染 “-”）
    if a.get("cdnServerNum") is not None:
        kv["CDN 节点规模"] = _text(a.get("cdnServerNum"))
    if a.get("hasOverseasCloudService") is not None:
        kv["海外服务器"] = _bool01(a.get("hasOverseasCloudService"))
    return kv


def _spend_rows(assets: Any) -> List[Dict[str, Any]]:
    """Real cloud-spend share from cloudServiceProviderRatio [{cloudService, ratio}].

    Replaces the previous fake 'vendor coverage' bar (which assigned count=1 to
    every vendor). ratio is a 0-1 fraction; we render it as a percentage.
    """
    a = assets if isinstance(assets, dict) else {}
    out: List[Dict[str, Any]] = []
    for item in (a.get("cloudServiceProviderRatio") or []):
        if not isinstance(item, dict) or not _has_evidence(item):
            continue
        vendor = _text(item.get("cloudService"))
        if not vendor:
            continue
        ratio = item.get("ratio")
        pct = source_ratio_percent(ratio)
        out.append({"云厂商": vendor, "支出占比": format_source_ratio(ratio),
                    "支出占比数值": float(pct) if pct is not None else 0.0})
    out.sort(key=lambda r: r["支出占比数值"], reverse=True)
    return out


def _vendor_rows(assets: Any) -> List[Dict[str, Any]]:
    """Multi-cloud breadth: each vendor present = 1 (kept for vendor-coverage view)."""
    a = assets if isinstance(assets, dict) else {}
    vendors = [str(t).strip() for t in (a.get("cloudServerList") or []) if str(t).strip()]
    out = []
    seen = set()
    for v in vendors:
        if v in seen:
            continue
        seen.add(v)
        out.append({"云厂商": v, "覆盖服务数": "1"})
    return out


def _capability_rows(assets: Any) -> List[Dict[str, Any]]:
    """Cloud-capability enabled pie.

    Only hasOverseasCloudService is a real flag in the upstream payload; the
    former hasCdn/hasIDC/hasCloudStorage fields do not exist and were removed
    to avoid rendering spurious “-” entries.
    """
    a = assets if isinstance(assets, dict) else {}
    enabled = 0
    disabled = 0
    for k in ("hasOverseasCloudService",):
        flag = a.get(k)
        if flag in (1, "1", True):
            enabled += 1
        elif flag in (0, "0", False):
            disabled += 1
    rows = []
    if enabled or disabled:
        rows.append({"能力状态": "已启用（海外服务器）", "数量": str(enabled)})
        rows.append({"能力状态": "未启用（海外服务器）", "数量": str(disabled)})
    return rows


def _domain_year_rows(domain: Any) -> List[Dict[str, Any]]:
    """Aggregate filingAuditTime by year -> 备案年度趋势."""
    year_counter: Dict[str, int] = {}
    for item in _first_list(domain):
        if not isinstance(item, dict) or not _has_evidence(item):
            continue
        t = _text(item.get("filingAuditTime"))
        if not t or len(t) < 4:
            continue
        year = t[:4]  # extract YYYY from '2019-12-26'
        if year.isdigit():
            year_counter[year] = year_counter.get(year, 0) + 1
    return [{"年份": y, "数量": n} for y, n in sorted(year_counter.items())]


def _domain_rows(domain: Any) -> List[Dict[str, Any]]:
    out = []
    for item in _first_list(domain):
        if not isinstance(item, dict) or not _has_evidence(item):
            continue
        out.append({
            "网址": _text(item.get("domainUrl")) or "-",
            "网站备案号": _text(item.get("websiteRecord")) or "-",
            "审核时间": _text(item.get("filingAuditTime")) or "-",
            "是否官网": _bool01(item.get("isHomePage")),
        })
    return out


def build_core_analysis(assets: Any, domain: Any) -> Dict[str, Any]:
    assets_kv = _assets_kv(assets)
    domain_rows = _domain_rows(domain)
    spend_rows = _spend_rows(assets)
    vendor_rows = _vendor_rows(assets)
    capability_rows = _capability_rows(assets)
    domain_year_rows = _domain_year_rows(domain)
    domain_total = _safe_total(domain) if isinstance(domain, dict) else None

    sections = [
        {"key": "cloud_assets_overview", "title": "云资产概况", "kind": "kv"},
        {"key": "spend_dist", "title": "云支出占比", "kind": "table",
         "note": "逐条保留上游百分数；各行未证明互斥，不求和、不重分配或归一化至 100%",
         "columns": [("云厂商", "云厂商"), ("支出占比", "支出占比")]},
        {"key": "vendor_dist", "title": "云服务厂商记录", "kind": "bar", "note": "上游返回的云服务厂商去重记录",
         "chart": {"name": "云厂商", "value": "覆盖服务数", "orient": "v"},
         "columns": [("云厂商", "云厂商"), ("覆盖服务数", "覆盖服务数")]},
        {"key": "domain_year_trend", "title": "备案年度趋势", "kind": "line", "note": "按备案审核年度统计新增域名数量",
         "chart": {"x": "年份", "y": "数量", "area": True},
         "columns": [("年份", "年份"), ("数量", "数量")]},
        {"key": "capability_dist", "title": "海外服务器字段", "kind": "pie", "note": "仅展示上游 hasOverseasCloudService 字段",
         "chart": {"name": "能力状态", "value": "数量", "donut": True},
         "columns": [("能力状态", "能力状态"), ("数量", "数量")]},
        {"key": "domain_records", "title": "备案域名明细", "kind": "table",
         "note": (f"上游总量 {domain_total} 条，本次归纳 {len(domain_rows)} 条"
                  if domain_total is not None else f"上游未返回总量，本次归纳 {len(domain_rows)} 条"),
         "columns": [("网址", "网址"), ("网站备案号", "网站备案号"), ("审核时间", "审核时间"), ("是否官网", "是否官网")]},
    ]
    return {
        "sections": sections,
        "cloud_assets_overview": assets_kv,
        "spend_dist": spend_rows,
        "vendor_dist": vendor_rows,
        "domain_year_trend": domain_year_rows,
        "capability_dist": capability_rows,
        "domain_records": domain_rows,
    }


def build_records(core: Mapping[str, Any]) -> List[Dict[str, Any]]:
    out = []
    for item in core.get("domain_records") or []:
        out.append({
            "网址": item.get("网址") or "-",
            "网站备案号": item.get("网站备案号") or "-",
            "是否官网": item.get("是否官网") or "-",
        })
    return out[:20]


def build_insights(subject: Mapping[str, Any], core: Mapping[str, Any], metrics: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """Describe returned observations only; do not infer maturity, security or compliance."""
    insights: List[Dict[str, Any]] = []
    metric_map = {m["label"]: str(m["value"]) for m in metrics}
    observed = [
        ("有效域名数", "有效域名观察"),
        ("子域名数", "子域名观察"),
        ("上云资产等级", "资产等级观察"),
        ("备案域名数", "备案域名总量观察"),
    ]
    for label, feature in observed:
        if label in metric_map:
            insights.append({
                "feature": feature,
                "evidence": f"上游返回{label}为 {metric_map[label]}。",
                "interpretation": "该值仅按上游字段展示，不能单独推断技术架构、业务规模、安全风险或监管状态。",
            })
    vendor_rows = core.get("vendor_dist") or []
    if vendor_rows:
        names = "、".join(_text(r.get("云厂商")) for r in vendor_rows if r.get("云厂商"))
        insights.append({
            "feature": "云服务厂商记录",
            "evidence": f"上游返回 {len(vendor_rows)} 个去重厂商记录：{names}。",
            "interpretation": "厂商记录数量不代表容灾能力、议价能力或运维复杂度。",
        })
    spend_rows = core.get("spend_dist") or []
    if spend_rows:
        evidence = "、".join(f"{r.get('云厂商')} {r.get('支出占比')}" for r in spend_rows)
        insights.append({
            "feature": "云支出占比记录",
            "evidence": f"上游返回：{evidence}。",
            "interpretation": "占比仅描述该字段口径，不推断厂商依赖、锁定风险或议价能力。",
        })
    cap_rows = core.get("capability_dist") or []
    if cap_rows:
        evidence = "、".join(f"{r.get('能力状态')} {r.get('数量')}" for r in cap_rows)
        insights.append({
            "feature": "海外服务器字段观察",
            "evidence": evidence + "。",
            "interpretation": "该布尔字段不证明海外用户、跨境业务或服务能力。",
        })
    year_rows = core.get("domain_year_trend") or []
    if year_rows:
        evidence = "、".join(f"{r.get('年份')}年 {r.get('数量')} 条" for r in year_rows)
        insights.append({
            "feature": "备案年度记录",
            "evidence": evidence + "。",
            "interpretation": "年度数量仅来自当前返回记录，不推断网站上线、扩张或存量运营阶段。",
        })
    if not insights:
        insights.append({
            "feature": "数据完整性",
            "evidence": "未返回可用于业务观察的云资产或备案域名字段。",
            "interpretation": "不得将缺失解释为资产为零、未使用云服务或不存在备案。",
        })
    return insights

def build_abstract(subject: Mapping[str, Any], core: Mapping[str, Any], metrics: Sequence[Mapping[str, Any]]) -> str:
    name = subject.get("enterprise") or subject.get("match_raw") or "目标企业"
    if subject.get("requires_confirmation"):
        return f"原始关键词“{subject.get('match_raw') or name}”返回多个候选主体，待人工确认；本报告未调用云资产详情，也不形成主体云资产结论。"
    if not metrics and not any(_has_evidence(v) for k, v in core.items() if k != "sections"):
        return f"本次未获得“{name}”的可用云资产或备案域名证据，核心维度覆盖率为 0；不得据此判断资产规模或备案情况。"
    parts = [f"本报告以“{name}”为分析对象，基于云上资产大数据，系统呈现企业云资产概况（域名/CDN/IDC/云厂商/云用量）与备案域名明细。"]
    if metrics:
        kv = "、".join(f"{m['label']} {m['value']}" for m in metrics[:5])
        parts.append(f"关键指标包括：{kv}。")
    parts.append("报告仅对上游返回的云资产字段、备案域名总量与已获取样本作结构化展示，不作技术实践、安全或监管判断。")
    return "".join(parts)


# --------------------------------------------------------------------------- #
# Dry-run sample
# --------------------------------------------------------------------------- #

def build_dry_run_payload(raw: str, keyword_type: str) -> Dict[str, Any]:
    try:
        sample = load_json_file(SAMPLE_PATH)
    except Exception:
        sample = {}
    sample = sample if isinstance(sample, dict) else {}
    subject = sample.get("subject") or {"enterprise": raw, "matchKeyword": raw, "keywordType": keyword_type, "match_raw": raw}
    subject = {**subject, "match_raw": raw, "keywordType": keyword_type}
    core = sample.get("core_analysis") or {}
    metrics = sample.get("metrics") or []
    return _assemble(subject, core, metrics, dry_run=True)


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #

def _assemble(subject: Mapping[str, Any], core: Mapping[str, Any], metrics: Sequence[Mapping[str, Any]], *, dry_run: bool) -> Dict[str, Any]:
    abstract = build_abstract(subject, core, metrics)
    records = build_records(core)
    insights = build_insights(subject, core, metrics)
    # Quality gate: count populated core-analysis sections.
    ca = core if isinstance(core, dict) else {}
    secs = ca.get("sections", [])
    if secs:
        total_secs = len(secs)
        populated = sum(1 for s in secs if isinstance(s, dict) and _has_evidence(ca.get(s.get("key"))))
    else:
        total_secs = max(1, len([k for k in ca if k != "sections"]))
        populated = sum(1 for k in ca if k != "sections" and _has_evidence(ca.get(k)))
    quality_report = {
        "total_sections": total_secs,
        "populated_sections": populated,
        "empty_sections": total_secs - populated,
        "coverage_pct": round(populated / max(1, total_secs) * 100),
    }
    if populated == 0:
        import sys
        print("⚠️ 质量门禁警告: 所有核心分析维度均无数据", file=sys.stderr)
    title = f"{subject.get('enterprise') or '目标企业'} 上云大数据报告"
    report = {
        "report_type": REPORT_TYPE,
        "title": title,
        "banner": REPORT_BANNER,
        "subject": dict(subject),
        "abstract": abstract,
        "summary": abstract,
        "executive_summary": [item["interpretation"] for item in insights][:5] or [abstract[:120]],
        "metrics": list(metrics),
        "caliber": build_caliber(subject),
        "core_analysis": dict(core),
        "representative_records": records,
        "insights": insights,
        "data_source": {
            "mcp_server": "cloudmigration-mcp-server",
            "products": [
                {"name": "企业云资产", "product_id": "6704f43fa9a1ec205f429e05"},
                {"name": "备案域名信息", "product_id": "66a0f258ce3408eb23b56706"},
            ],
            "generated_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "dry_run": dry_run,
            "quality_report": quality_report,
        },
    }
    return apply_content_review(report)


@paid_call_scope
def build_payload(raw: str, keyword_type: str, page_size: int, max_pages: int = 1) -> Dict[str, Any]:
    if isinstance(max_pages, bool) or not isinstance(max_pages, int) or max_pages < 1:
        raise ValueError("max_pages 必须为正整数")
    resolved = resolve_enterprise_name(raw)
    if (resolved.get("fuzzy_total") or 0) > 1:
        subject = build_subject(raw, resolved, keyword_type)
        core = build_core_analysis({}, {})
        return _assemble(subject, core, [], dry_run=False)
    enterprise = resolved["enterprise"]
    mk_args: Dict[str, Any] = {"matchKeyword": enterprise, "keywordType": keyword_type}
    assets = _safe_call(T_CLOUD_ASSETS, mk_args)
    domain = collect_detail_pages(
        _safe_call, T_DOMAIN_INFO,
        {"matchKeyword": enterprise, "keywordType": keyword_type, "pageSize": page_size},
        get_rows=_first_list, get_total=_safe_total, is_error=_is_api_error,
        max_pages=max_pages,
    )

    subject = build_subject(raw, resolved, keyword_type)
    pinfo = domain.get("_pagination") or {}
    subject.update({
        "domain_total": _safe_total(domain),
        "domain_returned": len(_domain_rows(domain)),
        "domain_pages": pinfo.get("pages_fetched"),
        "domain_page_size": page_size,
    })
    core = build_core_analysis(assets, domain)
    metrics = build_metrics(assets, domain)
    _derive_core_metrics(metrics, core if isinstance(core, dict) else {})
    # --- Enterprise profile enrichment (from fuzzy_search) ---
    _enrich_metrics_with_profile(metrics, resolved.get("record") if isinstance(resolved, dict) else None)
    report = _assemble(subject, core, metrics, dry_run=False)
    return attach_pagination(report, {"备案域名": domain})


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main() -> None:
    parser = argparse.ArgumentParser(description="Compose a cloud-migration big-data report via the cloudmigration MCP.")
    parser.add_argument("--enterprise", required=True, help="企业全称或关键词（关键词将自动模糊补全）")
    parser.add_argument("--keyword-type", default="name", help="主体类型：name/nameId/regNumber/socialCreditCode")
    parser.add_argument("--page-size", type=int, default=10, help="备案域名明细分页大小（最多 50）")
    parser.add_argument("--max-pages", type=int, default=1, help="备案域名明细最多付费翻页数（默认 1；仅在明确需要更多结论/证据时增大）")
    parser.add_argument("--dry-run", action="store_true", help="不调用真实 MCP，使用样例数据组装报告骨架")
    parser.add_argument("--output", help="输出 JSON 路径；省略则打印到 stdout")
    parser.add_argument("--report-output", help="同时输出 HTML 报告（.html）与 Markdown 报告（.md）")
    parser.add_argument("--pdf-output", help="额外输出 PDF 报告（.pdf）；需要 Playwright + Chromium")
    args = parser.parse_args()

    if not args.dry_run:
        if args.max_pages is not None and args.max_pages < 1:
            die("--max-pages 必须为正整数")

    if args.dry_run:
        payload = build_dry_run_payload(args.enterprise, args.keyword_type)
    else:
        payload = build_payload(args.enterprise, args.keyword_type, args.page_size, args.max_pages)

    payload = prepare_draft(payload)

    if args.output:
        out = pathlib.Path(args.output).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json_dumps(payload, pretty=True), encoding="utf-8")
        print_json({"ok": True, "json": str(out), "dry_run": args.dry_run})
    else:
        print_json(payload)

    if args.report_output:
        base_out = pathlib.Path(args.report_output).expanduser()
        base_out.parent.mkdir(parents=True, exist_ok=True)
        html_path = base_out.with_suffix(".html") if base_out.suffix.lower() not in (".html", ".htm") else base_out
        md_path = html_path.with_suffix(".md")
        html_path.write_text(render_html(payload), encoding="utf-8")
        md_path.write_text(render_markdown(payload), encoding="utf-8")
        if args.pdf_output:
            pdf_path = pathlib.Path(args.pdf_output).expanduser()
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            html_to_pdf(render_html(payload), str(pdf_path))
        print_json({"ok": True, "html": str(html_path), "markdown": str(md_path), "pdf": str(pdf_path) if args.pdf_output else None, "dry_run": args.dry_run})


if __name__ == "__main__":
    main()
