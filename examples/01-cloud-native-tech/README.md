# 大型科技企业云资产画像

- 用户需求：请分析腾讯科技（深圳）有限公司的域名、CDN、IDC、云厂商和云用量线索。
- 决策用途：云服务竞争与基础设施画像
- 本轮结果：**本轮检查通过**
- 实际工具调用：2；失败 0
- 章节覆盖率：67%（不代表证据质量）

## 预期业务检查（不自动宣称通过）

- 云资产概况与备案域名明细同时检查
- 域名记录可读且不重复夸大
- 云厂商和 IDC 字段仅按返回事实描述
- 缺失字段不置为零

## 本轮自动检查发现


## 使用局限

- 公开备案域名不等于全部线上资产
- 无法仅据报告确认实时云消费金额

## 证据与复现

- [审计结果](result.json)
- [工具调用、结果形态与响应摘要哈希](calls.json)
- [JSON](report.json) / [HTML](report.html) / [Markdown](report.md)

```bash
python3 cloudmigration-skill/scripts/compose_report.py --enterprise '腾讯科技（深圳）有限公司' --page-size 10 --output cloudmigration-skill/output/01-cloud-native-tech/report.json --report-output cloudmigration-skill/output/01-cloud-native-tech/report.html
```

## 逐场景业务复核

当前冻结产物逐项满足场景契约；结论仅限本轮公开数据和报告口径。

- **pass** 云资产概况与备案域名明细同时检查：core_analysis 同时含 cloud_assets_overview 与2条 domain_records；quality_report 为4/6。；本轮当前产物：technical=passed，successful_data_calls=2；subject.enterprise=腾讯科技（深圳）有限公司，resolved=True；metrics[有效域名数=4；子域名数=6；上云资产等级=1000-5000W；备案域名数=2；备案年份覆盖=2；最新备案年份=2017]；quality={'total_sections': 6, 'populated_sections': 4, 'empty_sections': 2, 'coverage_pct': 67}；非空章节=['云资产概况', '备案年度趋势', '海外服务器字段', '备案域名明细']；代表记录=2；calls[-:cloudmigration_cloud_assets=data；-:cloudmigration_domain_info=data(2/2)]
- **pass** 域名记录可读且不重复夸大：domain_records 为 wecity-qcloud.com、hudongcdn.com 两条唯一域名；summary 明确上游备案总量2、当前页2。；本轮当前产物：technical=passed，successful_data_calls=2；subject.enterprise=腾讯科技（深圳）有限公司，resolved=True；metrics[有效域名数=4；子域名数=6；上云资产等级=1000-5000W；备案域名数=2；备案年份覆盖=2；最新备案年份=2017]；quality={'total_sections': 6, 'populated_sections': 4, 'empty_sections': 2, 'coverage_pct': 67}；非空章节=['云资产概况', '备案年度趋势', '海外服务器字段', '备案域名明细']；代表记录=2；calls[-:cloudmigration_cloud_assets=data；-:cloudmigration_domain_info=data(2/2)]
- **pass** 云厂商和 IDC 字段仅按返回事实描述：云资产概况只展示上游有效域名4、子域名6、资产等级及海外服务器字段；未推断架构、安全或监管结论。；本轮当前产物：technical=passed，successful_data_calls=2；subject.enterprise=腾讯科技（深圳）有限公司，resolved=True；metrics[有效域名数=4；子域名数=6；上云资产等级=1000-5000W；备案域名数=2；备案年份覆盖=2；最新备案年份=2017]；quality={'total_sections': 6, 'populated_sections': 4, 'empty_sections': 2, 'coverage_pct': 67}；非空章节=['云资产概况', '备案年度趋势', '海外服务器字段', '备案域名明细']；代表记录=2；calls[-:cloudmigration_cloud_assets=data；-:cloudmigration_domain_info=data(2/2)]
- **pass** 缺失字段不置为零：缺失 vendor/spend 列表保持为空；没有把未知厂商或IDC字段写成0。；本轮当前产物：technical=passed，successful_data_calls=2；subject.enterprise=腾讯科技（深圳）有限公司，resolved=True；metrics[有效域名数=4；子域名数=6；上云资产等级=1000-5000W；备案域名数=2；备案年份覆盖=2；最新备案年份=2017]；quality={'total_sections': 6, 'populated_sections': 4, 'empty_sections': 2, 'coverage_pct': 67}；非空章节=['云资产概况', '备案年度趋势', '海外服务器字段', '备案域名明细']；代表记录=2；calls[-:cloudmigration_cloud_assets=data；-:cloudmigration_domain_info=data(2/2)]

## 离线浏览器检查

[Ego Lite 离线图表、页面溢出和脚本检查](browser-check.json)
[页面截图](browser.png)