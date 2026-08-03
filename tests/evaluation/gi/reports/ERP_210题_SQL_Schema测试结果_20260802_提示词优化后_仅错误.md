# ERP 210 题 SQLite SQL Schema 测试结果

- 测试时间：2026-08-02T18:36:44+08:00
- 测试页面：`http://127.0.0.1:5174`
- 后端接口：`http://127.0.0.1:8001/api/query`
- 数据源：`sqlite_internal`（SQLite 本地快照）
- 基准答案：`docs/基准答案.md`
- 评分标准：`tests/evaluation/gi/reports/ERP_210题_SQL_Schema测试标准.md`
- 原始输出：`tests/evaluation/gi/results/ERP_210题_SQLite输出_20260802_提示词优化后.json`

## 结论

共测试 **210** 题，四项全部通过 **160** 题，通过率 **76.19%**；失败 **50** 题。共有 **14** 题触发 `DISTINCT` 缺失警告（警告本身不计失败）。

| 指标 | 通过 | 未通过 | 通过率 |
| --- | ---: | ---: | ---: |
| 视图 | 188 | 22 | 89.52% |
| 筛选条件 | 190 | 20 | 90.48% |
| 查询字段 | 188 | 22 | 89.52% |
| 其他关键字 | 195 | 15 | 92.86% |
| 四项全部通过 | 160 | 50 | 76.19% |

### 系统响应状态

| 状态 | 数量 |
| --- | ---: |
| `clarification_required` | 1 |
| `completed` | 208 |
| `query_failed` | 1 |

### 失败组合

| 未通过项目 | 题数 |
| --- | ---: |
| 查询字段 | 9 |
| 筛选条件 | 8 |
| 视图 | 7 |
| 其他关键字 | 6 |
| 查询字段+其他关键字 | 5 |
| 视图+筛选条件 | 5 |
| 视图+筛选条件+查询字段 | 5 |
| 视图+筛选条件+查询字段+其他关键字 | 2 |
| 视图+其他关键字 | 2 |
| 视图+查询字段 | 1 |

## 逐题未通过结果

本报告按要求隐藏全部通过题，只展示未通过题目的1、2、3、4对比。

| 题号 | 问题 | 状态 | 视图 | 筛选 | 字段 | 其他 | 总判定 |
| --- | --- | --- | :---: | :---: | :---: | :---: | :---: |
| 2.7 | 查询物料编码120000019有没有库存 | `completed` | ✅ | ✅ | ❌ | ❌ | ❌ |
| 3.1 | 查询项目号24M148-H的工单数量 | `completed` | ✅ | ✅ | ❌ | ❌ | ❌ |
| 3.4 | 查询24M148-H共有多少张工单 | `completed` | ✅ | ✅ | ❌ | ❌ | ❌ |
| 3.7 | 查询项目号24M148-A的工单数量 | `completed` | ✅ | ✅ | ✅ | ❌ | ❌ |
| 3.9 | 查询A240024对应的工单数量 | `completed` | ✅ | ✅ | ❌ | ❌ | ❌ |
| 5.1 | 查询描述为齿条,M5L1200H50S75的采购订单号 | `completed` | ❌ | ✅ | ✅ | ✅ | ❌ |
| 5.6 | 查询描述为瓷管,φ30*φ24*500的采购订单和供应商 | `query_failed` | ❌ | ❌ | ❌ | ❌ | ❌ |
| 8.7 | 查询GCr15圆钢Φ45库存数量 | `completed` | ✅ | ✅ | ❌ | ❌ | ❌ |
| 8.9 | 查询编码120000019和描述GCr15圆钢Φ45的现有量 | `completed` | ✅ | ❌ | ✅ | ✅ | ❌ |
| 9.2 | 查询物料编码6100002529用于哪个上级部件 | `completed` | ❌ | ❌ | ✅ | ✅⚠️ | ❌ |
| 9.5 | 查询6100002502对应的上级部件名称 | `completed` | ✅ | ❌ | ✅ | ✅⚠️ | ❌ |
| 9.8 | 查询PLC这项物料属于哪个上级部件 | `completed` | ✅ | ❌ | ✅ | ✅⚠️ | ❌ |
| 11.6 | 查询供应商卡尔松（常州）电气有限公司的采购订单数量和收货数量 | `completed` | ❌ | ❌ | ✅ | ✅ | ❌ |
| 11.7 | 查询2025年12月29日下单的采购记录 | `completed` | ❌ | ❌ | ❌ | ✅ | ❌ |
| 11.8 | 查询2026年1月8日下单的采购记录 | `completed` | ❌ | ❌ | ❌ | ✅ | ❌ |
| 11.10 | 查询供应商卡尔松（常州）电气有限公司在2026年1月的采购收货情况 | `completed` | ❌ | ❌ | ❌ | ✅ | ❌ |
| 12.7 | 查询300018332是否已审批 | `completed` | ✅ | ✅ | ✅ | ❌⚠️ | ❌ |
| 12.8 | 查询300018845是否已审批 | `completed` | ✅ | ✅ | ✅ | ❌⚠️ | ❌ |
| 13.7 | 查询项目24M148-A对应工单000032的完工数量 | `completed` | ❌ | ❌ | ❌ | ✅ | ❌ |
| 13.8 | 查询24M148-H是否全部完成 | `clarification_required` | ❌ | ❌ | ❌ | ❌ | ❌ |
| 13.9 | 查询24M148-A是否全部完成 | `completed` | ✅ | ✅ | ✅ | ❌ | ❌ |
| 15.8 | 查询销售订单782的物料描述、订单数量和行金额 | `completed` | ✅ | ✅ | ❌ | ✅ | ❌ |
| 16.9 | 查询26M001-I-1-W是否已验收 | `completed` | ✅ | ✅ | ✅ | ❌ | ❌ |
| 17.1 | 查询工单24M007-I-14的完工数量 | `completed` | ❌ | ✅ | ✅ | ✅ | ❌ |
| 17.2 | 查询工单WO019594的完工数量 | `completed` | ❌ | ✅ | ✅ | ✅ | ❌ |
| 17.3 | 查询24M007-I-14目前完成了多少 | `completed` | ❌ | ✅ | ✅ | ✅ | ❌ |
| 17.4 | 查询WO019594目前完成了多少 | `completed` | ❌ | ✅ | ✅ | ✅ | ❌ |
| 17.5 | 查询24M007-I-14的工单数量和完工数量 | `completed` | ❌ | ❌ | ✅ | ✅ | ❌ |
| 17.6 | 查询WO019594的工单数量和完工数量 | `completed` | ❌ | ✅ | ✅ | ✅ | ❌ |
| 17.7 | 查询24M007-I-14是否已经完工 | `completed` | ❌ | ✅ | ✅ | ❌ | ❌ |
| 17.8 | 查询WO019594是否已经完工 | `completed` | ❌ | ✅ | ✅ | ❌ | ❌ |
| 17.9 | 查询工单24M007-I-14对应部件的完工数量 | `completed` | ❌ | ✅ | ✅ | ✅ | ❌ |
| 17.10 | 查询工单WO019594对应部件的完工数量 | `completed` | ❌ | ✅ | ❌ | ✅ | ❌ |
| 18.2 | 查询物料181L-01-01-003-A_扇形盖板_发黑的库存计量单位和采购计量单位 | `completed` | ✅ | ❌ | ✅ | ✅⚠️ | ❌ |
| 18.3 | 查询211.181L-01-01-003-A的时间轴明细 | `completed` | ✅ | ✅ | ✅ | ❌ | ❌ |
| 18.5 | 查询211.181L-01-01-003-A当前余额数量 | `completed` | ✅ | ❌ | ✅ | ✅ | ❌ |
| 18.7 | 查询3010000978在2024年9月23日的需求数量和余额 | `completed` | ✅ | ❌ | ✅ | ✅ | ❌ |
| 18.8 | 查询图号211.181L-01-01-003-A的现存量 | `completed` | ❌ | ❌ | ❌ | ✅ | ❌ |
| 18.9 | 查询物料211.181L-01-01-003-A后续供需变化 | `completed` | ✅ | ❌ | ✅ | ✅ | ❌ |
| 18.10 | 查询211.181L-01-01-003-A的库存单位、采购单位和余额数量 | `completed` | ✅ | ❌ | ✅ | ✅ | ❌ |
| 20.6 | 查询供应商上海洪瀚流体控制设备有限公司的累计金额 | `completed` | ✅ | ✅ | ❌ | ✅ | ❌ |
| 20.8 | 查询上海影旗传动机械有限公司的应付余额 | `completed` | ✅ | ✅ | ❌ | ✅ | ❌ |
| 20.9 | 查询供应商上海洪瀚流体控制设备有限公司的剩余应付金额 | `completed` | ✅ | ✅ | ❌ | ✅ | ❌ |
| 20.10 | 查询上海影旗传动机械有限公司的累计金额和余额 | `completed` | ✅ | ✅ | ❌ | ✅ | ❌ |
| 21.3 | 查询客户江西江铜龙昌精密铜管有限公司的累计金额 | `completed` | ✅ | ✅ | ❌ | ✅ | ❌ |
| 21.5 | 查询客户金龙精密铜管集团股份有限公司的原币余额 | `completed` | ✅ | ✅ | ❌ | ✅ | ❌ |
| 21.7 | 查询江西江铜龙昌精密铜管有限公司的应收余额 | `completed` | ✅ | ✅ | ❌ | ✅ | ❌ |
| 21.8 | 查询金龙精密铜管集团股份有限公司的应收余额 | `completed` | ✅ | ✅ | ❌ | ✅ | ❌ |
| 21.9 | 查询江西江铜龙昌精密铜管有限公司的本币余额和原币余额 | `completed` | ❌ | ❌ | ✅ | ✅ | ❌ |
| 21.10 | 查询金龙精密铜管集团股份有限公司的累计金额和余额 | `completed` | ❌ | ❌ | ✅ | ✅ | ❌ |

