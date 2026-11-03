# 金融机构云资产边界

- 用户需求：请查询招商银行股份有限公司的公开云资产，并注明不能据此判断的内容。
- 决策用途：金融行业云合作前置调研
- 本轮结果：**本轮检查通过**
- 实际工具调用：2；失败 0
- 章节覆盖率：100%（不代表证据质量）

## 预期业务检查（不自动宣称通过）

- 只展示公开可得资产事实
- 安全或合规结论不由域名数量推断
- 报告明确数据覆盖边界
- 敏感配置和凭证绝不出现

## 本轮自动检查发现


## 使用局限

- 不得据报告推断内部网络拓扑或安全水平
- 金融机构可能使用专有云且公开线索有限

## 证据与复现

- [审计结果](result.json)
- [工具调用、结果形态与响应摘要哈希](calls.json)
- [JSON](report.json) / [HTML](report.html) / [Markdown](report.md)

```bash
python3 cloudmigration-skill/scripts/compose_report.py --enterprise '招商银行股份有限公司' --page-size 8 --output cloudmigration-skill/output/04-bank-cloud-boundary/report.json --report-output cloudmigration-skill/output/04-bank-cloud-boundary/report.html
```

## 逐场景业务复核

当前冻结产物逐项满足场景契约；结论仅限本轮公开数据和报告口径。

- **pass** 只展示公开可得资产事实：报告仅列有效域名163、子域名718、资产等级、厂商/支出与8条备案域名字段。；本轮当前产物：technical=passed，successful_data_calls=2；subject.enterprise=招商银行股份有限公司，resolved=True；metrics[有效域名数=163；子域名数=718；上云资产等级=5000W以上；备案域名数=10；备案年份覆盖=4；最新备案年份=2026]；quality={'total_sections': 6, 'populated_sections': 6, 'empty_sections': 0, 'coverage_pct': 100}；非空章节=['云资产概况', '云支出占比', '云服务厂商记录', '备案年度趋势', '海外服务器字段', '备案域名明细']；代表记录=8；calls[-:cloudmigration_cloud_assets=data；-:cloudmigration_domain_info=data(8/10)]
- **pass** 安全或合规结论不由域名数量推断：summary 明示不作安全或监管判断；各 insight 也明确数量不能单独推断安全风险或监管状态。；本轮当前产物：technical=passed，successful_data_calls=2；subject.enterprise=招商银行股份有限公司，resolved=True；metrics[有效域名数=163；子域名数=718；上云资产等级=5000W以上；备案域名数=10；备案年份覆盖=4；最新备案年份=2026]；quality={'total_sections': 6, 'populated_sections': 6, 'empty_sections': 0, 'coverage_pct': 100}；非空章节=['云资产概况', '云支出占比', '云服务厂商记录', '备案年度趋势', '海外服务器字段', '备案域名明细']；代表记录=8；calls[-:cloudmigration_cloud_assets=data；-:cloudmigration_domain_info=data(8/10)]
- **pass** 报告明确数据覆盖边界：caliber.limit 明示公开探测覆盖、不同产品不可直接相除、备案总量10/当前页8及更新延迟。；本轮当前产物：technical=passed，successful_data_calls=2；subject.enterprise=招商银行股份有限公司，resolved=True；metrics[有效域名数=163；子域名数=718；上云资产等级=5000W以上；备案域名数=10；备案年份覆盖=4；最新备案年份=2026]；quality={'total_sections': 6, 'populated_sections': 6, 'empty_sections': 0, 'coverage_pct': 100}；非空章节=['云资产概况', '云支出占比', '云服务厂商记录', '备案年度趋势', '海外服务器字段', '备案域名明细']；代表记录=8；calls[-:cloudmigration_cloud_assets=data；-:cloudmigration_domain_info=data(8/10)]
- **pass** 敏感配置和凭证绝不出现：报告中未出现 secret、signature、token、password、authorization、密钥或签名内容。；本轮当前产物：technical=passed，successful_data_calls=2；subject.enterprise=招商银行股份有限公司，resolved=True；metrics[有效域名数=163；子域名数=718；上云资产等级=5000W以上；备案域名数=10；备案年份覆盖=4；最新备案年份=2026]；quality={'total_sections': 6, 'populated_sections': 6, 'empty_sections': 0, 'coverage_pct': 100}；非空章节=['云资产概况', '云支出占比', '云服务厂商记录', '备案年度趋势', '海外服务器字段', '备案域名明细']；代表记录=8；calls[-:cloudmigration_cloud_assets=data；-:cloudmigration_domain_info=data(8/10)]

## 离线浏览器检查

[Ego Lite 离线图表、页面溢出和脚本检查](browser-check.json)