---
name: cloudmigration-report
description: Use for generating a professional cloud-migration (上云) big-data report (上云大数据报告) from the HandaaS cloudmigration MCP — covering 企业云资产概况（域名/CDN/IDC/云厂商/云用量）与备案域名明细. Trigger when users ask for “上云大数据报告”, “云资产分析”, “查一家公司的云资产”, “上云情况分析”, “备案域名查询”, “企业上云画像”, or “云基础设施画像”. Infer the canonical enterprise name (auto-fuzzy-completing a keyword), pick the right MCP tools, and produce HTML + Markdown + JSON reports automatically. MCP 服务名称触发词：上云资产分布。
---

# 上云大数据报告

## 用户契约

把“上云大数据报告”作为面向用户的调用短语。`cloudmigration-report` 仅为内部包名。

当本 skill 处于激活状态：

1. 不要向用户索要 product_id、MCP 工具名、API 字段、内部参数或凭证信息；只接受企业名称、统一社会信用代码、注册号或企业 ID。
2. 接受自然目标，例如“查一下某某公司的云资产”“分析这家企业的上云情况”“给我一份某某公司的上云报告”“看看这家企业用了哪些云厂商”。
3. 当用户只给关键词时，自动调用关键词模糊查询补全企业全称，再查云资产/备案域名详情。
4. 优先使用 MCP 连接（`CLOUDMIGRATION_MCP_URL` Remote MCP 或本地 `handaas-mcp-server/cloudmigration-mcp-server`）；不要让用户处理签名或凭证。
5. 同时产出 HTML（可分享交付）、Markdown（知识库 / wiki）、JSON（系统集成）三类产物。
6. 报告正文必须是专业研究报告风格：只见云资产事实与结构化数据，绝不出现工具名、入参、product_id、内部字段或空表。
7. 绝不打印 `secret_id`、`secret_key`、签名、token 或原始签名请求。
8. 默认 dry-run；真实付费 / 凭证调用需用户明确要求且 MCP 连接配置完整。
9. 数据为空时明确说明数据范围 / 口径，不渲染空表、不臆造事实。


- MCP 返回的嵌套 JSON 字符串（如金额 `{"coinType":"人民币","value":430000000.0}`、地址 `{"city":"杭州市",...}`）必须解析为可读文本（如"4.30 亿 人民币"、"浙江省杭州市"），绝不在报告正文、表格或指标中输出原始 JSON 字符串。
- 报告所有章节标题、指标卡标签必须用中文；`core_analysis.sections` 的 `title` 字段必须中文，不可显示英文 key（如 `holders`、`investments`）。
- 指标值必须可读化：金额格式为"X 亿/万 + 币种"，地址拼接省市区，比率显示百分号。详见 `references/report-output.md` 的「数据格式约束」。

## MCP 服务入口

- MCP 服务当前名称：上云资产分布（连接仍使用原服务目录标识）。

- 上游 MCP 项目：`handaas-mcp-server/cloudmigration-mcp-server`（“上云大数据”）。
- Remote MCP：设置环境变量 `CLOUDMIGRATION_MCP_URL`（streamable-http），可选 `CLOUDMIGRATION_MCP_TOKEN`。
- 本地 MCP：设置 `HANDAAS_MCP_SERVER_ROOT` 指向 `handaas-mcp-server` 仓库根目录；该 server 自己的 `.env` 提供 `INTEGRATOR_ID` / `SECRET_ID` / `SECRET_KEY`。
- 首次真实查询前，运行 `scripts/mcp_client.py ping` 与 `scripts/mcp_client.py list-tools` 验证连通。

## 按需加载 references

- 不清楚该 MCP 有哪些工具、参数、返回字段、何时调用：`references/mcp-tools-reference.md`。
- 报告结构、章节、质量底线、渲染工作流：`references/report-output.md`。

## 付费调用与预算约束（必读）