## 未通过题 SQL 与判定依据

### 2.7 查询物料编码120000019有没有库存

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartNum = '120000019'`
3. 查询字段：`Qty`
4. 其他关键字内容：`SUM(Qty)`、`CASE WHEN SUM(Qty) > 0 THEN '是' ELSE '否' END`

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryPartOnHandV`
2. 筛选条件：`PartNum = '120000019'`
3. 查询字段：`PartNum`、`PartDescription`、`BinNum`、`BinName`、`Qty`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：❌ 正确结果要求 `Qty`；测试额外输出 `binname`、`binnum`、`partdescription`、`partnum`，这些普通字段使单值汇总产生分组或混合聚合，改变了答案粒度。
4. 其他关键字内容：❌ 正确结果要求 `SUM(Qty)`、`CASE WHEN SUM(Qty) > 0 THEN '是' ELSE '否' END`；测试结果为 空。错误原因：缺少或错误使用必需聚合；缺少或错误使用必需 CASE。

- 实际 SQLite SQL：`SELECT PartNum, PartDescription, BinNum, BinName, Qty FROM AiQueryPartOnHandV WHERE PartNum = ?`
- 参数：`["120000019"]`
- 未通过原因：附加输出字段改变结果粒度：binname, binnum, partdescription, partnum；缺少或错误使用必需聚合；缺少或错误使用必需 CASE

### 3.1 查询项目号24M148-H的工单数量

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：可选其一：`Cux.AiQueryJobV`、`Cux.AiQueryProjectJobV`
2. 筛选条件：`ProjectID = '24M148-H'`
3. 查询字段：`JobNum`
4. 其他关键字内容：`COUNT(DISTINCT JobNum)`

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryJobV`
2. 筛选条件：`ProjectID = '24M148-H'`
3. 查询字段：`COUNT(*) AS JobCount`
4. 其他关键字内容：`COUNT(*)`

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：❌ 正确结果要求 `JobNum`；测试输出为 `COUNT(*) AS JobCount`，缺少必需业务字段：`jobnum`。
4. 其他关键字内容：❌ 正确结果要求 `COUNT(DISTINCT JobNum)`；测试结果为 `COUNT(*)`。错误原因：缺少或错误使用必需聚合。

- 实际 SQLite SQL：`SELECT COUNT(*) AS JobCount FROM AiQueryJobV WHERE ProjectID = ?`
- 参数：`["24M148-H"]`
- 未通过原因：输出缺少字段：jobnum；缺少或错误使用必需聚合

### 3.4 查询24M148-H共有多少张工单

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryJobV`
2. 筛选条件：`ProjectID = '24M148-H'`
3. 查询字段：`JobNum`
4. 其他关键字内容：`COUNT(DISTINCT JobNum)`

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryJobV`
2. 筛选条件：`ProjectID = '24M148-H'`
3. 查询字段：`COUNT(*)`
4. 其他关键字内容：`COUNT(*)`

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：❌ 正确结果要求 `JobNum`；测试输出为 `COUNT(*)`，缺少必需业务字段：`jobnum`。
4. 其他关键字内容：❌ 正确结果要求 `COUNT(DISTINCT JobNum)`；测试结果为 `COUNT(*)`。错误原因：缺少或错误使用必需聚合。

- 实际 SQLite SQL：`SELECT COUNT(*) FROM AiQueryJobV WHERE ProjectID = ?`
- 参数：`["24M148-H"]`
- 未通过原因：输出缺少字段：jobnum；缺少或错误使用必需聚合

### 3.7 查询项目号24M148-A的工单数量

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryJobV`
2. 筛选条件：`ProjectID = '24M148-A'`
3. 查询字段：`JobNum`
4. 其他关键字内容：`COUNT(DISTINCT JobNum)`

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryJobV`
2. 筛选条件：`ProjectID = '24M148-A'`
3. 查询字段：`COUNT(JobNum) AS JobCount`
4. 其他关键字内容：`COUNT(JobNum)`

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：❌ 正确结果要求 `COUNT(DISTINCT JobNum)`；测试结果为 `COUNT(JobNum)`。错误原因：缺少或错误使用必需聚合。

- 实际 SQLite SQL：`SELECT COUNT(JobNum) AS JobCount FROM AiQueryJobV WHERE ProjectID = ?`
- 参数：`["24M148-A"]`
- 未通过原因：缺少或错误使用必需聚合

### 3.9 查询A240024对应的工单数量

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryJobV`
2. 筛选条件：`ProjectID = 'A240024'`
3. 查询字段：`JobNum`
4. 其他关键字内容：`COUNT(DISTINCT JobNum)`

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryJobV`
2. 筛选条件：`ProjectID = 'A240024'`
3. 查询字段：`COUNT(*) AS JobCount`
4. 其他关键字内容：`COUNT(*)`

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：❌ 正确结果要求 `JobNum`；测试输出为 `COUNT(*) AS JobCount`，缺少必需业务字段：`jobnum`。
4. 其他关键字内容：❌ 正确结果要求 `COUNT(DISTINCT JobNum)`；测试结果为 `COUNT(*)`。错误原因：缺少或错误使用必需聚合。

- 实际 SQLite SQL：`SELECT COUNT(*) AS JobCount FROM AiQueryJobV WHERE ProjectID = ?`
- 参数：`["A240024"]`
- 未通过原因：输出缺少字段：jobnum；缺少或错误使用必需聚合

### 5.1 查询描述为齿条,M5L1200H50S75的采购订单号

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryPoProgressV`
2. 筛选条件：`LineDesc = '齿条,M5L1200H50S75'`
3. 查询字段：`PONum`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryPoOverViewV`
2. 筛选条件：`LineDesc = '齿条,M5L1200H50S75'`
3. 查询字段：`PONum`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：❌ 正确结果只接受 `Cux.AiQueryPoProgressV`；测试实际使用 `AiQueryPoOverViewV`，不在允许范围内。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT PONum FROM AiQueryPoOverViewV WHERE LineDesc = ?`
- 参数：`["齿条,M5L1200H50S75"]`
- 未通过原因：视图应为 aiquerypoprogressv，实际为 aiquerypooverviewv

