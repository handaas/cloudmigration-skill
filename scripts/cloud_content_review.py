#!/usr/bin/env python3
"""Offline content review for an existing cloudmigration report.

Pure, side-effect-free ``apply_content_review(report)`` normalizes labels that
the upstream returns verbatim (vendor aliases, aggregate buckets, internal
parameter names) without adding facts. It never calls the MCP. Use the CLI to
rewrite a frozen ``report.json`` into a reviewed copy and re-render HTML/MD.
"""
from __future__ import annotations

import argparse
import copy
import json
import pathlib
import re
from typing import Any, Dict, Iterable, List, Mapping, Tuple

from cloud_ratio import format_source_ratio, source_ratio_percent

# Upstream labels that are buckets, not vendors.
_AGGREGATE = {"海外", "其他", "其它", "other", "unknown", "未识别"}
# Same-vendor spellings observed in upstream payloads. Keys are casefolded.
_ALIASES = {
    "aws": "AWS",
    "amazon": "AWS",
    "amazon web services": "AWS",
    "amazonaws": "AWS",
    "akamai": "Akamai",
    "google": "Google Cloud",
    "google cloud": "Google Cloud",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "阿里云": "阿里云",
    "aliyun": "阿里云",
    "alibaba cloud": "阿里云",
    "腾讯云": "腾讯云",
    "tencent cloud": "腾讯云",
    "华为": "华为",
    "华为云": "华为",
    "huawei cloud": "华为",
    "cloudflare": "Cloudflare",
    "金山云": "金山云",
    "kingsoft cloud": "金山云",
    "七牛": "七牛",
    "qiniu": "七牛",
    "又拍云": "又拍云",
    "upyun": "又拍云",
    "网宿": "网宿",
    "wangsu": "网宿",
    "天翼云": "天翼云",
    "电信": "中国电信",
    "联通": "中国联通",
    "移动": "中国移动",
    "广电": "中国广电",
    "世纪互联": "世纪互联",
}
_KEYWORD_LABELS = {
    "name": "企业名称",
    "nameid": "企业 ID",
    "regnumber": "注册号",
    "socialcreditcode": "统一社会信用代码",
}


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _strip_parens(text: Any) -> str:
    return re.sub(r"（[^）]*）", "", _text(text))


def _split(value: Any) -> List[str]:
    if isinstance(value, (list, tuple)):
        return [_text(v) for v in value if _text(v)]
    text = _text(value)
    if not text or text in {"-", "—"}:
        return []
    return [p.strip() for p in re.split(r"[、,，;；]", text) if p.strip() and p.strip() not in {"-", "—"}]


def _clean_raw(raw: str) -> str:
    text = _text(raw)
    text = re.sub(r"（原值：[^）]*）", "", text)
    text = re.sub(r"（上游未具名归类）", "", text)
    return text.strip()


def _canonical(raw: str) -> Tuple[str, bool]:
    name = _clean_raw(raw)
    key = name.casefold()
    if key in _AGGREGATE:
        return f"{name}（上游未具名归类）", False
    return _ALIASES.get(key, name), True


def _keyword_label(value: Any) -> str:
    text = _text(value) or "name"
    return _KEYWORD_LABELS.get(text.casefold(), text)


def _fix_caliber(report: Dict[str, Any]) -> None:
    subject = report.get("subject") if isinstance(report.get("subject"), dict) else {}
    label = _keyword_label(subject.get("keywordType"))
    caliber = report.get("caliber")
    if isinstance(caliber, dict):
        caliber["match_type"] = f"云资产/备案域名按{label}匹配；支持企业名称、统一社会信用代码、注册号和企业 ID"
        # Drop internal parameter spellings if a provider left them in prose.
        for key, value in list(caliber.items()):
            if isinstance(value, str):
                caliber[key] = re.sub(r"[（(]?keywordType\s*=\s*[A-Za-z_]+[）)]?", "", value).strip()


