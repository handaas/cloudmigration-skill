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

## AI 审校交付门禁（草稿 → final）

`compose_report.py` / `compose_fusion_report.py` 的正常生成与 `--dry-run` 都只产出数据草稿：JSON 标记 `data_source.semantic_review.status=pending`，同时生成的 HTML/Markdown 带“数据草稿（待AI语义审校）”提示，不能作为最终交付。`apply_content_review`、`organize_report` 等确定性整理只做规则清洗，不是语义审校，不能替代当前 AI 的实际阅读。

```bash
python scripts/review_report.py --input output/draft.json --request output/review-request.json
# 当前 AI 阅读 output/review-request.json 的 report 后写 output/ai-review.json
python scripts/review_report.py --input output/draft.json --review output/ai-review.json \
  --output output/final/report.json --report-output output/final/report.html
```

`--request` 只读草稿并生成审校请求，不调用 MCP、外部模型 API 或新增查询；`--review` 应用当前 AI 的逐项判断，写出最终 JSON，并由同一 JSON 渲染 HTML/Markdown（需要 PDF 时加 `--pdf-output`）。两个命令都只允许写入本 Skill 的 `output/` 目录，且不能覆盖原草稿或审校文件。

### 审校响应 JSON

请求包含 `source_sha256`、`report`、`visible_section_keys`、`instructions`、`response_fields`。响应必须是 JSON 对象：

```json
{
  "source_sha256": "<与请求完全一致>",
  "summary": [
    {"text": "逐句摘要中的一句", "sources": ["/core_analysis/..."], "kind": "fact"}
  ],
  "normalizations": [
    {"sources": ["/core_analysis/..."], "category": "语义类别", "normalized": "规范表达", "evidence": "原文摘录", "reason": "归类理由"}
  ],
  "insights": [
    {"feature": "特征", "evidence": "证据摘录", "interpretation": "有依据的解读", "sources": ["/metrics/0"]}
  ]
}
```

- `source_sha256` 必须与请求一致；对不上表示草稿已变化，须重新生成请求，不能沿用旧判断。
- `sources` 使用本报告 JSON Pointer，只能指向实际存在的 `/subject/…`、`/core_analysis/…`、`/metrics/…`、`/caliber/…`、`/data_source/…`、`/analysis_request/…`。`/core_analysis/sections` 与 `/data_source/semantic_review` 只是章节定义/状态，不能作为事实依据；旧 `abstract`/`summary`/`insights` 也不能当事实依据。
- 每项至少一个来源，且不能重复同一路径；同一来源可支持多条判断。不能引用其他企业、其他案例、其他记录或常识来补本记录。
- `summary` 写 3–5 句有信息量的逐句摘要，其 `kind` 只能是 `fact`（有数据的事实）、`interpretation`（可回溯的解释）或 `limitation`（覆盖、口径、未查询限制）。没有数据依据时只能写 `limitation`，不能生成事实或业务解释。
- `normalizations` 是独立视图，不改写原始字段：`normalized` 做语义归类和别名合并，`category` 写类别，`reason` 写逐项理由。`evidence` 必填，由当前 AI 选择简洁可读的原文摘录作为“原文依据”列，并由同项 `sources` 支撑，完整原值仍保留在 draft/request 与来源 SHA 记录中。必须保留来源中的否定、最高、至少、至多、试用期、转正后、仅限、部分、疑似、待定、已失效等限定；不同主体、互斥金额或比例不能合并；没有实际归类需要时可为空。
- `insights` 的 `feature`、`evidence` 和 `interpretation` 都必须由同一 `sources` 支撑；`evidence` 是实际 AI 写的简洁可读证据摘录，保留来源数字、单位与限定；不推断上下游关系、低风险、经营能力或行业地位。
- 文本中的每个数字（含千分位、百分号与原始小数位）必须逐字出现在所引 values 中；`normalized`、`category`、`reason`、`evidence` 和洞察文本同样适用。不得发明派生数字或改变精度；需要派生指标时先在脚本中计算并写入报告，再引用。
- 只使用本次数据；不调用 MCP、外部模型 API，也不新增查询。审校文件是 `output/ai-review.json`，不是最终报告。
- 应用后 `data_source.semantic_review.status=reviewed`，并记录 `source_sha256`、原 `generated_at`、审校时间与判断证据；原查询时间和原件不变。`summary` 写入 `abstract`/`summary`/`executive_summary`，`normalizations` 写入 `core_analysis.ai_normalization`（独立表格），`insights` 写入 `insights`；原始字段不改写。

### 展示与交付核对

- 空板块连标题和目录一起隐藏，但隐藏只为展示：不能从 `quality_report` 的分母抹去未覆盖维度，也不能因此提高覆盖率。真实 `0`/`False` 原样保留；缺失 `-` 与未查询不等于 0；失败或未查询只在口径限制中简述，不补数据、不推断“无风险”。
- AI 标准化与摘要是解释视图，不新增数据来源，也不改变原始字段或源数据覆盖率。
- 最终 JSON 是草稿加实际审校后的新副本；最终 HTML/Markdown 必须从该 JSON 渲染，并核对章节、目录、图表和空板块。只有请求文件、草稿或手工润色件不算完成。

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

审校复核：完整保留有来源的摘要句子及采集层“数据缺口／主体解析受阻”提示；重审不得引用 `/core_analysis/ai_normalization` 等既有 AI 视图作为原始证据。HTML 与 Markdown 应使用一致的样本数量、趋势顺序及数据列，单元格中的竖线和换行不得破坏表格结构。