### 5.6 查询描述为瓷管,φ30*φ24*500的采购订单和供应商

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryPoProgressV`
2. 筛选条件：`LineDesc = '瓷管,φ30*φ24*500'`
3. 查询字段：`PONum`、`VendorName`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：未输出（系统状态：query_failed）
2. 筛选条件：未输出（系统状态：query_failed）
3. 查询字段：未输出（系统状态：query_failed）
4. 其他关键字内容：未输出（系统状态：query_failed）

#### 1、2、3、4 逐项对比

1. 视图：❌ 系统未返回可评测的 SQLite SQL，无法与正确结果对比。
2. 筛选条件：❌ 系统未返回可评测的 SQLite SQL，无法与正确结果对比。
3. 查询字段：❌ 系统未返回可评测的 SQLite SQL，无法与正确结果对比。
4. 其他关键字内容：❌ 系统未返回可评测的 SQLite SQL，无法与正确结果对比。

- 实际 SQLite SQL：—
- 参数：`[]`
- 未通过原因：query_failed：您的查询中涉及的物料规格在现有业务信息中暂时找不到对应的采购记录，因此无法为您呈现结果。 建议您改用更常见的物料名称或直接提供采购单号，重新发起查询。

### 8.7 查询GCr15圆钢Φ45库存数量

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartDescription = 'GCr15圆钢Φ45'`
3. 查询字段：`Qty`
4. 其他关键字内容：`SUM(Qty)`

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryPartOnHandV`
2. 筛选条件：`PartDescription = 'GCr15圆钢Φ45'`
3. 查询字段：`PartNum`、`PartDescription`、`BinNum`、`BinName`、`Qty`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：❌ 正确结果要求 `Qty`；测试额外输出 `binname`、`binnum`、`partdescription`、`partnum`，这些普通字段使单值汇总产生分组或混合聚合，改变了答案粒度。
4. 其他关键字内容：❌ 正确结果要求 `SUM(Qty)`；测试结果为 空。错误原因：缺少或错误使用必需聚合。

- 实际 SQLite SQL：`SELECT PartNum, PartDescription, BinNum, BinName, Qty FROM AiQueryPartOnHandV WHERE PartDescription = ?`
- 参数：`["GCr15圆钢Φ45"]`
- 未通过原因：附加输出字段改变结果粒度：binname, binnum, partdescription, partnum；缺少或错误使用必需聚合

### 8.9 查询编码120000019和描述GCr15圆钢Φ45的现有量

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartNum = '120000019' AND PartDescription = 'GCr15圆钢Φ45'`
3. 查询字段：`Qty`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryPartOnHandV`
2. 筛选条件：`(PartNum = '120000019' OR PartDescription = 'GCr15圆钢Φ45')`
3. 查询字段：`PartNum`、`PartDescription`、`BinNum`、`BinName`、`Qty`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：❌ 正确筛选为 `PartNum = '120000019' AND PartDescription = 'GCr15圆钢Φ45'`；测试筛选为 `(PartNum = '120000019' OR PartDescription = 'GCr15圆钢Φ45')`。字段、运算符、筛选值或业务范围不等价。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT PartNum, PartDescription, BinNum, BinName, Qty FROM AiQueryPartOnHandV WHERE (PartNum = ? OR PartDescription = ?)`
- 参数：`["120000019", "GCr15圆钢Φ45"]`
- 未通过原因：筛选条件的字段、运算符、值或查询范围与标准不一致

### 9.2 查询物料编码6100002529用于哪个上级部件

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryBomV`
2. 筛选条件：`ECOMtl_MtlPartNum = '6100002529'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：`DISTINCT`

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryBomV`、`AiQueryPartV`
2. 筛选条件：`Company IN (SELECT DISTINCT Company FROM AiQueryPartV WHERE PartNum = '6100002529') AND ECOMtl_MtlPartNum = '6100002529'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：❌ 正确结果只接受 `Cux.AiQueryBomV`；测试实际使用 `AiQueryBomV`、`AiQueryPartV`，不在允许范围内。
2. 筛选条件：❌ 正确筛选为 `ECOMtl_MtlPartNum = '6100002529'`；测试筛选为 `Company IN (SELECT DISTINCT Company FROM AiQueryPartV WHERE PartNum = '6100002529') AND ECOMtl_MtlPartNum = '6100002529'`。字段、运算符、筛选值或业务范围不等价。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。 ⚠️ 测试缺少 `DISTINCT`；按测试标准本项仍通过，但存在重复记录风险。

- 实际 SQLite SQL：`SELECT PartNum, PartDescription FROM AiQueryBomV WHERE Company IN (SELECT DISTINCT Company FROM AiQueryPartV WHERE PartNum = ?) AND ECOMtl_MtlPartNum = ?`
- 参数：`["6100002529", "6100002529"]`
- 未通过原因：视图应为 aiquerybomv，实际为 aiquerybomv/aiquerypartv；筛选条件的字段、运算符、值或查询范围与标准不一致
- 警告：标准要求 DISTINCT，但实际未使用；按标准不判错，可能产生重复记录

### 9.5 查询6100002502对应的上级部件名称

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryBomV`
2. 筛选条件：`ECOMtl_MtlPartNum = '6100002502'`
3. 查询字段：`PartDescription`
4. 其他关键字内容：`DISTINCT`

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryBomV`
2. 筛选条件：`ECOMtl_MtlPartNum = '6100002502' AND NOT PartDescription IS NULL`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：❌ 正确筛选为 `ECOMtl_MtlPartNum = '6100002502'`；测试筛选为 `ECOMtl_MtlPartNum = '6100002502' AND NOT PartDescription IS NULL`。字段、运算符、筛选值或业务范围不等价。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。 ⚠️ 测试缺少 `DISTINCT`；按测试标准本项仍通过，但存在重复记录风险。

- 实际 SQLite SQL：`SELECT PartNum, PartDescription FROM AiQueryBomV WHERE ECOMtl_MtlPartNum = ? AND NOT PartDescription IS NULL`
- 参数：`["6100002502"]`
- 未通过原因：筛选条件的字段、运算符、值或查询范围与标准不一致
- 警告：标准要求 DISTINCT，但实际未使用；按标准不判错，可能产生重复记录