1. 每次业务工具调用与每次明细翻页都可能计费；想要 total/页数只是为了精确规划，不构成默认全量拉取的授权。
2. 调用前先推演所需结论与数据维度，确定工具/参数计划、必要页数与最大调用预算。total 未知时，第一个必要明细页既是数据又是 total 探测，绝不为此重复付费。
3. 优先用统计/画像/聚合接口回答问题；只在结论、图表、代表记录或明确全量/计数需求确实需要时取明细。只有确实要求综合报告时才跑完整流水线，绝不因为工具存在就全部调用。
4. 用 schema 允许的最大合理 pageSize 取所需行数，证据/样本目标满足即停，且不超过明确预算。更多调用必须有具体缺失结论支撑，不因为"补齐所有章节"而追加；不得用样本分布冒充全量结论。预算不足以支撑关键结论时，先说明证据缺口与预计额外调用数，等明确授权后再扩大——不得静默降级结论，也不得静默扩大计费范围。
5. 当前任务/报告内复用相同请求（含第一页规划数据）：同一 tool+相同参数只调用一次；不要为渲染重跑 compose/MCP——用已保存 JSON 本地重渲染；不得自动重试、重复取统计/明细或并行获取相同数据；补充查询先列明缺口并复用已返回记录。
6. `total_pages`/`remaining_pages` 是按请求 pageSize 的估算；短但非空的页仍有剩余记录时在预算内继续。只有稳定有效 total 与实际扫描数一致才算完整采集；报错、提前空页、重复页、total 变更/缺失、数量溢出均为不完整。显式预算或样本目标停止即部分采集，绝不宣称全量。不调用无关或不必要维度的工具。

本 skill 分页明细接口：`cloudmigration_domain_info`（备案域名，pageSize≤50），预算经 `--max-pages`（默认 1）传递；`cloudmigration_cloud_assets` 与模糊补全 `cloudmigration_fuzzy_search` 为单次调用，不进入分页预算。

## 意图路由

| 用户意图 | 内部工作流 |
| --- | --- |
| 查一家公司的全维度上云报告 | 调云资产 + 备案域名组装全量报告；`compose_report.py --enterprise ...` |
| 只要云资产概况 / 备案域名 | 仅调对应工具，按统一骨架组装 |
| 只要云厂商 / CDN / IDC / 云用量分布 | 用 `cloudmigration_cloud_assets` 输出 KV 概况 |
| 只给关键词（不是全称） | 先 `cloudmigration_fuzzy_search` 补全全称，再查详情 |
| 只要 JSON / 只要 HTML / 只要 Markdown | 用 `--output`（JSON）或 `--report-output`（HTML+MD），或 `render_report.py` 重渲染 |
| 连接 / 工具不存在 / 传参错误 | `mcp_client.py ping` / `list-tools` 排查；报脱敏后的缺失项 |

## Golden path for 上云大数据报告

1. **解析企业全称**：若输入含“公司/集团/有限/院/厂/中心/事务所/合作社/合伙”等后缀视为全称；否则调 `cloudmigration_fuzzy_search` 取首个命中。
2. **调用云工具**：`cloudmigration_cloud_assets`（云资产概况：域名/CDN/IDC/云厂商/云用量/上云等级）、`cloudmigration_domain_info`（备案域名明细）。入参为 `matchKeyword`（企业全称）+ `keywordType`。
3. **组装统一报告**：核心分析含云资产概况（KV）、备案域名明细（表）。
4. **渲染三件套**：`compose_report.py --enterprise ... --output ... --report-output ...` 直接产出 JSON + HTML + Markdown；或 `render_report.py --input ... --output ...` 重渲染。
5. **返回路径**：返回 JSON、HTML、Markdown 文件路径，以及企业全称映射与数据口径。

