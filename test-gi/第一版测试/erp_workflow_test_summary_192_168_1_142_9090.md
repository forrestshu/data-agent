# ERP Data Agent 测试汇总

本次共测试 210 条问题，通过 98 条，其中 ⚠️ 带警告通过 5 条；失败 112 条。

下面按照 Data Agent 结果质量的严重程度，将问题归并为 6 类。前 5 类计入失败，第 6 类为通过但需要关注的警告。

## 1. 视图查询错误

- 数量：2 条
- 案例：用例 6-1，查询描述为Q235钢板8的物料编码
- 期望：期望走 `Cux.AiQueryPartOnHandV`。
- 实际：实际命中 `[Cux].[AiQueryPartV]`，状态 `hit`，返回 1 行。
- 影响：视图选错会导致后续字段、数据口径和业务语义都不可靠，是 Data Agent 里优先级最高的问题。

## 2. 未查询到数据

- 数量：16 条
- 案例：用例 2-1，查询物料编码110000012的现有量
- 期望：期望状态 `hit`，命中 1 行。
- 实际：实际状态 `no_data`，返回 0 行。
- 影响：用户询问明确对象时返回无数据，会被理解为系统漏查或数据不可用。

## 3. 查到的数据错误

- 数量：52 条
- 案例：用例 3-1，查询项目号24M148-H的工单数量
- 期望：期望返回行能与 checklist 中的字段和值匹配。
- 实际：实际状态 `hit`，视图 `[Cux].[AiQueryJobV]`；返回样例：`JobCount=88` / `ProjectID=24M148-H`。
- 影响：视图和状态都看似正确，但关键业务数值或期望行错误，是最常见的结果质量问题。

## 4. 数据条数缺失

- 数量：4 条
- 案例：用例 1-6，查询编码1100000144的采购提前期
- 期望：期望返回 1 行。
- 实际：实际只返回 0 行。
- 影响：结果集不完整会让用户遗漏数据，尤其影响列表查询、导出和后续分析。

## 5. 数据条数过多

- 数量：38 条
- 案例：用例 1-4，查询编码1100000144的平均单价
- 期望：期望返回 1 行。
- 实际：实际返回 2 行；即使包含期望行也判失败。
- 影响：返回过多说明过滤条件没有收紧，会引入无关数据，降低答案可信度。

## 6. ⚠️ 字段不完整

- 数量：5 条
- 案例：用例 5-1，查询描述为齿条,M5L1200H50S75的采购订单号
- 期望：期望 checklist 中对应字段完整返回。
- 实际：实际已有字段和值匹配，但缺少字段：row_1_partial_match_missing_fields:PartNum。
- 影响：这类不计入失败，标记为 ⚠️ 警告通过；说明已有字段正确，但答案不够完整。

## 汇总表

| 严重程度 | 类型 | 数量 | 是否计入失败 |
| ---: | --- | ---: | --- |
| 1 | 视图查询错误 | 2 | 是 |
| 2 | 未查询到数据 | 16 | 是 |
| 3 | 查到的数据错误 | 52 | 是 |
| 4 | 数据条数缺失 | 4 | 是 |
| 5 | 数据条数过多 | 38 | 是 |
| 6 | ⚠️ 字段不完整 | 5 | 否，警告通过 |

## 各类型对应用例

### 视图查询错误

| 用例 | 视图 | 问题 | 关键标记 |
| --- | --- | --- | --- |
| 6-1 | `Cux.AiQueryPartOnHandV` | 查询描述为Q235钢板8的物料编码 | 期望 Cux.AiQueryPartOnHandV，实际 [Cux].[AiQueryPartV] |
| 6-4 | `Cux.AiQueryPartOnHandV` | 查询描述为20#无缝管Φ180x40的物料编码 | 期望 Cux.AiQueryPartOnHandV，实际 [Cux].[AiQueryPartV] |

### 未查询到数据