### 9.8 查询PLC这项物料属于哪个上级部件

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryBomV`
2. 筛选条件：`MtlPartDescription LIKE '%PLC%'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：`DISTINCT`

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryBomV`
2. 筛选条件：`MtlPartDescription = 'PLC'`
3. 查询字段：`PartNum`、`PartDescription`、`ECOMtl_MtlPartNum`、`MtlPartDescription`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：❌ 正确筛选为 `MtlPartDescription LIKE '%PLC%'`；测试筛选为 `MtlPartDescription = 'PLC'`。字段、运算符、筛选值或业务范围不等价。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。 ⚠️ 测试缺少 `DISTINCT`；按测试标准本项仍通过，但存在重复记录风险。

- 实际 SQLite SQL：`SELECT PartNum, PartDescription, ECOMtl_MtlPartNum, MtlPartDescription FROM AiQueryBomV WHERE MtlPartDescription = ?`
- 参数：`["PLC"]`
- 未通过原因：筛选条件的字段、运算符、值或查询范围与标准不一致
- 警告：标准要求 DISTINCT，但实际未使用；按标准不判错，可能产生重复记录

### 11.6 查询供应商卡尔松（常州）电气有限公司的采购订单数量和收货数量

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`Vendor_Name = '卡尔松（常州）电气有限公司'`
3. 查询字段：`OrderQty`、`ReceivedQty`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryPoProgressV`
2. 筛选条件：`VendorName = '卡尔松（常州）电气有限公司'`
3. 查询字段：`PONum`、`PartNum`、`LineDesc`、`OrderQty`、`ReceivedQty`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：❌ 正确结果只接受 `Cux.AiQueryPoOverViewV`；测试实际使用 `AiQueryPoProgressV`，不在允许范围内。
2. 筛选条件：❌ 正确筛选为 `Vendor_Name = '卡尔松（常州）电气有限公司'`；测试筛选为 `VendorName = '卡尔松（常州）电气有限公司'`。字段、运算符、筛选值或业务范围不等价。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT PONum, PartNum, LineDesc, OrderQty, ReceivedQty FROM AiQueryPoProgressV WHERE VendorName = ?`
- 参数：`["卡尔松（常州）电气有限公司"]`
- 未通过原因：视图应为 aiquerypooverviewv，实际为 aiquerypoprogressv；筛选条件的字段、运算符、值或查询范围与标准不一致

### 11.7 查询2025年12月29日下单的采购记录

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`OrderDate >= '2025-12-29' AND OrderDate < '2025-12-30'`
3. 查询字段：`PONum`、`OrderQty`、`ReceivedQty`、`InvoiceQty`、`RemainQty`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryPoProgressV`
2. 筛选条件：`OrderDate = '2025-12-29'`
3. 查询字段：`PONum`、`PartNum`、`LineDesc`、`VendorName`、`OrderDate`、`OrderQty`、`ReceivedQty`、`NetReceivedQty`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：❌ 正确结果只接受 `Cux.AiQueryPoOverViewV`；测试实际使用 `AiQueryPoProgressV`，不在允许范围内。
2. 筛选条件：❌ 正确筛选为 `OrderDate >= '2025-12-29' AND OrderDate < '2025-12-30'`；测试筛选为 `OrderDate = '2025-12-29'`。字段、运算符、筛选值或业务范围不等价。
3. 查询字段：❌ 正确结果要求 `PONum`、`OrderQty`、`ReceivedQty`、`InvoiceQty`、`RemainQty`；测试输出为 `PONum`、`PartNum`、`LineDesc`、`VendorName`、`OrderDate`、`OrderQty`、`ReceivedQty`、`NetReceivedQty`，缺少必需业务字段：`invoiceqty`、`remainqty`。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT PONum, PartNum, LineDesc, VendorName, OrderDate, OrderQty, ReceivedQty, NetReceivedQty FROM AiQueryPoProgressV WHERE OrderDate = ?`
- 参数：`["2025-12-29"]`
- 未通过原因：视图应为 aiquerypooverviewv，实际为 aiquerypoprogressv；筛选条件的字段、运算符、值或查询范围与标准不一致；输出缺少字段：invoiceqty, remainqty

### 11.8 查询2026年1月8日下单的采购记录

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`OrderDate >= '2026-01-08' AND OrderDate < '2026-01-09'`
3. 查询字段：`PONum`、`OrderQty`、`ReceivedQty`、`InvoiceQty`、`RemainQty`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryPoProgressV`
2. 筛选条件：`OrderDate = '2026-01-08'`
3. 查询字段：`PONum`、`PartNum`、`LineDesc`、`VendorName`、`OrderDate`、`OrderQty`、`DueDate`、`ReceivedQty`、`InspectionQty`、`NetReceivedQty`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：❌ 正确结果只接受 `Cux.AiQueryPoOverViewV`；测试实际使用 `AiQueryPoProgressV`，不在允许范围内。
2. 筛选条件：❌ 正确筛选为 `OrderDate >= '2026-01-08' AND OrderDate < '2026-01-09'`；测试筛选为 `OrderDate = '2026-01-08'`。字段、运算符、筛选值或业务范围不等价。
3. 查询字段：❌ 正确结果要求 `PONum`、`OrderQty`、`ReceivedQty`、`InvoiceQty`、`RemainQty`；测试输出为 `PONum`、`PartNum`、`LineDesc`、`VendorName`、`OrderDate`、`OrderQty`、`DueDate`、`ReceivedQty`、`InspectionQty`、`NetReceivedQty`，缺少必需业务字段：`invoiceqty`、`remainqty`。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT PONum, PartNum, LineDesc, VendorName, OrderDate, OrderQty, DueDate, ReceivedQty, InspectionQty, NetReceivedQty FROM AiQueryPoProgressV WHERE OrderDate = ?`
- 参数：`["2026-01-08"]`
- 未通过原因：视图应为 aiquerypooverviewv，实际为 aiquerypoprogressv；筛选条件的字段、运算符、值或查询范围与标准不一致；输出缺少字段：invoiceqty, remainqty

### 11.10 查询供应商卡尔松（常州）电气有限公司在2026年1月的采购收货情况

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`Vendor_Name = '卡尔松（常州）电气有限公司' AND OrderDate >= '2026-01-01' AND OrderDate < '2026-02-01'`
3. 查询字段：`OrderQty`、`ReceivedQty`、`InvoiceQty`、`RemainQty`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryPoProgressV`
2. 筛选条件：`VendorName = '卡尔松（常州）电气有限公司' AND OrderDate LIKE '%2026-01%' ESCAPE '\'`
3. 查询字段：`PONum`、`PartNum`、`LineDesc`、`VendorName`、`OrderDate`、`DueDate`、`OrderQty`、`ReceivedQty`、`InspectionQty`、`NetReceivedQty`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：❌ 正确结果只接受 `Cux.AiQueryPoOverViewV`；测试实际使用 `AiQueryPoProgressV`，不在允许范围内。
2. 筛选条件：❌ 正确筛选为 `Vendor_Name = '卡尔松（常州）电气有限公司' AND OrderDate >= '2026-01-01' AND OrderDate < '2026-02-01'`；测试筛选为 `VendorName = '卡尔松（常州）电气有限公司' AND OrderDate LIKE '%2026-01%' ESCAPE '\'`。字段、运算符、筛选值或业务范围不等价。
3. 查询字段：❌ 正确结果要求 `OrderQty`、`ReceivedQty`、`InvoiceQty`、`RemainQty`；测试输出为 `PONum`、`PartNum`、`LineDesc`、`VendorName`、`OrderDate`、`DueDate`、`OrderQty`、`ReceivedQty`、`InspectionQty`、`NetReceivedQty`，缺少必需业务字段：`invoiceqty`、`remainqty`。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT PONum, PartNum, LineDesc, VendorName, OrderDate, DueDate, OrderQty, ReceivedQty, InspectionQty, NetReceivedQty FROM AiQueryPoProgressV WHERE VendorName = ? AND OrderDate LIKE ? ESCAPE '\'`
- 参数：`["卡尔松（常州）电气有限公司", "%2026-01%"]`
- 未通过原因：视图应为 aiquerypooverviewv，实际为 aiquerypoprogressv；筛选条件的字段、运算符、值或查询范围与标准不一致；输出缺少字段：invoiceqty, remainqty

### 12.7 查询300018332是否已审批

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`PONum = 300018332`
3. 查询字段：`ApproveStatus_c`
4. 其他关键字内容：`DISTINCT`、`CASE WHEN ApproveStatus_c = 'Approved' THEN '是' ELSE '否' END`

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryPoOverViewV`
2. 筛选条件：`PONum = 300018332`
3. 查询字段：`PONum`、`ApproveStatus_c`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：❌ 正确结果要求 `DISTINCT`、`CASE WHEN ApproveStatus_c = 'Approved' THEN '是' ELSE '否' END`；测试结果为 空。错误原因：缺少或错误使用必需 CASE。 ⚠️ 测试缺少 `DISTINCT`；按测试标准本项仍通过，但存在重复记录风险。

- 实际 SQLite SQL：`SELECT PONum, ApproveStatus_c FROM AiQueryPoOverViewV WHERE PONum = ?`
- 参数：`[300018332]`
- 未通过原因：缺少或错误使用必需 CASE
- 警告：标准要求 DISTINCT，但实际未使用；按标准不判错，可能产生重复记录

### 12.8 查询300018845是否已审批

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`PONum = 300018845`
3. 查询字段：`ApproveStatus_c`
4. 其他关键字内容：`DISTINCT`、`CASE WHEN ApproveStatus_c = 'Approved' THEN '是' ELSE '否' END`

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryPoOverViewV`
2. 筛选条件：`PONum = 300018845`
3. 查询字段：`PONum`、`ApproveStatus_c`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：❌ 正确结果要求 `DISTINCT`、`CASE WHEN ApproveStatus_c = 'Approved' THEN '是' ELSE '否' END`；测试结果为 空。错误原因：缺少或错误使用必需 CASE。 ⚠️ 测试缺少 `DISTINCT`；按测试标准本项仍通过，但存在重复记录风险。

- 实际 SQLite SQL：`SELECT PONum, ApproveStatus_c FROM AiQueryPoOverViewV WHERE PONum = ?`
- 参数：`[300018845]`
- 未通过原因：缺少或错误使用必需 CASE
- 警告：标准要求 DISTINCT，但实际未使用；按标准不判错，可能产生重复记录