- **渲染前置检查**：执行会产出含图表 HTML / PDF 的报告命令前，先验证 `node --version` 与本 skill 自带 `assets/vendor/echarts.min.js` 存在；内嵌静态 SVG 的生成需要 Node.js（推荐当前 LTS，无需 npm 包），缺失时报告生成明确报错。查看已生成的 HTML 与 Markdown 输出不需要 Node。

## 脚本速查

```bash
# 校验连接配置（脱敏）
python scripts/validate_config.py --allow-placeholders

# 连通性自测
python scripts/mcp_client.py ping
python scripts/mcp_client.py list-tools

# 干跑（不调真实 API，用样例数据组装报告骨架）
python scripts/compose_report.py \
  --enterprise "示例科技有限公司" \
  --dry-run \
  --output output/cloudmigration.json \
  --report-output output/cloudmigration.html

# 真实查询 + 渲染（需 MCP 连接就绪）
python scripts/compose_report.py \
  --enterprise "示例科技有限公司" \
  --max-pages 1 \
  --output output/cloudmigration.json \
  --report-output output/cloudmigration.html

# 手动调单个工具
python scripts/mcp_client.py call-tool \
  --tool cloudmigration_cloud_assets \
  --arguments-json '{"matchKeyword": "示例科技有限公司", "keywordType": "name"}'

# 重渲染已有 JSON
python scripts/render_report.py --input output/cloudmigration.json --output output/cloudmigration.html
python scripts/render_report.py --input output/cloudmigration.json --output output/cloudmigration.md
```

## 输出字段

- `subject`：企业全称、匹配关键词、主体类型、是否自动补全。
- `abstract` / `summary`：封面摘要与详细摘要。
- `metrics`：有效域名数、子域名数、上云资产等级、备案域名数。
- `caliber`：匹配对象、匹配方式、数据范围、产品、局限。
- `core_analysis`：云资产概况（KV）、备案域名明细（表）。
- `representative_records`：代表性备案域名（域名 / 网址 / 是否官网）。
- `insights`：结构化解读（云上资产规模 / 上云深度 / 云架构特征 / 备案合规度）。
- `data_source`：MCP server、数据产品、生成时间、是否 dry-run。

## 内容整理与交付审校

生成后按“原始值 → 规范标签 → 证据位置”逐项整理，保留原始值供核对。`subject.keywordType`、`subject.matchKeyword` 等机器字段保留在 JSON 供系统集成，只从 caliber / 正文可见文本中移除内部代码：

1. **云厂商标签归一**：`AWS`/`Amazon`、`akamai`/`Akamai`、`google`/`Google Cloud` 等同一厂商的不同写法合并，并在括号中保留原始写法；`海外`、`其他` 是上游未具名归类，单列且不计入厂商数，绝不当作具体云厂商。
2. **比例不重算**：支出占比逐行保留，不因同名或别名合并、求和或去重；显式百分比字符串（如 `12.3400%`）原样输出，数值不补零、不舍入、不补齐到 100%，原始厂商写法保存在 JSON 的 `原始标签`。
3. **样本边界**：备案域名指标是上游总量，年度趋势/明细是当前页样本；趋势结论必须写明“当前返回 N 条（上游总量 M）”，不得用样本年度覆盖冒充全量。
4. **不越级推断**：域名数、子域名数、厂商数、资产等级不能推出技术架构、安全风险、跨境业务或监管状态；海外服务器字段只按“是/否”呈现。
5. **交付前自检**：正文不得出现 `keywordType`、`cloudServiceProviderRatio`、`hasOverseasCloudService` 等内部字段名；空维度不渲染；同一句解读不在执行摘要重复。

离线复核已有 JSON（不调用 MCP）：`python scripts/cloud_content_review.py --input <report.json> --out-dir <dir>`；纯函数为 `cloud_content_review.apply_content_review(report)`。

若 API 调用失败，明确报出缺失的配置 / 缺失的工具 / MCP 错误 / 参数校验错误 / 上游网络错误，给出 dry-run 命令或配置步骤，绝不暴露密钥。
