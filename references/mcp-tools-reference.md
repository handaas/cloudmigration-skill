# MCP 工具参考 — cloudmigration-mcp-server

本 skill 连接的 MCP server：`handaas-mcp-server/cloudmigration-mcp-server`（“上云大数据”）。

> **重要**：云资产/备案域名工具入参为 `matchKeyword`（**企业全称** / 注册号 / 统一社会信用代码 / 企业 id）+ `keywordType`；当用户只给企业关键词时，必须先调关键词模糊查询补全全称。

## 通用约定

- `keywordType` 枚举：`name`（企业名称）/ `nameId`（企业 id）/ `regNumber`（注册号）/ `socialCreditCode`（统一社会信用代码）。
- 分页：`pageIndex` 从 1 开始；备案域名 `pageSize` 单页最多 50。
- 0/1 布尔字段：`0` 表示“否”，`1` 表示“是”。

---

## 工具清单

### 1. `cloudmigration_cloud_assets` — 企业云资产

用途：查询企业的云上资产信息，包括有效域名、子域名、云服务厂商及用量、CDN、IDC、云存储、海外服务器、上云资产等级等。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `matchKeyword` | string | 是 | 企业名称 / 注册号 / 统一社会信用代码 / 企业 id（无全称则先调 fuzzy_search） |
| `keywordType` | string | 否 | 主体类型：name / nameId / regNumber / socialCreditCode |

返回：`effectiveSubDomainList`（有效域名 list）、`effectiveSubDomainNum`（有效域名数量）、`subDomainList`（子域名 list）、`subDomainNum`（子域名数量）、`cloudServerList`（云服务厂商 list）、`cloudServerNumInterval`（云用量范围）、`cloudConsumptionScale`（上云资产等级）、`cloudServiceProviderRatio`（厂商占比 list of {cloudService, ratio}）、`hasCdn`（0/1）、`cdnServerNum`（CDN 使用规模）、`cdnServerList`（CDN 服务商 list）、`hasIDC`（0/1）、`hasCloudStorage`（0/1）、`hasOverseasCloudService`（0/1）。

product_id：`6704f43fa9a1ec205f429e05`。

---

### 2. `cloudmigration_fuzzy_search` — 关键词模糊查询企业

用途：根据企业名称 / 人名 / 品牌 / 产品 / 岗位等关键词模糊查询企业列表，用于补全企业全称。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `matchKeyword` | string | 是 | 匹配关键词 |
| `pageIndex` | int | 否 | 分页开始位置（默认 1） |
| `pageSize` | int | 否 | 单页最多 50 |

返回：`total` + 企业列表（`name`、`nameId`、`regCapitalValue`、`foundTime`、`operStatus`、`address`、`legalRepresentative`、`enterpriseType`、`catchReason` 命中原因等）。

product_id：`675cea1f0e009a9ea37edaa1`。

---

### 3. `cloudmigration_domain_info` — 备案域名信息

用途：按企业主体查询已注册的备案域名信息，包括域名名称、对应网址、审核时间、是否官网、网站备案号。适合域名资产管理、合规核查与品牌安全监测。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `matchKeyword` | string | 是 | 企业名称 / 注册号 / 统一社会信用代码 / 企业 id（无全称则先调 fuzzy_search） |
| `pageIndex` | int | 否 | 页码（默认 1） |
| `keywordType` | string | 否 | 主体类型：name / nameId / regNumber / socialCreditCode |
| `pageSize` | int | 否 | 单页最多 50 |

返回（list + `total`）：`domainName`（域名名称）、`domainUrl`（网址）、`websiteRecord`（网站备案号）、`filingAuditTime`（审核时间）、`isHomePage`（是否官网 0/1）。

product_id：`66a0f258ce3408eb23b56706`。

---

## 推荐调用顺序（报告编排）

1. （若仅有关键词）`cloudmigration_fuzzy_search` → 取 `name` 作为全称。
2. `cloudmigration_cloud_assets` → 云资产概况。
3. `cloudmigration_domain_info` → 备案域名明细。

> 单次报告通常调用 2-3 个工具；云资产/备案域名入参均为企业主体 `matchKeyword` + `keywordType`。
