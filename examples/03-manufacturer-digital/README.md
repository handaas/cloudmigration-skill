# 制造企业数字基础设施

- 用户需求：请评估美的集团股份有限公司的云资产覆盖和备案域名数量。
- 决策用途：制造业数字化成熟度线索
- 本轮结果：**本轮检查通过**
- 实际工具调用：2；失败 0
- 章节覆盖率：100%（不代表证据质量）

## 预期业务检查（不自动宣称通过）

- 关键数量引用实际返回
- 域名样本与总量区分
- 不能把域名数量直接等同数字化成熟度
- 空云厂商字段不生成推断

## 本轮自动检查发现


## 使用局限

- 云资产只是数字化成熟度的间接信号
- 海外或未备案域名可能不在范围内

## 证据与复现

- [审计结果](result.json)
- [工具调用、结果形态与响应摘要哈希](calls.json)
- [JSON](report.json) / [HTML](report.html) / [Markdown](report.md)

```bash
python3 cloudmigration-skill/scripts/compose_report.py --enterprise '美的集团股份有限公司' --page-size 8 --output cloudmigration-skill/output/03-manufacturer-digital/report.json --report-output cloudmigration-skill/output/03-manufacturer-digital/report.html
```

## 逐场景业务复核

当前冻结产物逐项满足场景契约；结论仅限本轮公开数据和报告口径。

- **pass** 关键数量引用实际返回：metrics 引用上游有效域名119、子域名178、备案域名4、资产等级5000W以上。；本轮当前产物：technical=passed，successful_data_calls=2；subject.enterprise=美的集团股份有限公司，resolved=True；metrics[有效域名数=119；子域名数=178；上云资产等级=5000W以上；备案域名数=4；备案年份覆盖=2；最新备案年份=2026；官网数=2]；quality={'total_sections': 6, 'populated_sections': 6, 'empty_sections': 0, 'coverage_pct': 100}；非空章节=['云资产概况', '云支出占比', '云服务厂商记录', '备案年度趋势', '海外服务器字段', '备案域名明细']；代表记录=4；calls[-:cloudmigration_cloud_assets=data；-:cloudmigration_domain_info=data(4/4)]
- **pass** 域名样本与总量区分：备案总量4、当前页4与具体4条 domain_records 分开呈现。；本轮当前产物：technical=passed，successful_data_calls=2；subject.enterprise=美的集团股份有限公司，resolved=True；metrics[有效域名数=119；子域名数=178；上云资产等级=5000W以上；备案域名数=4；备案年份覆盖=2；最新备案年份=2026；官网数=2]；quality={'total_sections': 6, 'populated_sections': 6, 'empty_sections': 0, 'coverage_pct': 100}；非空章节=['云资产概况', '云支出占比', '云服务厂商记录', '备案年度趋势', '海外服务器字段', '备案域名明细']；代表记录=4；calls[-:cloudmigration_cloud_assets=data；-:cloudmigration_domain_info=data(4/4)]
- **pass** 不能把域名数量直接等同数字化成熟度：summary 明示“不作技术实践、安全或监管判断”；insights 对数量逐项声明不能推断架构/规模/风险/监管。；本轮当前产物：technical=passed，successful_data_calls=2；subject.enterprise=美的集团股份有限公司，resolved=True；metrics[有效域名数=119；子域名数=178；上云资产等级=5000W以上；备案域名数=4；备案年份覆盖=2；最新备案年份=2026；官网数=2]；quality={'total_sections': 6, 'populated_sections': 6, 'empty_sections': 0, 'coverage_pct': 100}；非空章节=['云资产概况', '云支出占比', '云服务厂商记录', '备案年度趋势', '海外服务器字段', '备案域名明细']；代表记录=4；calls[-:cloudmigration_cloud_assets=data；-:cloudmigration_domain_info=data(4/4)]
- **pass** 空云厂商字段不生成推断：本例 vendor_dist 有12条真实返回；报告只列厂商及占比，若为空不会生成替代推断。；本轮当前产物：technical=passed，successful_data_calls=2；subject.enterprise=美的集团股份有限公司，resolved=True；metrics[有效域名数=119；子域名数=178；上云资产等级=5000W以上；备案域名数=4；备案年份覆盖=2；最新备案年份=2026；官网数=2]；quality={'total_sections': 6, 'populated_sections': 6, 'empty_sections': 0, 'coverage_pct': 100}；非空章节=['云资产概况', '云支出占比', '云服务厂商记录', '备案年度趋势', '海外服务器字段', '备案域名明细']；代表记录=4；calls[-:cloudmigration_cloud_assets=data；-:cloudmigration_domain_info=data(4/4)]

## 离线浏览器检查

[Ego Lite 离线图表、页面溢出和脚本检查](browser-check.json)