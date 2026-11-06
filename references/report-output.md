# 报告输出 — 上云大数据报告

本文件规定 `cloudmigration-report` skill 产出的报告结构、质量底线与渲染工作流。所有产物遵循 `AGENTS.md` 的统一 JSON 骨架与本 skill 的领域裁剪。

## 默认展示模式

- HTML：可分享 / 可交付的可视化报告；独立本地文件，内嵌 CSS，无调试 / 内部段落。
- Markdown：知识库 / wiki / PRD / 后续手工编辑。
- JSON：系统集成或二次处理。

`compose_report.py` 通过 `--report-output <path>` 同时产出 HTML + Markdown；`--output <path>` 产出 JSON。`render_report.py` 可基于已有 JSON 重渲染。

## 报告结构（7 章）

1. **报告摘要**：分析对象、数据覆盖范围、核心发现、关键指标卡。
2. **查询对象与口径**：企业全称、匹配方式、数据范围、产品、局限。
3. **数据总览**：有效域名数、子域名数、上云资产等级、备案域名数等指标卡。
4. **核心分析**（上云专属子章节，由 `core_analysis.sections` 驱动渲染）：
   - 云资产概况（KV：有效域名 / 子域名 / 云厂商 / 云用量 / CDN / IDC / 云存储 / 海外服务器 / 上云等级）。
   - 备案域名明细（表：域名名称 / 网址 / 网站备案号 / 审核时间 / 是否官网）。
5. **代表性记录**：关键备案域名 Top N（域名 / 网址 / 是否官网）。
6. **特征与洞察**：只描述上游返回的域名、厂商、资产等级、海外服务器字段和备案年度记录；不得由数量或等级推断技术实践、安全风险、跨境业务或监管状态。
7. **数据口径与来源**：MCP server、数据产品、生成时间、是否 dry-run。

## 质量底线

- 报告脱离 Skill 上下文也可独立阅读；正文只见云资产事实与结构化数据。
- 绝不出现工具名、入参（如 `matchKeyword=...`）、product_id、内部字段名、空表、调试信息。
- HTML 采用研究报告视觉风格：A4 风、灰色顶部条纹、蓝色报告横幅、左侧目录 / 范围侧栏、深蓝章节标题、深蓝表头、浅蓝斑马行、打印友好分页。
- 数据为空时明确说明数据范围 / 口径，不渲染空表、不臆造事实。
- 备案域名必须同时披露上游 `total` 与实际归纳条数（采集完整性以 `data_source.pagination` 与摘要披露为准，未取全时必须标注剩余条数与停止原因）；云资产产品与备案域名产品的不同总体不得直接相除。
- 绝不打印 `secret_id` / `secret_key` / 签名 / token / 原始签名请求。
- 自动补全企业全称时，在报告口径中说明“由关键词模糊查询补全”。

### 数据格式约束（铁律）

以下约束适用于 compose_report.py 组装数据与 render_report.py 渲染输出的全过程：

1. **嵌套 JSON 字符串必须解析**：MCP 返回的某些字段（如 `regCapital`、`addressValue`、`subscriptionDetail`）可能是 JSON 字符串（例：`{"coinType":"人民币","value":430000000.0}`）。compose 层必须调用 `_unwrap_json_str()` / `_parse_reg_capital()` / `_flatten_addr()` 解析为可读文本（如"4.30 亿 人民币"、"浙江省杭州市滨江区..."）。绝不在报告正文、表格单元格或指标值中输出原始 JSON 字符串。

2. **section 标题必须用中文**：`core_analysis.sections` 数组中每个 section 的 `title` 字段必须使用中文（如"企业基本信息"、"对外投资"、"股东信息"）。`key` 字段用英文 snake_case 供程序索引，但 `title` 绝不可显示英文 key。即使缺少 sections 数组，渲染器回退逻辑也内置了 `_TITLE_MAP` 映射。

3. **指标值可读化**：所有 `metrics` 的 `value` 字段必须格式化为人类可读形式：
   - 金额：`10995210218.0` → `109.95 亿 人民币`（≥1 亿用亿，≥1 万用万）
   - 地址：嵌套 dict → 省+市+区拼接 或取 `value` 字段
   - 比率：`0.8858` → `88.58%`
   - 日期：保持 `yyyy-MM-dd` 格式
   - "-" 表示字段缺失（MCP 未返回）；`0` 表示真实为零

4. **企业画像指标提取**：有 fuzzy_search 的 skill 必须从返回的 record 中提取 `regCapitalValue` / `foundTime` / `operStatus` / `enterpriseType` / `legalRepresentative`，通过 `_enrich_metrics_with_profile()` 追加为指标卡。

5. **派生边界**：仅可从同一返回集合计算可复核的展示统计，不为凑足指标数量派生比例，不跨产品总体计算覆盖率。

## 工作流

```bash
# 1. 干跑（不调真实 API，用样例数据组装报告骨架）
python scripts/compose_report.py \
  --enterprise "示例科技有限公司" \
  --dry-run \
  --output output/cloudmigration.json \
  --report-output output/cloudmigration.html

# 2. 真实查询 + 渲染（需 MCP 连接就绪）
python scripts/compose_report.py \
  --enterprise "示例科技有限公司" \
  --output output/cloudmigration.json \
  --report-output output/cloudmigration.html

# 3. 重渲染已有 JSON
python scripts/render_report.py --input output/cloudmigration.json --output output/cloudmigration.html
python scripts/render_report.py --input output/cloudmigration.json --output output/cloudmigration.md
```

返回：JSON 路径、HTML 路径、Markdown 路径，以及企业全称映射与数据口径摘要。

## 内容审校（离线）

对已有 `report.json` 复核而不调用 MCP：`python scripts/cloud_content_review.py --input <report.json> --out-dir <dir>`；纯函数 `cloud_content_review.apply_content_review(report)` 返回深拷贝，可单独测试。审校顺序：

1. 云厂商标签：同义写法合并、`海外/其他` 单列为上游未具名归类，不计厂商数；原始写法保留在 `原始标签`。
2. 比例：支出占比记录逐行保留，不因别名合并或求和；显式百分比字符串原样输出，不四舍五入、不补齐到 100%。
   报告 `spend_dist` 的 `支出占比` / `支出占比数值` 已是百分数单位，旧报告中的数值 `0.5` 代表 `0.5%`；不可按数值大小猜测单位。只有原始接口的 0–1 比例按分数转换；显式 `0.5%` / `1.00%` 不再乘 100。
   云支出占比使用逐条可见表格，不用饼图的 `{d}%` 将源值再次归一化；正常生成、离线复核及独立重渲染都保留同一源端展示串，不假定记录互斥或合计为 100%。
3. 证据：备案年度趋势必须带“当前返回 N 条（上游总量 M）”；指标卡不删除 `0`。
4. 措辞：删除 `keywordType`、`cloudServiceProviderRatio` 等内部字段名；不以资产等级推断技术/安全/跨境结论。

交付前按最终 `sections` 与实际 body 刷新 `data_source.quality_report`（`0` 计为已填充；`coverage_pct` 仅为章节填充率，不是准确率）；保留原 `generated_at`。

CLI 会拒绝 `--out-dir` 的 `report.json` 解析为 `--input` 的调用；输出目标应位于本 skill 的 `output/content-quality-review/`，不得覆盖 `examples/` 或 `test-records/`。