### 13.7 查询项目24M148-A对应工单000032的完工数量

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryProjectJobV`
2. 筛选条件：`ProjectID = '24M148-A' AND JobHead_JobNum = '000032'`
3. 查询字段：`CompleteQty`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryJobProgressV`、`AiQueryJobV`
2. 筛选条件：`JobNum = '000032' AND Company IN (SELECT Company FROM AiQueryJobV WHERE ProjectID = '24M148-A' AND JobNum = '000032')`
3. 查询字段：`JobOprCompQty`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：❌ 正确结果只接受 `Cux.AiQueryProjectJobV`；测试实际使用 `AiQueryJobProgressV`、`AiQueryJobV`，不在允许范围内。
2. 筛选条件：❌ 正确筛选为 `ProjectID = '24M148-A' AND JobHead_JobNum = '000032'`；测试筛选为 `JobNum = '000032' AND Company IN (SELECT Company FROM AiQueryJobV WHERE ProjectID = '24M148-A' AND JobNum = '000032')`。字段、运算符、筛选值或业务范围不等价。
3. 查询字段：❌ 正确结果要求 `CompleteQty`；测试输出为 `JobOprCompQty`，缺少必需业务字段：`completeqty`。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT JobOprCompQty FROM AiQueryJobProgressV WHERE JobNum = ? AND Company IN (SELECT Company FROM AiQueryJobV WHERE ProjectID = ? AND JobNum = ?)`
- 参数：`["000032", "24M148-A", "000032"]`
- 未通过原因：视图应为 aiqueryprojectjobv，实际为 aiqueryjobprogressv/aiqueryjobv；筛选条件的字段、运算符、值或查询范围与标准不一致；输出缺少字段：completeqty

### 13.8 查询24M148-H是否全部完成

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryProjectJobV`
2. 筛选条件：`ProjectID = '24M148-H'`
3. 查询字段：`JobHead_ProdQty`、`CompleteQty`
4. 其他关键字内容：`COUNT(*)`、`MIN(CASE WHEN CompleteQty >= JobHead_ProdQty AND JobHead_ProdQty > 0 THEN 1 ELSE 0 END)`、`CASE WHEN COUNT(*) > 0 AND MIN(...) = 1 THEN '是' ELSE '否' END`

#### 测试结果的 1、2、3、4

1. 视图：未输出（系统状态：clarification_required）
2. 筛选条件：未输出（系统状态：clarification_required）
3. 查询字段：未输出（系统状态：clarification_required）
4. 其他关键字内容：未输出（系统状态：clarification_required）

#### 1、2、3、4 逐项对比

1. 视图：❌ 系统未返回可评测的 SQLite SQL，无法与正确结果对比。
2. 筛选条件：❌ 系统未返回可评测的 SQLite SQL，无法与正确结果对比。
3. 查询字段：❌ 系统未返回可评测的 SQLite SQL，无法与正确结果对比。
4. 其他关键字内容：❌ 系统未返回可评测的 SQLite SQL，无法与正确结果对比。

- 实际 SQLite SQL：—
- 参数：`[]`
- 未通过原因：clarification_required：请确认“全部完成”的判定口径：以项目下工单的完工入库数量(CompleteQty)等于生产数量(JobHead_ProdQty)为准，还是以工单末道工序完成数量(JobOprCompQty)等于工单数量(JobQty)为准？

### 13.9 查询24M148-A是否全部完成

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryProjectJobV`
2. 筛选条件：`ProjectID = '24M148-A'`
3. 查询字段：`JobHead_ProdQty`、`CompleteQty`
4. 其他关键字内容：`COUNT(*)`、`MIN(CASE WHEN CompleteQty >= JobHead_ProdQty AND JobHead_ProdQty > 0 THEN 1 ELSE 0 END)`、`CASE WHEN COUNT(*) > 0 AND MIN(...) = 1 THEN '是' ELSE '否' END`

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryProjectJobV`
2. 筛选条件：`ProjectID = '24M148-A'`
3. 查询字段：`SUM(CompleteQty) AS TotalCompleteQty`、`SUM(JobHead_ProdQty) AS TotalPlanQty`
4. 其他关键字内容：`SUM(CompleteQty)`、`SUM(JobHead_ProdQty)`

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：❌ 正确结果要求 `COUNT(*)`、`MIN(CASE WHEN CompleteQty >= JobHead_ProdQty AND JobHead_ProdQty > 0 THEN 1 ELSE 0 END)`、`CASE WHEN COUNT(*) > 0 AND MIN(...) = 1 THEN '是' ELSE '否' END`；测试结果为 `SUM(CompleteQty)`、`SUM(JobHead_ProdQty)`。错误原因：缺少或错误使用必需聚合；缺少或错误使用必需 CASE。

- 实际 SQLite SQL：`SELECT SUM(CompleteQty) AS TotalCompleteQty, SUM(JobHead_ProdQty) AS TotalPlanQty FROM AiQueryProjectJobV WHERE ProjectID = ?`
- 参数：`["24M148-A"]`
- 未通过原因：缺少或错误使用必需聚合；缺少或错误使用必需 CASE

### 15.8 查询销售订单782的物料描述、订单数量和行金额

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQuerySoOverViewV`
2. 筛选条件：`OrderNum = 782`
3. 查询字段：`LineDesc`、`OrderQty`、`DocLineAmount`、`LineAmount`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQuerySoOverViewV`
2. 筛选条件：`OrderNum = 782`
3. 查询字段：`LineDesc`、`OrderQty`、`LineAmount`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：❌ 正确结果要求 `LineDesc`、`OrderQty`、`DocLineAmount`、`LineAmount`；测试输出为 `LineDesc`、`OrderQty`、`LineAmount`，缺少必需业务字段：`doclineamount`。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT LineDesc, OrderQty, LineAmount FROM AiQuerySoOverViewV WHERE OrderNum = ?`
- 参数：`[782]`
- 未通过原因：输出缺少字段：doclineamount

### 16.9 查询26M001-I-1-W是否已验收

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryProjectV`
2. 筛选条件：`ProjectID = '26M001-I-1-W'`
3. 查询字段：`Checkdate`
4. 其他关键字内容：`CASE WHEN Checkdate IS NULL THEN '否' ELSE '是' END`

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryProjectV`
2. 筛选条件：`ProjectID = '26M001-I-1-W'`
3. 查询字段：`ProjectID`、`ProjectStatus`、`Checkdate`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：❌ 正确结果要求 `CASE WHEN Checkdate IS NULL THEN '否' ELSE '是' END`；测试结果为 空。错误原因：缺少或错误使用必需 CASE。

- 实际 SQLite SQL：`SELECT ProjectID, ProjectStatus, Checkdate FROM AiQueryProjectV WHERE ProjectID = ?`
- 参数：`["26M001-I-1-W"]`
- 未通过原因：缺少或错误使用必需 CASE

### 17.1 查询工单24M007-I-14的完工数量

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryJobTrackingV`
2. 筛选条件：`JobNum = '24M007-I-14'`
3. 查询字段：`JobOprCompQty`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryJobProgressV`
2. 筛选条件：`JobNum = '24M007-I-14'`
3. 查询字段：`JobNum`、`JobOprCompQty`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：❌ 正确结果只接受 `Cux.AiQueryJobTrackingV`；测试实际使用 `AiQueryJobProgressV`，不在允许范围内。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT JobNum, JobOprCompQty FROM AiQueryJobProgressV WHERE JobNum = ?`
- 参数：`["24M007-I-14"]`
- 未通过原因：视图应为 aiqueryjobtrackingv，实际为 aiqueryjobprogressv

### 17.2 查询工单WO019594的完工数量

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryJobTrackingV`
2. 筛选条件：`JobNum = 'WO019594'`
3. 查询字段：`JobOprCompQty`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryJobProgressV`
2. 筛选条件：`JobNum = 'WO019594'`
3. 查询字段：`JobNum`、`JobOprCompQty`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：❌ 正确结果只接受 `Cux.AiQueryJobTrackingV`；测试实际使用 `AiQueryJobProgressV`，不在允许范围内。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT JobNum, JobOprCompQty FROM AiQueryJobProgressV WHERE JobNum = ?`
- 参数：`["WO019594"]`
- 未通过原因：视图应为 aiqueryjobtrackingv，实际为 aiqueryjobprogressv

### 17.3 查询24M007-I-14目前完成了多少

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryJobTrackingV`
2. 筛选条件：`JobNum = '24M007-I-14'`
3. 查询字段：`JobOprCompQty`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryJobProgressV`
2. 筛选条件：`JobNum = '24M007-I-14'`
3. 查询字段：`JobOprCompQty`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：❌ 正确结果只接受 `Cux.AiQueryJobTrackingV`；测试实际使用 `AiQueryJobProgressV`，不在允许范围内。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT JobOprCompQty FROM AiQueryJobProgressV WHERE JobNum = ?`
- 参数：`["24M007-I-14"]`
- 未通过原因：视图应为 aiqueryjobtrackingv，实际为 aiqueryjobprogressv