| 用例 | 视图 | 问题 | 关键标记 |
| --- | --- | --- | --- |
| 2-1 | `Cux.AiQueryPartOnHandV` | 查询物料编码110000012的现有量 | 期望 hit，实际 no_data；返回 0 行 |
| 2-2 | `Cux.AiQueryPartOnHandV` | 查询物料编码110000012的库位 | 期望 hit，实际 no_data；返回 0 行 |
| 2-3 | `Cux.AiQueryPartOnHandV` | 查询物料编码110000012的库位名称 | 期望 hit，实际 no_data；返回 0 行 |
| 2-7 | `Cux.AiQueryPartOnHandV` | 查询物料编码110000012有没有库存 | 期望 hit，实际 no_data；返回 0 行 |
| 2-8 | `Cux.AiQueryPartOnHandV` | 查询110000012当前库存数量是多少 | 期望 hit，实际 no_data；返回 0 行 |
| 2-10 | `Cux.AiQueryPartOnHandV` | 查询110000012的库存数量和库位名称 | 期望 hit，实际 no_data；返回 0 行 |
| 6-2 | `Cux.AiQueryPartOnHandV` | 查询描述为Q235钢板8的库位 | 期望 hit，实际 no_data；返回 0 行 |
| 6-3 | `Cux.AiQueryPartOnHandV` | 查询描述为Q235钢板8的库位名称 | 期望 hit，实际 no_data；返回 0 行 |
| 6-7 | `Cux.AiQueryPartOnHandV` | 查询描述包含钢板8的物料编码和库位 | 期望 hit，实际 no_data；返回 0 行 |
| 6-9 | `Cux.AiQueryPartOnHandV` | 查询Q235钢板8存放在哪个库位 | 期望 hit，实际 no_data；返回 0 行 |
| 8-1 | `Cux.AiQueryPartOnHandV` | 查询物料编码110000012的现有量 | 期望 hit，实际 no_data；返回 0 行 |
| 8-3 | `Cux.AiQueryPartOnHandV` | 查询物料描述Q235钢板8的现有量 | 期望 hit，实际 no_data；返回 0 行 |
| 8-5 | `Cux.AiQueryPartOnHandV` | 查询110000012当前库存有多少 | 期望 hit，实际 no_data；返回 0 行 |
| 8-7 | `Cux.AiQueryPartOnHandV` | 查询Q235钢板8库存数量 | 期望 hit，实际 no_data；返回 0 行 |
| 8-9 | `Cux.AiQueryPartOnHandV` | 查询编码110000012和描述Q235钢板8的现有量 | 期望 hit，实际 no_data；返回 0 行 |
| 18-7 | `Cux.AiQueryPartTimeTrackingV` | 查询211.181L-01-01-003-A在2026年4月8日的需求数量和余额 | 期望 hit，实际 no_data；返回 0 行 |

### 查到的数据错误

