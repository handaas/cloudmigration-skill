# cloudmigration-skill：已验收示例

本目录只展示 **6 个完全通过的真实正向场景**（最低要求4例）。

每例均为真实、非空、非缓存调用；技术检查、独立业务检查和离线浏览器检查全部通过。报告保持原实测字节，不把空数据、报错处理或仅生成页面计作通过。

| 场景 | 真实使用需求 | 报告 |
|---|---|---|
| [大型科技企业云资产画像](01-cloud-native-tech/README.md) | 请分析腾讯科技（深圳）有限公司的域名、CDN、IDC、云厂商和云用量线索。 | [HTML](01-cloud-native-tech/report.html) / [MD](01-cloud-native-tech/report.md) / [JSON](01-cloud-native-tech/report.json) |
| [电商平台云基础设施](02-ecommerce-cloud/README.md) | 请查看北京京东世纪贸易有限公司的上云资产和备案域名。 | [HTML](02-ecommerce-cloud/report.html) / [MD](02-ecommerce-cloud/report.md) / [JSON](02-ecommerce-cloud/report.json) |
| [制造企业数字基础设施](03-manufacturer-digital/README.md) | 请评估美的集团股份有限公司的云资产覆盖和备案域名数量。 | [HTML](03-manufacturer-digital/report.html) / [MD](03-manufacturer-digital/report.md) / [JSON](03-manufacturer-digital/report.json) |
| [金融机构云资产边界](04-bank-cloud-boundary/README.md) | 请查询招商银行股份有限公司的公开云资产，并注明不能据此判断的内容。 | [HTML](04-bank-cloud-boundary/report.html) / [MD](04-bank-cloud-boundary/report.md) / [JSON](04-bank-cloud-boundary/report.json) |
| [车企云资产画像](05-automaker-cloud/README.md) | 请分析比亚迪股份有限公司的备案域名和云服务商线索。 | [HTML](05-automaker-cloud/report.html) / [MD](05-automaker-cloud/report.md) / [JSON](05-automaker-cloud/report.json) |
| [消费电子企业云线索](06-consumer-electronics-cloud/README.md) | 请查看小米科技有限责任公司的上云情况和主要域名。 | [HTML](06-consumer-electronics-cloud/report.html) / [MD](06-consumer-electronics-cloud/report.md) / [JSON](06-consumer-electronics-cloud/report.json) |

- [逐例验收结果](results.json) · [业务复核](review.json) · [证据摘要](evidence-index.json)
- [完整测试记录](../test-records/live-replaced-20261027/README.md)仅用于审计，不属于可展示示例。
- 当前数据与结论限于原查询时点及公开样本；覆盖率不代表准确率或低风险。