### 17.4 查询WO019594目前完成了多少

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryJobTrackingV`
2. 筛选条件：`JobNum = 'WO019594'`
3. 查询字段：`JobOprCompQty`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryJobProgressV`
2. 筛选条件：`JobNum = 'WO019594'`
3. 查询字段：`JobNum`、`JobOprCompQty`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：❌ 正确结果只接受 `Cux.AiQueryJobTrackingV`；测试实际使用 `AiQueryJobProgressV`，不在允许范围内。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT JobNum, JobOprCompQty FROM AiQueryJobProgressV WHERE JobNum = ?`
- 参数：`["WO019594"]`
- 未通过原因：视图应为 aiqueryjobtrackingv，实际为 aiqueryjobprogressv

### 17.5 查询24M007-I-14的工单数量和完工数量

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryJobTrackingV`
2. 筛选条件：`JobNum = '24M007-I-14'`
3. 查询字段：`JobQty`、`JobOprCompQty`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryJobProgressV`
2. 筛选条件：`PartNum LIKE '%24M007-I-14%' ESCAPE '\'`
3. 查询字段：`JobNum`、`JobQty`、`JobOprCompQty`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：❌ 正确结果只接受 `Cux.AiQueryJobTrackingV`；测试实际使用 `AiQueryJobProgressV`，不在允许范围内。
2. 筛选条件：❌ 正确筛选为 `JobNum = '24M007-I-14'`；测试筛选为 `PartNum LIKE '%24M007-I-14%' ESCAPE '\'`。字段、运算符、筛选值或业务范围不等价。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT JobNum, JobQty, JobOprCompQty FROM AiQueryJobProgressV WHERE PartNum LIKE ? ESCAPE '\'`
- 参数：`["%24M007-I-14%"]`
- 未通过原因：视图应为 aiqueryjobtrackingv，实际为 aiqueryjobprogressv；筛选条件的字段、运算符、值或查询范围与标准不一致

### 17.6 查询WO019594的工单数量和完工数量

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryJobTrackingV`
2. 筛选条件：`JobNum = 'WO019594'`
3. 查询字段：`JobQty`、`JobOprCompQty`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryJobProgressV`
2. 筛选条件：`JobNum = 'WO019594'`
3. 查询字段：`JobNum`、`JobQty`、`JobOprCompQty`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：❌ 正确结果只接受 `Cux.AiQueryJobTrackingV`；测试实际使用 `AiQueryJobProgressV`，不在允许范围内。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT JobNum, JobQty, JobOprCompQty FROM AiQueryJobProgressV WHERE JobNum = ?`
- 参数：`["WO019594"]`
- 未通过原因：视图应为 aiqueryjobtrackingv，实际为 aiqueryjobprogressv

### 17.7 查询24M007-I-14是否已经完工

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryJobTrackingV`
2. 筛选条件：`JobNum = '24M007-I-14'`
3. 查询字段：`JobQty`、`JobOprCompQty`
4. 其他关键字内容：`CASE WHEN JobOprCompQty >= JobQty AND JobQty > 0 THEN '是' ELSE '否' END`

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryJobProgressV`
2. 筛选条件：`JobNum = '24M007-I-14'`
3. 查询字段：`JobNum`、`PartNum`、`PartDescription`、`JobQty`、`JobOprCompQty`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：❌ 正确结果只接受 `Cux.AiQueryJobTrackingV`；测试实际使用 `AiQueryJobProgressV`，不在允许范围内。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：❌ 正确结果要求 `CASE WHEN JobOprCompQty >= JobQty AND JobQty > 0 THEN '是' ELSE '否' END`；测试结果为 空。错误原因：缺少或错误使用必需 CASE。

- 实际 SQLite SQL：`SELECT JobNum, PartNum, PartDescription, JobQty, JobOprCompQty FROM AiQueryJobProgressV WHERE JobNum = ?`
- 参数：`["24M007-I-14"]`
- 未通过原因：视图应为 aiqueryjobtrackingv，实际为 aiqueryjobprogressv；缺少或错误使用必需 CASE

### 17.8 查询WO019594是否已经完工

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryJobTrackingV`
2. 筛选条件：`JobNum = 'WO019594'`
3. 查询字段：`JobQty`、`JobOprCompQty`
4. 其他关键字内容：`CASE WHEN JobOprCompQty >= JobQty AND JobQty > 0 THEN '是' ELSE '否' END`

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryJobProgressV`
2. 筛选条件：`JobNum = 'WO019594'`
3. 查询字段：`JobNum`、`JobQty`、`JobOprCompQty`、`LaborQty`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：❌ 正确结果只接受 `Cux.AiQueryJobTrackingV`；测试实际使用 `AiQueryJobProgressV`，不在允许范围内。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：❌ 正确结果要求 `CASE WHEN JobOprCompQty >= JobQty AND JobQty > 0 THEN '是' ELSE '否' END`；测试结果为 空。错误原因：缺少或错误使用必需 CASE。

- 实际 SQLite SQL：`SELECT JobNum, JobQty, JobOprCompQty, LaborQty FROM AiQueryJobProgressV WHERE JobNum = ?`
- 参数：`["WO019594"]`
- 未通过原因：视图应为 aiqueryjobtrackingv，实际为 aiqueryjobprogressv；缺少或错误使用必需 CASE

### 17.9 查询工单24M007-I-14对应部件的完工数量

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryJobTrackingV`
2. 筛选条件：`JobNum = '24M007-I-14'`
3. 查询字段：`PartNum`、`PartDescription`、`JobOprCompQty`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryJobProgressV`
2. 筛选条件：`JobNum = '24M007-I-14'`
3. 查询字段：`PartNum`、`PartDescription`、`JobQty`、`JobOprCompQty`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：❌ 正确结果只接受 `Cux.AiQueryJobTrackingV`；测试实际使用 `AiQueryJobProgressV`，不在允许范围内。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT PartNum, PartDescription, JobQty, JobOprCompQty FROM AiQueryJobProgressV WHERE JobNum = ?`
- 参数：`["24M007-I-14"]`
- 未通过原因：视图应为 aiqueryjobtrackingv，实际为 aiqueryjobprogressv

### 17.10 查询工单WO019594对应部件的完工数量

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryJobTrackingV`
2. 筛选条件：`JobNum = 'WO019594'`
3. 查询字段：`PartNum`、`PartDescription`、`JobOprCompQty`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryJobProgressV`
2. 筛选条件：`JobNum = 'WO019594'`
3. 查询字段：`JobOprCompQty`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：❌ 正确结果只接受 `Cux.AiQueryJobTrackingV`；测试实际使用 `AiQueryJobProgressV`，不在允许范围内。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：❌ 正确结果要求 `PartNum`、`PartDescription`、`JobOprCompQty`；测试输出为 `JobOprCompQty`，缺少必需业务字段：`partdescription`、`partnum`。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT JobOprCompQty FROM AiQueryJobProgressV WHERE JobNum = ?`
- 参数：`["WO019594"]`
- 未通过原因：视图应为 aiqueryjobtrackingv，实际为 aiqueryjobprogressv；输出缺少字段：partdescription, partnum

### 18.2 查询物料181L-01-01-003-A_扇形盖板_发黑的库存计量单位和采购计量单位

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryPartTimeTrackingV`
2. 筛选条件：`PartDescription = '181L-01-01-003-A_扇形盖板_发黑'`
3. 查询字段：`IUM`、`PUM`
4. 其他关键字内容：`DISTINCT`

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryPartTimeTrackingV`
2. 筛选条件：`PartNum = '181L-01-01-003-A_扇形盖板_发黑' OR PartDescription LIKE '%扇形盖板\_发黑%' ESCAPE '\'`
3. 查询字段：`IUM`、`PUM`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：❌ 正确筛选为 `PartDescription = '181L-01-01-003-A_扇形盖板_发黑'`；测试筛选为 `PartNum = '181L-01-01-003-A_扇形盖板_发黑' OR PartDescription LIKE '%扇形盖板\_发黑%' ESCAPE '\'`。字段、运算符、筛选值或业务范围不等价。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。 ⚠️ 测试缺少 `DISTINCT`；按测试标准本项仍通过，但存在重复记录风险。

- 实际 SQLite SQL：`SELECT IUM, PUM FROM AiQueryPartTimeTrackingV WHERE PartNum = ? OR PartDescription LIKE ? ESCAPE '\'`
- 参数：`["181L-01-01-003-A_扇形盖板_发黑", "%扇形盖板\\_发黑%"]`
- 未通过原因：筛选条件的字段、运算符、值或查询范围与标准不一致
- 警告：标准要求 DISTINCT，但实际未使用；按标准不判错，可能产生重复记录