| 用例 | 视图 | 问题 | 关键标记 |
| --- | --- | --- | --- |
| 3-1 | `Cux.AiQueryJobV` | 查询项目号24M148-H的工单数量 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 3-4 | `Cux.AiQueryJobV` | 查询24M148-H共有多少张工单 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 3-5 | `Cux.AiQueryJobV` | 查询项目24M148-H最早合交期 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 3-6 | `Cux.AiQueryJobV` | 查询项目24M148-H最晚合交期 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 3-7 | `Cux.AiQueryJobV` | 查询项目号24M148-A的工单数量 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 3-10 | `Cux.AiQueryJobV` | 查询A240024的合交期 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 5-3 | `Cux.AiQueryPoProgressV` | 查询描述为齿条,M5L1200H50S75的下单时间和需求时间 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 5-7 | `Cux.AiQueryPoProgressV` | 查询描述为瓷管,φ30*φ24*500的下单时间 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 5-9 | `Cux.AiQueryPoProgressV` | 查询物料Z01.02.0026的采购到货进度 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 5-10 | `Cux.AiQueryPoProgressV` | 查询物料Z440300054的采购进度明细 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 11-3 | `Cux.AiQueryPoOverViewV` | 查询物料编码6206320的采购追踪信息 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 11-4 | `Cux.AiQueryPoOverViewV` | 查询描述为威图悬臂箱底座，A250063的采购追踪信息 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 11-5 | `Cux.AiQueryPoOverViewV` | 查询描述为施瓦茨项目悬臂使用底座的采购追踪信息 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 11-10 | `Cux.AiQueryPoOverViewV` | 查询供应商卡尔松（常州）电气有限公司在2026年1月的采购收货情况 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 13-2 | `Cux.AiQueryProjectJobV` | 查询项目24M148-H的工单完工数量 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 15-1 | `Cux.AiQuerySoOverViewV` | 查询销售订单293的订单日期和客户名称 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 15-3 | `Cux.AiQuerySoOverViewV` | 查询销售订单293的行金额和订单金额 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 15-4 | `Cux.AiQuerySoOverViewV` | 查询销售订单293的需求日期和发货数量 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 15-7 | `Cux.AiQuerySoOverViewV` | 查询销售订单782的订单日期和客户名称 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 15-8 | `Cux.AiQuerySoOverViewV` | 查询销售订单782的物料描述、订单数量和行金额 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 15-9 | `Cux.AiQuerySoOverViewV` | 查询销售订单782的发货数量和开票数量 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 15-10 | `Cux.AiQuerySoOverViewV` | 查询销售订单782的客户采购订单号、需求日期和货币代码 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 16-4 | `Cux.AiQueryProjectV` | 查询项目26M001-C-W的发货日期和验收日期 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 16-7 | `Cux.AiQueryProjectV` | 查询项目26M001-I-1-W的发货日期 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 16-10 | `Cux.AiQueryProjectV` | 查询项目26M001-C-W和26M001-I-1-W的发货日期 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 18-5 | `Cux.AiQueryPartTimeTrackingV` | 查询211.181L-01-01-003-A当前余额数量 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 18-8 | `Cux.AiQueryPartTimeTrackingV` | 查询图号211.181L-01-01-003-A的现存量 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 18-9 | `Cux.AiQueryPartTimeTrackingV` | 查询物料211.181L-01-01-003-A后续供需变化 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 19-1 | `Cux.AiQueryProjRevCstV` | 查询项目22149-2的发生成本 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 19-3 | `Cux.AiQueryProjRevCstV` | 查询项目22149-2的已结转成本和未结转成本 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 19-4 | `Cux.AiQueryProjRevCstV` | 查询项目22213的发生成本和已确认收入 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 19-5 | `Cux.AiQueryProjRevCstV` | 查询项目22213的已结转成本 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 19-7 | `Cux.AiQueryProjRevCstV` | 查询客户宁波金田铜管有限公司的项目成本和确认收入 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 19-8 | `Cux.AiQueryProjRevCstV` | 查询客户烟台孚信达双金属股份有限公司的项目收入成本情况 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 19-9 | `Cux.AiQueryProjRevCstV` | 查询项目22149-2的收入成本结转情况 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 20-3 | `Cux.AiQueryPayablesV` | 查询供应商上海影旗传动机械有限公司的累计金额 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 20-4 | `Cux.AiQueryPayablesV` | 查询供应商上海洪瀚流体控制设备有限公司的本币余额 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 20-5 | `Cux.AiQueryPayablesV` | 查询供应商上海洪瀚流体控制设备有限公司的原币余额 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 20-6 | `Cux.AiQueryPayablesV` | 查询供应商上海洪瀚流体控制设备有限公司的累计金额 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 20-7 | `Cux.AiQueryPayablesV` | 查询上海洪瀚流体控制设备有限公司的本币余额和原币余额 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 20-9 | `Cux.AiQueryPayablesV` | 查询供应商上海洪瀚流体控制设备有限公司的剩余应付金额 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 20-10 | `Cux.AiQueryPayablesV` | 查询上海影旗传动机械有限公司的累计金额和余额 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 21-1 | `Cux.AiQueryReceivablesV` | 查询客户江西江铜龙昌精密铜管有限公司的本币余额 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 21-2 | `Cux.AiQueryReceivablesV` | 查询客户江西江铜龙昌精密铜管有限公司的原币余额 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 21-3 | `Cux.AiQueryReceivablesV` | 查询客户江西江铜龙昌精密铜管有限公司的累计金额 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 21-4 | `Cux.AiQueryReceivablesV` | 查询客户金龙精密铜管集团股份有限公司的本币余额 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 21-5 | `Cux.AiQueryReceivablesV` | 查询客户金龙精密铜管集团股份有限公司的原币余额 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 21-6 | `Cux.AiQueryReceivablesV` | 查询客户金龙精密铜管集团股份有限公司的累计金额 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 21-7 | `Cux.AiQueryReceivablesV` | 查询江西江铜龙昌精密铜管有限公司的应收余额 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 21-8 | `Cux.AiQueryReceivablesV` | 查询金龙精密铜管集团股份有限公司的应收余额 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 21-9 | `Cux.AiQueryReceivablesV` | 查询江西江铜龙昌精密铜管有限公司的本币余额和原币余额 | 命中视图和状态，但关键字段值或期望行不匹配 |
| 21-10 | `Cux.AiQueryReceivablesV` | 查询金龙精密铜管集团股份有限公司的累计金额和余额 | 命中视图和状态，但关键字段值或期望行不匹配 |

