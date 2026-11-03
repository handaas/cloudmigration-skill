# 电商平台云基础设施

- 用户需求：请查看北京京东世纪贸易有限公司的上云资产和备案域名。
- 决策用途：云迁移销售线索评估
- 本轮结果：**本轮检查通过**
- 实际工具调用：2；失败 0
- 章节覆盖率：100%（不代表证据质量）

## 预期业务检查（不自动宣称通过）

- 主体名称准确
- 备案域名与云资产指标分开展示
- 报告能识别云厂商/CDN/IDC 等实际返回维度
- 报告口径说明分页限制

## 本轮自动检查发现


## 使用局限

- 集团关联主体域名可能不归入本主体
- 备案与实际部署位置可能不同

## 证据与复现

- [审计结果](result.json)
- [工具调用、结果形态与响应摘要哈希](calls.json)
- [JSON](report.json) / [HTML](report.html) / [Markdown](report.md)

```bash
python3 cloudmigration-skill/scripts/compose_report.py --enterprise '北京京东世纪贸易有限公司' --page-size 10 --output cloudmigration-skill/output/02-ecommerce-cloud/report.json --report-output cloudmigration-skill/output/02-ecommerce-cloud/report.html
```

## 逐场景业务复核

当前冻结产物逐项满足场景契约；结论仅限本轮公开数据和报告口径。

- **pass** 主体名称准确：subject/title/caliber.match_target 均为“北京京东世纪贸易有限公司”。；本轮当前产物：technical=passed，successful_data_calls=2；subject.enterprise=北京京东世纪贸易有限公司，resolved=True；metrics[有效域名数=31；子域名数=33；上云资产等级=500-1000W；备案域名数=27；备案年份覆盖=2；最新备案年份=2025]；quality={'total_sections': 6, 'populated_sections': 6, 'empty_sections': 0, 'coverage_pct': 100}；非空章节=['云资产概况', '云支出占比', '云服务厂商记录', '备案年度趋势', '海外服务器字段', '备案域名明细']；代表记录=10；calls[-:cloudmigration_cloud_assets=data；-:cloudmigration_domain_info=data(10/27)]
- **pass** 备案域名与云资产指标分开展示：cloud_assets_overview 的有效域名31/子域名33与 domain_records 的备案总量27、当前页10分别展示，且声明不可直接相除。；本轮当前产物：technical=passed，successful_data_calls=2；subject.enterprise=北京京东世纪贸易有限公司，resolved=True；metrics[有效域名数=31；子域名数=33；上云资产等级=500-1000W；备案域名数=27；备案年份覆盖=2；最新备案年份=2025]；quality={'total_sections': 6, 'populated_sections': 6, 'empty_sections': 0, 'coverage_pct': 100}；非空章节=['云资产概况', '云支出占比', '云服务厂商记录', '备案年度趋势', '海外服务器字段', '备案域名明细']；代表记录=10；calls[-:cloudmigration_cloud_assets=data；-:cloudmigration_domain_info=data(10/27)]
- **pass** 报告能识别云厂商/CDN/IDC 等实际返回维度：概况明确厂商“电信、联通”和云支出各50%；CDN、云用量、海外服务器也按上游字段展示。；本轮当前产物：technical=passed，successful_data_calls=2；subject.enterprise=北京京东世纪贸易有限公司，resolved=True；metrics[有效域名数=31；子域名数=33；上云资产等级=500-1000W；备案域名数=27；备案年份覆盖=2；最新备案年份=2025]；quality={'total_sections': 6, 'populated_sections': 6, 'empty_sections': 0, 'coverage_pct': 100}；非空章节=['云资产概况', '云支出占比', '云服务厂商记录', '备案年度趋势', '海外服务器字段', '备案域名明细']；代表记录=10；calls[-:cloudmigration_cloud_assets=data；-:cloudmigration_domain_info=data(10/27)]
- **pass** 报告口径说明分页限制：caliber.limit 明示备案上游总量27、当前页10、第1页、每页最多10条。；本轮当前产物：technical=passed，successful_data_calls=2；subject.enterprise=北京京东世纪贸易有限公司，resolved=True；metrics[有效域名数=31；子域名数=33；上云资产等级=500-1000W；备案域名数=27；备案年份覆盖=2；最新备案年份=2025]；quality={'total_sections': 6, 'populated_sections': 6, 'empty_sections': 0, 'coverage_pct': 100}；非空章节=['云资产概况', '云支出占比', '云服务厂商记录', '备案年度趋势', '海外服务器字段', '备案域名明细']；代表记录=10；calls[-:cloudmigration_cloud_assets=data；-:cloudmigration_domain_info=data(10/27)]

## 离线浏览器检查

[Ego Lite 离线图表、页面溢出和脚本检查](browser-check.json)