### 18.3 查询211.181L-01-01-003-A的时间轴明细

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryPartTimeTrackingV`
2. 筛选条件：`PartNum = '211.181L-01-01-003-A'`
3. 查询字段：`DueDate`、`ReceiptQty`、`RequiredQty`、`BalanceQty`、`SourceName`
4. 其他关键字内容：`ORDER BY DueDate ASC`

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryPartTimeTrackingV`
2. 筛选条件：`PartNum = '211.181L-01-01-003-A'`
3. 查询字段：`PartNum`、`PartDescription`、`IUM`、`PUM`、`DueDate`、`ReceiptQty`、`RequiredQty`、`BalanceQty`、`SourceName`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：❌ 正确结果要求 `ORDER BY DueDate ASC`；测试结果为 空。错误原因：ORDER BY 与标准不一致。

- 实际 SQLite SQL：`SELECT PartNum, PartDescription, IUM, PUM, DueDate, ReceiptQty, RequiredQty, BalanceQty, SourceName FROM AiQueryPartTimeTrackingV WHERE PartNum = ?`
- 参数：`["211.181L-01-01-003-A"]`
- 未通过原因：ORDER BY 与标准不一致

### 18.5 查询211.181L-01-01-003-A当前余额数量

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryPartTimeTrackingV`
2. 筛选条件：`PartNum = '211.181L-01-01-003-A' AND SourceName = '现存量'`
3. 查询字段：`BalanceQty`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryPartTimeTrackingV`
2. 筛选条件：`PartNum = '211.181L-01-01-003-A'`
3. 查询字段：`BalanceQty`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：❌ 正确筛选为 `PartNum = '211.181L-01-01-003-A' AND SourceName = '现存量'`；测试筛选为 `PartNum = '211.181L-01-01-003-A'`。字段、运算符、筛选值或业务范围不等价。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT BalanceQty FROM AiQueryPartTimeTrackingV WHERE PartNum = ?`
- 参数：`["211.181L-01-01-003-A"]`
- 未通过原因：筛选条件的字段、运算符、值或查询范围与标准不一致

### 18.7 查询3010000978在2024年9月23日的需求数量和余额

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryPartTimeTrackingV`
2. 筛选条件：`PartNum = '3010000978' AND DueDate >= '2024-09-23' AND DueDate < '2024-09-24'`
3. 查询字段：`RequiredQty`、`BalanceQty`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryPartTimeTrackingV`
2. 筛选条件：`PartNum = '3010000978' AND DueDate = '2024-09-23'`
3. 查询字段：`RequiredQty`、`BalanceQty`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：❌ 正确筛选为 `PartNum = '3010000978' AND DueDate >= '2024-09-23' AND DueDate < '2024-09-24'`；测试筛选为 `PartNum = '3010000978' AND DueDate = '2024-09-23'`。字段、运算符、筛选值或业务范围不等价。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT RequiredQty, BalanceQty FROM AiQueryPartTimeTrackingV WHERE PartNum = ? AND DueDate = ?`
- 参数：`["3010000978", "2024-09-23"]`
- 未通过原因：筛选条件的字段、运算符、值或查询范围与标准不一致

### 18.8 查询图号211.181L-01-01-003-A的现存量

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryPartTimeTrackingV`
2. 筛选条件：`PartNum = '211.181L-01-01-003-A' AND SourceName = '现存量'`
3. 查询字段：`BalanceQty`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryPartOnHandV`
2. 筛选条件：`PartNum = '211.181L-01-01-003-A'`
3. 查询字段：`PartNum`、`PartDescription`、`Qty`、`BinNum`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：❌ 正确结果只接受 `Cux.AiQueryPartTimeTrackingV`；测试实际使用 `AiQueryPartOnHandV`，不在允许范围内。
2. 筛选条件：❌ 正确筛选为 `PartNum = '211.181L-01-01-003-A' AND SourceName = '现存量'`；测试筛选为 `PartNum = '211.181L-01-01-003-A'`。字段、运算符、筛选值或业务范围不等价。
3. 查询字段：❌ 正确结果要求 `BalanceQty`；测试输出为 `PartNum`、`PartDescription`、`Qty`、`BinNum`，缺少必需业务字段：`balanceqty`。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT PartNum, PartDescription, Qty, BinNum FROM AiQueryPartOnHandV WHERE PartNum = ?`
- 参数：`["211.181L-01-01-003-A"]`
- 未通过原因：视图应为 aiqueryparttimetrackingv，实际为 aiquerypartonhandv；筛选条件的字段、运算符、值或查询范围与标准不一致；输出缺少字段：balanceqty

### 18.9 查询物料211.181L-01-01-003-A后续供需变化

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryPartTimeTrackingV`
2. 筛选条件：`PartNum = '211.181L-01-01-003-A' AND DueDate >= CURRENT_DATE`
3. 查询字段：`DueDate`、`ReceiptQty`、`RequiredQty`、`BalanceQty`、`SourceName`
4. 其他关键字内容：`ORDER BY DueDate ASC`

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryPartTimeTrackingV`
2. 筛选条件：`PartNum = '211.181L-01-01-003-A'`
3. 查询字段：`DueDate`、`ReceiptQty`、`RequiredQty`、`BalanceQty`、`SourceName`
4. 其他关键字内容：`ORDER BY DueDate`

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：❌ 正确筛选为 `PartNum = '211.181L-01-01-003-A' AND DueDate >= CURRENT_DATE`；测试筛选为 `PartNum = '211.181L-01-01-003-A'`。字段、运算符、筛选值或业务范围不等价。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT DueDate, ReceiptQty, RequiredQty, BalanceQty, SourceName FROM AiQueryPartTimeTrackingV WHERE PartNum = ? ORDER BY DueDate`
- 参数：`["211.181L-01-01-003-A"]`
- 未通过原因：筛选条件的字段、运算符、值或查询范围与标准不一致

### 18.10 查询211.181L-01-01-003-A的库存单位、采购单位和余额数量

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryPartTimeTrackingV`
2. 筛选条件：`PartNum = '211.181L-01-01-003-A' AND SourceName = '现存量'`
3. 查询字段：`IUM`、`PUM`、`BalanceQty`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryPartTimeTrackingV`
2. 筛选条件：`PartNum = '211.181L-01-01-003-A' AND SourceName = '当前现存量'`
3. 查询字段：`IUM`、`PUM`、`BalanceQty`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：❌ 正确筛选为 `PartNum = '211.181L-01-01-003-A' AND SourceName = '现存量'`；测试筛选为 `PartNum = '211.181L-01-01-003-A' AND SourceName = '当前现存量'`。字段、运算符、筛选值或业务范围不等价。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT IUM, PUM, BalanceQty FROM AiQueryPartTimeTrackingV WHERE PartNum = ? AND SourceName = '当前现存量'`
- 参数：`["211.181L-01-01-003-A"]`
- 未通过原因：筛选条件的字段、运算符、值或查询范围与标准不一致

### 20.6 查询供应商上海洪瀚流体控制设备有限公司的累计金额

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryPayablesV`
2. 筛选条件：`VendorName = '上海洪瀚流体控制设备有限公司'`
3. 查询字段：`Amount`、`BeqAmount`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryPayablesV`
2. 筛选条件：`VendorName = '上海洪瀚流体控制设备有限公司'`
3. 查询字段：`BeqAmount`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：❌ 正确结果要求 `Amount`、`BeqAmount`；测试输出为 `BeqAmount`，缺少必需业务字段：`amount`。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT BeqAmount FROM AiQueryPayablesV WHERE VendorName = ?`
- 参数：`["上海洪瀚流体控制设备有限公司"]`
- 未通过原因：输出缺少字段：amount

