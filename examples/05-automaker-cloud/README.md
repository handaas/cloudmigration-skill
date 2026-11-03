# 车企云资产画像

- 用户需求：请分析比亚迪股份有限公司的备案域名和云服务商线索。
- 决策用途：车联网及企业云商机研究
- 本轮结果：**本轮检查通过**
- 实际工具调用：2；失败 0
- 章节覆盖率：100%（不代表证据质量）

## 预期业务检查（不自动宣称通过）

- 备案域名明细字段完整
- 云厂商分布依据数据而非品牌常识
- 报告中的总数和样本条数可区分
- 空章节跳过

## 本轮自动检查发现


## 使用局限

- 关联品牌和海外域名可能分属其他主体
- 无法据公开资产确认车联网技术架构

## 证据与复现

- [审计结果](result.json)
- [工具调用、结果形态与响应摘要哈希](calls.json)
- [JSON](report.json) / [HTML](report.html) / [Markdown](report.md)

```bash
python3 cloudmigration-skill/scripts/compose_report.py --enterprise '比亚迪股份有限公司' --page-size 10 --output cloudmigration-skill/output/05-automaker-cloud/report.json --report-output cloudmigration-skill/output/05-automaker-cloud/report.html
```

## 逐场景业务复核

当前冻结产物逐项满足场景契约；结论仅限本轮公开数据和报告口径。

- **pass** 备案域名明细字段完整：10条 domain_records 均保留网址、备案号、审核时间和官网标识。；本轮当前产物：technical=passed，successful_data_calls=2；subject.enterprise=比亚迪股份有限公司，resolved=True；metrics[有效域名数=127；子域名数=143；上云资产等级=5000W以上；备案域名数=18；备案年份覆盖=4；最新备案年份=2026；官网数=2]；quality={'total_sections': 6, 'populated_sections': 6, 'empty_sections': 0, 'coverage_pct': 100}；非空章节=['云资产概况', '云支出占比', '云服务厂商记录', '备案年度趋势', '海外服务器字段', '备案域名明细']；代表记录=10；calls[-:cloudmigration_cloud_assets=data；-:cloudmigration_domain_info=data(10/18)]
- **pass** 云厂商分布依据数据而非品牌常识：vendor_dist 的15个厂商与 cloud_assets 调用结果一致，报告明确不从厂商数推断容灾/依赖。；本轮当前产物：technical=passed，successful_data_calls=2；subject.enterprise=比亚迪股份有限公司，resolved=True；metrics[有效域名数=127；子域名数=143；上云资产等级=5000W以上；备案域名数=18；备案年份覆盖=4；最新备案年份=2026；官网数=2]；quality={'total_sections': 6, 'populated_sections': 6, 'empty_sections': 0, 'coverage_pct': 100}；非空章节=['云资产概况', '云支出占比', '云服务厂商记录', '备案年度趋势', '海外服务器字段', '备案域名明细']；代表记录=10；calls[-:cloudmigration_cloud_assets=data；-:cloudmigration_domain_info=data(10/18)]
- **pass** 报告中的总数和样本条数可区分：subject 及 caliber.limit 明示 domain_total=18、domain_returned=10、page_size=10。；本轮当前产物：technical=passed，successful_data_calls=2；subject.enterprise=比亚迪股份有限公司，resolved=True；metrics[有效域名数=127；子域名数=143；上云资产等级=5000W以上；备案域名数=18；备案年份覆盖=4；最新备案年份=2026；官网数=2]；quality={'total_sections': 6, 'populated_sections': 6, 'empty_sections': 0, 'coverage_pct': 100}；非空章节=['云资产概况', '云支出占比', '云服务厂商记录', '备案年度趋势', '海外服务器字段', '备案域名明细']；代表记录=10；calls[-:cloudmigration_cloud_assets=data；-:cloudmigration_domain_info=data(10/18)]
- **pass** 空章节跳过：quality_report 6/6；无数据时渲染器不生成空表，本例所有章节均有真实返回。；本轮当前产物：technical=passed，successful_data_calls=2；subject.enterprise=比亚迪股份有限公司，resolved=True；metrics[有效域名数=127；子域名数=143；上云资产等级=5000W以上；备案域名数=18；备案年份覆盖=4；最新备案年份=2026；官网数=2]；quality={'total_sections': 6, 'populated_sections': 6, 'empty_sections': 0, 'coverage_pct': 100}；非空章节=['云资产概况', '云支出占比', '云服务厂商记录', '备案年度趋势', '海外服务器字段', '备案域名明细']；代表记录=10；calls[-:cloudmigration_cloud_assets=data；-:cloudmigration_domain_info=data(10/18)]

## 离线浏览器检查

[Ego Lite 离线图表、页面溢出和脚本检查](browser-check.json)