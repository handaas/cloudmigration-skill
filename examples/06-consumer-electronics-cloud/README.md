# 消费电子企业云线索

- 用户需求：请查看小米科技有限责任公司的上云情况和主要域名。
- 决策用途：云生态合作机会识别
- 本轮结果：**本轮检查通过**
- 实际工具调用：2；失败 0
- 章节覆盖率：100%（不代表证据质量）

## 预期业务检查（不自动宣称通过）

- 主体全称直查
- 域名、CDN 和云厂商信息分别呈现
- 洞察引用报告证据
- 不输出原始嵌套 JSON

## 本轮自动检查发现


## 使用局限

- 集团内其他经营主体可能不在查询范围
- 域名所有权与业务运营主体可能不一致

## 证据与复现

- [审计结果](result.json)
- [工具调用、结果形态与响应摘要哈希](calls.json)
- [JSON](report.json) / [HTML](report.html) / [Markdown](report.md)

```bash
python3 cloudmigration-skill/scripts/compose_report.py --enterprise '小米科技有限责任公司' --page-size 10 --output cloudmigration-skill/output/06-consumer-electronics-cloud/report.json --report-output cloudmigration-skill/output/06-consumer-electronics-cloud/report.html
```

## 逐场景业务复核

当前冻结产物逐项满足场景契约；结论仅限本轮公开数据和报告口径。

- **pass** 主体全称直查：subject.enterprise 与 match_raw 均为“小米科技有限责任公司”，resolved=true。；本轮当前产物：technical=passed，successful_data_calls=2；subject.enterprise=小米科技有限责任公司，resolved=True；metrics[有效域名数=1427；子域名数=3602；上云资产等级=5000W以上；备案域名数=92；备案年份覆盖=1；最新备案年份=2025]；quality={'total_sections': 6, 'populated_sections': 6, 'empty_sections': 0, 'coverage_pct': 100}；非空章节=['云资产概况', '云支出占比', '云服务厂商记录', '备案年度趋势', '海外服务器字段', '备案域名明细']；代表记录=10；calls[-:cloudmigration_cloud_assets=data；-:cloudmigration_domain_info=data(10/92)]
- **pass** 域名、CDN 和云厂商信息分别呈现：overview 分列有效域名、子域名、CDN节点、云服务厂商；domain_records 独立列出10条备案域名。；本轮当前产物：technical=passed，successful_data_calls=2；subject.enterprise=小米科技有限责任公司，resolved=True；metrics[有效域名数=1427；子域名数=3602；上云资产等级=5000W以上；备案域名数=92；备案年份覆盖=1；最新备案年份=2025]；quality={'total_sections': 6, 'populated_sections': 6, 'empty_sections': 0, 'coverage_pct': 100}；非空章节=['云资产概况', '云支出占比', '云服务厂商记录', '备案年度趋势', '海外服务器字段', '备案域名明细']；代表记录=10；calls[-:cloudmigration_cloud_assets=data；-:cloudmigration_domain_info=data(10/92)]
- **pass** 洞察引用报告证据：每条 insight 都引用具体返回值，并明确不据此推断架构、业务、安全或监管。；本轮当前产物：technical=passed，successful_data_calls=2；subject.enterprise=小米科技有限责任公司，resolved=True；metrics[有效域名数=1427；子域名数=3602；上云资产等级=5000W以上；备案域名数=92；备案年份覆盖=1；最新备案年份=2025]；quality={'total_sections': 6, 'populated_sections': 6, 'empty_sections': 0, 'coverage_pct': 100}；非空章节=['云资产概况', '云支出占比', '云服务厂商记录', '备案年度趋势', '海外服务器字段', '备案域名明细']；代表记录=10；calls[-:cloudmigration_cloud_assets=data；-:cloudmigration_domain_info=data(10/92)]
- **pass** 不输出原始嵌套 JSON：report.md/html 使用表格和文字字段展示，未输出原始嵌套 JSON 字符串。；本轮当前产物：technical=passed，successful_data_calls=2；subject.enterprise=小米科技有限责任公司，resolved=True；metrics[有效域名数=1427；子域名数=3602；上云资产等级=5000W以上；备案域名数=92；备案年份覆盖=1；最新备案年份=2025]；quality={'total_sections': 6, 'populated_sections': 6, 'empty_sections': 0, 'coverage_pct': 100}；非空章节=['云资产概况', '云支出占比', '云服务厂商记录', '备案年度趋势', '海外服务器字段', '备案域名明细']；代表记录=10；calls[-:cloudmigration_cloud_assets=data；-:cloudmigration_domain_info=data(10/92)]

## 离线浏览器检查

[Ego Lite 离线图表、页面溢出和脚本检查](browser-check.json)