def _normalize_vendors(report: Dict[str, Any]) -> None:
    core = report.get("core_analysis")
    if not isinstance(core, dict):
        return
    kv = core.get("cloud_assets_overview")
    if not isinstance(kv, dict):
        return

    raw_vendors: List[str] = []
    vendor_source: List[str] = []
    for row in core.get("vendor_dist") or []:
        if isinstance(row, dict):
            if row.get("原始标签") is not None:
                vendor_source.extend(_split(row.get("原始标签")))
            else:
                vendor_source.append(row.get("云厂商"))
    spend_source: List[str] = []
    for row in core.get("spend_dist") or []:
        if isinstance(row, dict):
            if row.get("原始标签") is not None:
                spend_source.extend(_split(row.get("原始标签")))
            else:
                spend_source.extend(_split(row.get("云厂商")))
    sources = vendor_source + spend_source
    if not sources:
        sources = _split(_strip_parens(kv.get("云服务厂商")))
    for name in sources:
        name = _clean_raw(name)
        if name and name not in raw_vendors:
            raw_vendors.append(name)

    variants: Dict[str, List[str]] = {}
    order: List[str] = []
    for raw in raw_vendors:
        canonical, named = _canonical(raw)
        if not named:
            canonical = canonical.split("（", 1)[0] + "（上游未具名归类）"
        if canonical not in variants:
            variants[canonical] = []
            order.append(canonical)
        if raw not in variants[canonical]:
            variants[canonical].append(raw)

    def display(canonical: str) -> str:
        raws = variants.get(canonical, [])
        if canonical.endswith("（上游未具名归类）") or not raws or raws == [canonical]:
            return canonical
        return f"{canonical}（原值：{'、'.join(raws)}）"

    def display_for(canonical: str, raw: str) -> str:
        if canonical.endswith("（上游未具名归类）") or raw == canonical:
            return canonical
        return f"{canonical}（原值：{raw}）"

    named = [name for name in order if not name.endswith("（上游未具名归类）")]
    aggregates = [name for name in order if name.endswith("（上游未具名归类）")]
    if named:
        kv["云服务厂商"] = "、".join(display(n) for n in named)
    else:
        kv.pop("云服务厂商", None)
    if aggregates:
        kv["上游未具名归类"] = "、".join(display(n) for n in aggregates)

    # Vendor labels: canonical display names with their original spellings.
    vendor_rows: List[Dict[str, Any]] = []
    for canonical in named:
        raws = variants[canonical]
        vendor_rows.append({
            "云厂商": display(canonical),
            "原始标签": "、".join(raws),
        })
    core["vendor_dist"] = vendor_rows

    # Spend rows: retain every upstream row and its ratio; only labels are
    # canonicalized. Alias spelling alone does not prove non-overlapping shares,
    # so rows are never summed, merged, or dropped.
    raw_spend = [r for r in (core.get("spend_dist") or []) if isinstance(r, dict)]
    spend_rows: List[Dict[str, Any]] = []
    for row in raw_spend:
        raw = _clean_raw(row.get("原始标签") or row.get("云厂商"))
        if not raw:
            continue
        canonical, _ = _canonical(raw)
        if canonical.endswith("（上游未具名归类）"):
            canonical = canonical.split("（", 1)[0] + "（上游未具名归类）"
        ratio = row.get("支出占比")
        if ratio in (None, ""):
            ratio = row.get("支出占比数值")
        # Both report fields are percentage points, including legacy numerics.
        # Their unit comes from the schema, never from the observed magnitude.
        display_ratio = format_source_ratio(ratio, already_percent=True)
        sort_value = source_ratio_percent(ratio, already_percent=True)
        spend_rows.append({
            "云厂商": display_for(canonical, raw),
            "支出占比": display_ratio,
            "支出占比数值": float(sort_value) if sort_value is not None else 0.0,
            "原始标签": raw,
        })
    core["spend_dist"] = spend_rows
    if spend_rows:
        kv["云支出占比"] = "、".join(f"{r['云厂商']} {r['支出占比']}" for r in spend_rows)

    if isinstance(core.get("sections"), list):
        for section in core["sections"]:
            if not isinstance(section, dict):
                continue
            if section.get("key") == "spend_dist":
                section["kind"] = "table"
                section.pop("chart", None)
                section["columns"] = [("云厂商", "云厂商"), ("支出占比", "支出占比")]
                section["note"] = "按上游百分数逐条展示；仅规范化厂商显示名，各行未证明互斥，不合并、不求和、不删除记录，也不归一化至 100%；显式百分比原样保留"
            elif section.get("key") == "vendor_dist":
                section["title"] = "云服务厂商标签"
                section["kind"] = "table"
                section["note"] = "上游厂商标签仅做显示名规范化，保留原始写法；别名写法数量不是业务记录数，不作数量排名。海外/其他为上游未具名归类，不计入厂商数"
                section.pop("chart", None)
                section["columns"] = [("云厂商", "云厂商"), ("原始标签", "原始标签")]
            elif section.get("key") == "capability_dist":
                section["note"] = "仅展示上游返回的海外服务器标识（是/否），不代表跨境业务能力"