### 20.8 查询上海影旗传动机械有限公司的应付余额

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryPayablesV`
2. 筛选条件：`VendorName = '上海影旗传动机械有限公司'`
3. 查询字段：`RemainAmount`、`BeqRemainAmount`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryPayablesV`
2. 筛选条件：`VendorName = '上海影旗传动机械有限公司'`
3. 查询字段：`VendorName`、`BeqRemainAmount`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：❌ 正确结果要求 `RemainAmount`、`BeqRemainAmount`；测试输出为 `VendorName`、`BeqRemainAmount`，缺少必需业务字段：`remainamount`。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT VendorName, BeqRemainAmount FROM AiQueryPayablesV WHERE VendorName = ?`
- 参数：`["上海影旗传动机械有限公司"]`
- 未通过原因：输出缺少字段：remainamount

### 20.9 查询供应商上海洪瀚流体控制设备有限公司的剩余应付金额

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryPayablesV`
2. 筛选条件：`VendorName = '上海洪瀚流体控制设备有限公司'`
3. 查询字段：`RemainAmount`、`BeqRemainAmount`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryPayablesV`
2. 筛选条件：`VendorName = '上海洪瀚流体控制设备有限公司'`
3. 查询字段：`VendorName`、`BeqRemainAmount`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：❌ 正确结果要求 `RemainAmount`、`BeqRemainAmount`；测试输出为 `VendorName`、`BeqRemainAmount`，缺少必需业务字段：`remainamount`。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT VendorName, BeqRemainAmount FROM AiQueryPayablesV WHERE VendorName = ?`
- 参数：`["上海洪瀚流体控制设备有限公司"]`
- 未通过原因：输出缺少字段：remainamount

### 20.10 查询上海影旗传动机械有限公司的累计金额和余额

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryPayablesV`
2. 筛选条件：`VendorName = '上海影旗传动机械有限公司'`
3. 查询字段：`Amount`、`BeqAmount`、`RemainAmount`、`BeqRemainAmount`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryPayablesV`
2. 筛选条件：`VendorName = '上海影旗传动机械有限公司'`
3. 查询字段：`Amount`、`RemainAmount`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：❌ 正确结果要求 `Amount`、`BeqAmount`、`RemainAmount`、`BeqRemainAmount`；测试输出为 `Amount`、`RemainAmount`，缺少必需业务字段：`beqamount`、`beqremainamount`。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT Amount, RemainAmount FROM AiQueryPayablesV WHERE VendorName = ?`
- 参数：`["上海影旗传动机械有限公司"]`
- 未通过原因：输出缺少字段：beqamount, beqremainamount

### 21.3 查询客户江西江铜龙昌精密铜管有限公司的累计金额

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryReceivablesV`
2. 筛选条件：`CustName = '江西江铜龙昌精密铜管有限公司'`
3. 查询字段：`Amount`、`BeqAmount`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryReceivablesV`
2. 筛选条件：`CustName = '江西江铜龙昌精密铜管有限公司'`
3. 查询字段：`BeqAmount`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：❌ 正确结果要求 `Amount`、`BeqAmount`；测试输出为 `BeqAmount`，缺少必需业务字段：`amount`。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT BeqAmount FROM AiQueryReceivablesV WHERE CustName = ?`
- 参数：`["江西江铜龙昌精密铜管有限公司"]`
- 未通过原因：输出缺少字段：amount

### 21.5 查询客户金龙精密铜管集团股份有限公司的原币余额

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryReceivablesV`
2. 筛选条件：`CustName = '金龙精密铜管集团股份有限公司'`
3. 查询字段：`RemainAmount`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryReceivablesV`
2. 筛选条件：`CustName = '金龙精密铜管集团股份有限公司'`
3. 查询字段：`CustID`、`CustName`、`BeqRemainAmount`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：❌ 正确结果要求 `RemainAmount`；测试输出为 `CustID`、`CustName`、`BeqRemainAmount`，缺少必需业务字段：`remainamount`。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT CustID, CustName, BeqRemainAmount FROM AiQueryReceivablesV WHERE CustName = ?`
- 参数：`["金龙精密铜管集团股份有限公司"]`
- 未通过原因：输出缺少字段：remainamount

### 21.7 查询江西江铜龙昌精密铜管有限公司的应收余额

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryReceivablesV`
2. 筛选条件：`CustName = '江西江铜龙昌精密铜管有限公司'`
3. 查询字段：`RemainAmount`、`BeqRemainAmount`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryReceivablesV`
2. 筛选条件：`CustName = '江西江铜龙昌精密铜管有限公司'`
3. 查询字段：`CustName`、`RemainAmount`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：❌ 正确结果要求 `RemainAmount`、`BeqRemainAmount`；测试输出为 `CustName`、`RemainAmount`，缺少必需业务字段：`beqremainamount`。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT CustName, RemainAmount FROM AiQueryReceivablesV WHERE CustName = ?`
- 参数：`["江西江铜龙昌精密铜管有限公司"]`
- 未通过原因：输出缺少字段：beqremainamount

### 21.8 查询金龙精密铜管集团股份有限公司的应收余额

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryReceivablesV`
2. 筛选条件：`CustName = '金龙精密铜管集团股份有限公司'`
3. 查询字段：`RemainAmount`、`BeqRemainAmount`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryReceivablesV`
2. 筛选条件：`CustName = '金龙精密铜管集团股份有限公司'`
3. 查询字段：`CustName`、`BeqRemainAmount`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：✅ 测试使用的视图属于正确结果允许的视图。
2. 筛选条件：✅ 字段、运算符、筛选值和业务范围一致；参数绑定、条件顺序及不改变范围的写法差异已忽略。
3. 查询字段：❌ 正确结果要求 `RemainAmount`、`BeqRemainAmount`；测试输出为 `CustName`、`BeqRemainAmount`，缺少必需业务字段：`remainamount`。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT CustName, BeqRemainAmount FROM AiQueryReceivablesV WHERE CustName = ?`
- 参数：`["金龙精密铜管集团股份有限公司"]`
- 未通过原因：输出缺少字段：remainamount

### 21.9 查询江西江铜龙昌精密铜管有限公司的本币余额和原币余额

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryReceivablesV`
2. 筛选条件：`CustName = '江西江铜龙昌精密铜管有限公司'`
3. 查询字段：`RemainAmount`、`BeqRemainAmount`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryPayablesV`
2. 筛选条件：`VendorName = '江西江铜龙昌精密铜管有限公司'`
3. 查询字段：`VendorName`、`BeqRemainAmount`、`RemainAmount`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：❌ 正确结果只接受 `Cux.AiQueryReceivablesV`；测试实际使用 `AiQueryPayablesV`，不在允许范围内。
2. 筛选条件：❌ 正确筛选为 `CustName = '江西江铜龙昌精密铜管有限公司'`；测试筛选为 `VendorName = '江西江铜龙昌精密铜管有限公司'`。字段、运算符、筛选值或业务范围不等价。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT VendorName, BeqRemainAmount, RemainAmount FROM AiQueryPayablesV WHERE VendorName = ?`
- 参数：`["江西江铜龙昌精密铜管有限公司"]`
- 未通过原因：视图应为 aiqueryreceivablesv，实际为 aiquerypayablesv；筛选条件的字段、运算符、值或查询范围与标准不一致

### 21.10 查询金龙精密铜管集团股份有限公司的累计金额和余额

- 总判定：❌ 未通过

#### 正确结果的 1、2、3、4

1. 视图：`Cux.AiQueryReceivablesV`
2. 筛选条件：`CustName = '金龙精密铜管集团股份有限公司'`
3. 查询字段：`Amount`、`BeqAmount`、`RemainAmount`、`BeqRemainAmount`
4. 其他关键字内容：空

#### 测试结果的 1、2、3、4

1. 视图：`AiQueryPayablesV`
2. 筛选条件：`VendorName = '金龙精密铜管集团股份有限公司'`
3. 查询字段：`Amount`、`BeqAmount`、`RemainAmount`、`BeqRemainAmount`
4. 其他关键字内容：空

#### 1、2、3、4 逐项对比

1. 视图：❌ 正确结果只接受 `Cux.AiQueryReceivablesV`；测试实际使用 `AiQueryPayablesV`，不在允许范围内。
2. 筛选条件：❌ 正确筛选为 `CustName = '金龙精密铜管集团股份有限公司'`；测试筛选为 `VendorName = '金龙精密铜管集团股份有限公司'`。字段、运算符、筛选值或业务范围不等价。
3. 查询字段：✅ 正确结果要求的业务字段全部出现在测试最终输出中；允许不改变业务含义或粒度的附加字段。
4. 其他关键字内容：✅ 必需的聚合、去重、分组、排序、CASE 和数量限制与正确结果一致。

- 实际 SQLite SQL：`SELECT Amount, BeqAmount, RemainAmount, BeqRemainAmount FROM AiQueryPayablesV WHERE VendorName = ?`
- 参数：`["金龙精密铜管集团股份有限公司"]`
- 未通过原因：视图应为 aiqueryreceivablesv，实际为 aiquerypayablesv；筛选条件的字段、运算符、值或查询范围与标准不一致