### 数据条数缺失

| 用例 | 视图 | 问题 | 关键标记 |
| --- | --- | --- | --- |
| 1-6 | `Cux.AiQueryPoPriceV` | 查询编码1100000144的采购提前期 | 期望 1 行，实际 0 行 |
| 7-9 | `Cux.AiQueryPartV` | 通过部分编码1100000查询物料描述 | 期望 517 行，实际 200 行 |
| 18-3 | `Cux.AiQueryPartTimeTrackingV` | 查询211.181L-01-01-003-A的时间轴明细 | 期望 6 行，实际 5 行 |
| 18-4 | `Cux.AiQueryPartTimeTrackingV` | 查询211.181L-01-01-003-A的到货数量和需求数量 | 期望 6 行，实际 5 行 |

### 数据条数过多

| 用例 | 视图 | 问题 | 关键标记 |
| --- | --- | --- | --- |
| 1-4 | `Cux.AiQueryPoPriceV` | 查询编码1100000144的平均单价 | 期望 1 行，实际 2 行 |
| 1-5 | `Cux.AiQueryPoPriceV` | 查询编码1100000144的最新采购价 | 期望 1 行，实际 2 行 |
| 1-7 | `Cux.AiQueryPoPriceV` | 查询描述包含钢丝网的平均单价 | 期望 6 行，实际 110 行 |
| 1-8 | `Cux.AiQueryPoPriceV` | 查询描述包含钢丝网的最新采购价 | 期望 6 行，实际 110 行 |
| 1-10 | `Cux.AiQueryPoPriceV` | 查询描述包含雨布6500*4300的平均单价 | 期望 1 行，实际 2 行 |
| 3-2 | `Cux.AiQueryJobV` | 查询项目号24M148-H的合交期 | 期望 10 行，实际 88 行 |
| 3-3 | `Cux.AiQueryJobV` | 查询项目24M148-H有哪些工单 | 期望 10 行，实际 88 行 |
| 3-8 | `Cux.AiQueryJobV` | 查询项目24M148-A的合交期 | 期望 3 行，实际 26 行 |
| 4-4 | `Cux.AiQueryPartV` | 查询描述包含钢板的物料编码 | 期望 120 行，实际 200 行 |
| 4-5 | `Cux.AiQueryPartV` | 查询描述包含40Cr的物料编码 | 期望 20 行，实际 51 行 |
| 4-9 | `Cux.AiQueryPartV` | 描述里有钢板30的物料编码有哪些 | 期望 5 行，实际 6 行 |
| 6-8 | `Cux.AiQueryPartOnHandV` | 查询描述包含无缝管的物料编码和库位 | 期望 34 行，实际 72 行 |
| 7-6 | `Cux.AiQueryPartV` | 查询编码包含11000001的物料描述 | 期望 76 行，实际 77 行 |
| 7-10 | `Cux.AiQueryPartV` | 通过描述包含钢板查询物料编码 | 期望 120 行，实际 200 行 |
| 8-10 | `Cux.AiQueryPartOnHandV` | 查询描述包含无缝管的现有量 | 期望 34 行，实际 72 行 |
| 9-1 | `Cux.AiQueryBomV` | 查询物料编码6100002502用于哪个上级部件 | 期望 3 行，实际 20 行 |
| 9-2 | `Cux.AiQueryBomV` | 查询物料编码6100002529用于哪个上级部件 | 期望 4 行，实际 20 行 |
| 9-3 | `Cux.AiQueryBomV` | 查询描述包含KTP700 Basic的物料用于哪个部件 | 期望 3 行，实际 131 行 |
| 9-4 | `Cux.AiQueryBomV` | 查询描述包含CPU 1512C-1PN的物料用于哪个部件 | 期望 4 行，实际 110 行 |
| 9-5 | `Cux.AiQueryBomV` | 查询6100002502对应的上级部件名称 | 期望 3 行，实际 20 行 |
| 9-6 | `Cux.AiQueryBomV` | 查询6100002529的上级部件描述 | 期望 4 行，实际 20 行 |
| 9-7 | `Cux.AiQueryBomV` | 查询HMI这项物料属于哪个部件 | 期望 7 行，实际 200 行 |
| 9-8 | `Cux.AiQueryBomV` | 查询PLC这项物料属于哪个上级部件 | 期望 7 行，实际 200 行 |
| 9-9 | `Cux.AiQueryBomV` | 查询物料描述包含Siemens的子件用于哪个部件 | 期望 12 行，实际 200 行 |
| 9-10 | `Cux.AiQueryBomV` | 查询物料描述包含触摸式操作的物料用于哪个上级部件 | 期望 3 行，实际 151 行 |
| 11-7 | `Cux.AiQueryPoOverViewV` | 查询2025年12月29日下单的采购记录 | 期望 1 行，实际 200 行 |
| 11-8 | `Cux.AiQueryPoOverViewV` | 查询2026年1月8日下单的采购记录 | 期望 1 行，实际 200 行 |
| 14-1 | `Cux.AiQueryPartV` | 查询描述包含钢板的物料编码 | 期望 120 行，实际 200 行 |
| 14-2 | `Cux.AiQueryPartV` | 查询描述包含无缝管的物料编码 | 期望 175 行，实际 195 行 |
| 14-4 | `Cux.AiQueryPartV` | 查询描述包含40Cr的物料编码 | 期望 20 行，实际 51 行 |
| 14-5 | `Cux.AiQueryPartV` | 查询描述包含角钢的物料编码 | 期望 28 行，实际 71 行 |
| 14-6 | `Cux.AiQueryPartV` | 查询描述包含钢板30的物料是否存在 | 期望 5 行，实际 6 行 |
| 14-9 | `Cux.AiQueryPartV` | 模糊查找描述包含45#钢板的料号 | 期望 29 行，实际 30 行 |
| 14-10 | `Cux.AiQueryPartV` | 查询名称里带无缝管的物料编码列表 | 期望 175 行，实际 195 行 |
| 18-1 | `Cux.AiQueryPartTimeTrackingV` | 查询图号211.181L-01-01-003-A的库存计量单位和采购计量单位 | 期望 1 行，实际 5 行 |
| 18-2 | `Cux.AiQueryPartTimeTrackingV` | 查询物料181L-01-01-003-A_扇形盖板_发黑的库存计量单位和采购计量单位 | 期望 1 行，实际 5 行 |
| 18-6 | `Cux.AiQueryPartTimeTrackingV` | 查询扇形盖板_发黑的来源说明 | 期望 6 行，实际 10 行 |
| 18-10 | `Cux.AiQueryPartTimeTrackingV` | 查询211.181L-01-01-003-A的库存单位、采购单位和余额数量 | 期望 1 行，实际 5 行 |