def _fix_metrics(report: Dict[str, Any]) -> None:
    metrics = report.get("metrics")
    if not isinstance(metrics, list):
        return
    out: List[Dict[str, Any]] = []
    for metric in metrics:
        if not isinstance(metric, dict):
            continue
        if metric.get("label") == "子域名数":
            metric.pop("delta", None)
        out.append(metric)
    report["metrics"] = out


def _rebuild_insights(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    core = report.get("core_analysis") if isinstance(report.get("core_analysis"), dict) else {}
    metrics = {m.get("label"): _text(m.get("value")) for m in (report.get("metrics") or []) if isinstance(m, dict)}
    insights: List[Dict[str, Any]] = []
    for label, feature in (("有效域名数", "有效域名观察"), ("子域名数", "子域名观察"),
                           ("上云资产等级", "资产等级观察"), ("备案域名数", "备案域名总量观察")):
        if label in metrics:
            insights.append({
                "feature": feature,
                "evidence": f"上游返回{label}为 {metrics[label]}。",
                "interpretation": "该值仅按上游字段展示，不能单独推断技术架构、业务规模、安全风险或监管状态。",
            })

    vendors = [r for r in (core.get("vendor_dist") or []) if isinstance(r, dict) and r.get("云厂商")]
    if vendors:
        evidence = "、".join(str(r["云厂商"]) for r in vendors)
        aggregates = _text((core.get("cloud_assets_overview") or {}).get("上游未具名归类"))
        if aggregates:
            evidence += f"；另有上游未具名归类：{aggregates}"
        insights.append({
            "feature": "云服务厂商标签",
            "evidence": f"合并同一厂商的不同写法后，具名厂商 {len(vendors)} 个：{evidence}。",
            "interpretation": "厂商记录数量不代表容灾能力、议价能力或运维复杂度；上游未具名归类不能计入具体厂商。",
        })

    spend = [r for r in (core.get("spend_dist") or []) if isinstance(r, dict) and r.get("云厂商")]
    if spend:
        insights.append({
            "feature": "云支出占比记录",
            "evidence": "上游返回：" + "、".join(f"{r['云厂商']} {r.get('支出占比')}" for r in spend) + "。",
            "interpretation": "占比仅描述该字段口径，不推断厂商依赖、锁定风险或议价能力；厂商显示名仅做别名规范化，各条占比记录逐条保留，不合并、不求和、不重算。",
        })

    kv = core.get("cloud_assets_overview") if isinstance(core.get("cloud_assets_overview"), dict) else {}
    if kv.get("海外服务器") not in (None, "", "-"):
        insights.append({
            "feature": "海外服务器标识",
            "evidence": f"上游返回海外服务器标识为“{kv['海外服务器']}”。",
            "interpretation": "该布尔字段不证明海外用户、跨境业务或服务能力。",
        })

    years = [r for r in (core.get("domain_year_trend") or []) if isinstance(r, dict)]
    if years:
        subject = report.get("subject") if isinstance(report.get("subject"), dict) else {}
        returned = subject.get("domain_returned")
        total = subject.get("domain_total")
        scope = ""
        if returned is not None:
            scope = f"当前返回 {returned} 条"
            if total is not None and _text(total) != _text(returned):
                scope += f"（上游总量 {total}）"
            scope += "中："
        insights.append({
            "feature": "备案年度记录",
            "evidence": scope + "、".join(f"{r.get('年份')}年 {r.get('数量')} 条" for r in years) + "。",
            "interpretation": "年度数量仅来自当前返回记录，不推断网站上线、扩张或存量运营阶段。",
        })
    if not insights:
        insights.append({
            "feature": "数据完整性",
            "evidence": "未返回可用于业务观察的云资产或备案域名字段。",
            "interpretation": "不得将缺失解释为资产为零、未使用云服务或不存在备案。",
        })
    return insights


def _dedupe(items: Iterable[Any]) -> List[Any]:
    out: List[Any] = []
    seen = set()
    for item in items:
        key = json.dumps(item, ensure_ascii=False, sort_keys=True) if isinstance(item, (dict, list)) else _text(item)
        if key and key not in seen:
            seen.add(key)
            out.append(item)
    return out


def _has_review_body(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, (str, list, dict, tuple)) and len(value) == 0:
        return False
    return True


def _refresh_quality_report(report: Dict[str, Any]) -> None:
    """Recompute section-fill stats from the final sections and bodies.

    0 counts as populated; only None and empty containers/strings are empty.
    coverage_pct is section fill rate, never an accuracy claim.
    """
    core = report.get("core_analysis") if isinstance(report.get("core_analysis"), dict) else {}
    sections = core.get("sections") if isinstance(core.get("sections"), list) else []
    total = len([s for s in sections if isinstance(s, dict)])
    populated = 0
    for section in sections:
        if not isinstance(section, dict):
            continue
        key = section.get("key")
        if key and _has_review_body(core.get(key)):
            populated += 1
    data_source = report.get("data_source")
    if not isinstance(data_source, dict):
        data_source = {}
        report["data_source"] = data_source
    quality = data_source.get("quality_report")
    if not isinstance(quality, dict):
        quality = {}
        data_source["quality_report"] = quality
    quality.update({
        "total_sections": total,
        "populated_sections": populated,
        "empty_sections": total - populated,
        "coverage_pct": round(populated / total * 100) if total else 0,
    })


def apply_content_review(report: Mapping[str, Any]) -> Dict[str, Any]:
    """Return a reviewed deep copy of a frozen cloudmigration report."""
    reviewed = copy.deepcopy(dict(report))
    _fix_caliber(reviewed)
    _normalize_vendors(reviewed)
    _fix_metrics(reviewed)
    insights = _rebuild_insights(reviewed)
    reviewed["insights"] = insights
    reviewed["executive_summary"] = _dedupe(i.get("interpretation") for i in insights)[:5] or [reviewed.get("abstract", "")]
    if isinstance(reviewed.get("caliber"), dict):
        reviewed["caliber"]["match_type"] = reviewed["caliber"].get("match_type", "")
    _refresh_quality_report(reviewed)
    return reviewed


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply offline content review to a cloudmigration report.json")
    parser.add_argument("--input", required=True, help="frozen report.json")
    parser.add_argument("--out-dir", required=True, help="output directory for report.json/md/html")
    args = parser.parse_args()
    input_path = pathlib.Path(args.input).expanduser().resolve()
    output_path = pathlib.Path(args.out_dir).expanduser()
    target = (output_path / "report.json").resolve()
    same = target == input_path
    if not same and target.exists():
        try:
            same = target.samefile(input_path)
        except OSError:
            same = False
    if same:
        raise SystemExit("拒绝写入：--out-dir 的 report.json 指向 --input，冻结源报告不可覆盖")
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from render_report import render_html, render_markdown

    source = json.loads(pathlib.Path(args.input).read_text(encoding="utf-8"))
    reviewed = apply_content_review(source)
    out = pathlib.Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(json.dumps(reviewed, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "report.md").write_text(render_markdown(reviewed), encoding="utf-8")
    (out / "report.html").write_text(render_html(reviewed), encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