### 字段不完整

| 用例 | 视图 | 问题 | 关键标记 |
| --- | --- | --- | --- |
| 5-1 | `Cux.AiQueryPoProgressV` | 查询描述为齿条,M5L1200H50S75的采购订单号 | row_1_partial_match_missing_fields:PartNum |
| 5-2 | `Cux.AiQueryPoProgressV` | 查询描述为齿条,M5L1200H50S75的供应商 | row_1_partial_match_missing_fields:PONum |
| 11-6 | `Cux.AiQueryPoOverViewV` | 查询供应商卡尔松（常州）电气有限公司的采购订单数量和收货数量 | row_1_partial_match_missing_fields:LineDesc；row_2_partial_match_missing_fields:LineDesc |
| 12-6 | `Cux.AiQueryPoOverViewV` | 查询采购订单300018845的订单进度和审批状态 | row_1_partial_match_missing_fields:OrderQty,ReceivedQty,InvoiceQty,RemainQty |
| 16-5 | `Cux.AiQueryProjectV` | 查询项目26M001-I-1-W的客户名称和项目机型 | row_1_partial_match_missing_fields:ProjectID |

## 结论

- 当前最需要优先处理的是视图查询错误、未查询到数据和查到的数据错误，这三类会直接影响用户对答案是否可信的判断。
- 数据条数缺失和数据条数过多属于结果范围控制问题：前者漏数据，后者带入无关数据，都会影响列表型查询质量。
- 字段不完整的用例暂不计失败，但建议作为答案完整性优化项跟进。
