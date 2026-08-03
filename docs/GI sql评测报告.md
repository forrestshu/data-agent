# ERP 210 题 SQL Schema 评测报告（按新测试标准）

## 第一部分：评测结果

- 总题数：210 题
- 正确：196 题
  - 无警告通过：184 题
  - 带警告通过：12 题
- 错误：14 题
- 警告：12 题
- 正确率：93.33%

缺少 `DISTINCT` 不再判定为错误；只要其他评测项正确，该题计入正确，同时标记警告。

## 第二部分：错误和警告类型

### 1. 缺少必要的汇总操作

错在哪里：问题要求返回物料或项目层面的总量，但测试答案只返回明细行，或逐行进行判断，没有使用必要的 `SUM` 汇总。因此可能返回多条记录，或者不能得到整体数量。

涉及问题：`2.7`、`2.8`、`8.5`、`8.6`、`8.7`、`8.8`

### 2. 视图、筛选字段和业务指标选择错误

错在哪里：测试答案查询的是末道工序完成进度，而问题要求的是完工入库数量。两者属于不同业务阶段，不能相互替代。

涉及问题：`10.6`

### 3. 额外筛选条件改变查询范围

错在哪里：测试答案增加了 `JobHead_JobNum NOT LIKE '%[^0-9]%'`，排除了项目中的非纯数字工单。题目没有要求排除这些工单，因此结果范围被缩小。

涉及问题：`13.1`、`13.4`、`13.8`、`13.9`、`13.10`

### 4. “全部完成”的判断逻辑错误

错在哪里：测试答案比较项目总完成量和总生产量；某个工单超额完成时，可能掩盖另一个未完成工单。正确逻辑应逐工单判断，再确认所有工单都满足完成条件。

涉及问题：`13.8`、`13.9`

### 5. 缺少必要的日期排序

错在哪里：问题要求按时间查看供需变化，测试答案没有按 `DueDate ASC` 排序，不能保证结果按时间先后展示。

涉及问题：`18.3`、`18.9`

### 6. “后续”时间范围筛选错误

错在哪里：测试答案只检查日期不为空，没有限定当前日期及之后，因此会混入历史记录。

涉及问题：`18.9`

### 7. 警告：缺少 `DISTINCT`

警告内容：测试答案没有去重，在数据存在重复行时可能返回重复记录。按照新标准，这类题目仍判定为正确，但记录警告。

涉及问题：`9.1`、`9.2`、`9.3`、`9.4`、`9.5`、`9.6`、`9.7`、`9.8`、`9.9`、`9.10`、`12.7`、`12.8`

## 第三部分：错误题详细内容

### 2.7

1. 问题：查询物料编码120000019有没有库存

2. 标准答案：

   - 视图：`Cux.AiQueryPartOnHandV`
   - 筛选条件：`PartNum = '120000019'`
   - 查询字段：`Qty`
   - 其他关键字内容：`SUM(Qty)`、`CASE WHEN SUM(Qty) > 0 THEN '是' ELSE '否' END`

3. 测试答案：

   - 视图：`Cux.AiQueryPartOnHandV`
   - 筛选条件：`PartNum = '120000019'`
   - 查询字段：`PartNum`、`PartDescription`、`Qty`、`BinNum`、`BinName`
   - 其他关键字内容：`CASE WHEN ISNULL(Qty, 0) > 0 THEN '是' ELSE '否' END`

4. 错的地方在哪：

   - 其他关键字或操作不一致：标准答案要求先用 `SUM(Qty)` 汇总该物料在全部库位的库存，再判断汇总结果是否大于 0；测试答案直接逐行判断 `Qty`，没有汇总，可能对同一物料返回多条“是/否”结果。


### 2.8

1. 问题：查询120000019当前库存数量是多少

2. 标准答案：

   - 视图：`Cux.AiQueryPartOnHandV`
   - 筛选条件：`PartNum = '120000019'`
   - 查询字段：`Qty`
   - 其他关键字内容：`SUM(Qty)`

3. 测试答案：

   - 视图：`Cux.AiQueryPartOnHandV`
   - 筛选条件：`PartNum = '120000019'`
   - 查询字段：`PartNum`、`PartDescription`、`Qty`
   - 其他关键字内容：空

4. 错的地方在哪：

   - 其他关键字或操作缺失：标准答案要求使用 `SUM(Qty)` 计算该物料的总库存量；测试答案只查询各库存记录的 `Qty`，没有做总量汇总。


### 8.5

1. 问题：查询120000019当前库存有多少

2. 标准答案：

   - 视图：`Cux.AiQueryPartOnHandV`
   - 筛选条件：`PartNum = '120000019'`
   - 查询字段：`Qty`
   - 其他关键字内容：`SUM(Qty)`

3. 测试答案：

   - 视图：`Cux.AiQueryPartOnHandV`
   - 筛选条件：`PartNum = '120000019'`
   - 查询字段：`PartNum`、`PartDescription`、`Qty`
   - 其他关键字内容：空

4. 错的地方在哪：

   - 其他关键字或操作缺失：标准答案要求使用 `SUM(Qty)` 汇总成品库存；测试答案只返回库存明细，没有计算总库存量。


### 8.6

1. 问题：查询120000019库存数量

2. 标准答案：

   - 视图：`Cux.AiQueryPartOnHandV`
   - 筛选条件：`PartNum = '120000019'`
   - 查询字段：`Qty`
   - 其他关键字内容：`SUM(Qty)`

3. 测试答案：

   - 视图：`Cux.AiQueryPartOnHandV`
   - 筛选条件：`PartNum = '120000019'`
   - 查询字段：`PartNum`、`PartDescription`、`Qty`
   - 其他关键字内容：空

4. 错的地方在哪：

   - 其他关键字或操作缺失：标准答案要求使用 `SUM(Qty)` 汇总成品库存；测试答案只返回库存明细，没有计算总库存量。


### 8.7

1. 问题：查询GCr15圆钢Φ45库存数量

2. 标准答案：

   - 视图：`Cux.AiQueryPartOnHandV`
   - 筛选条件：`PartDescription = 'GCr15圆钢Φ45'`
   - 查询字段：`Qty`
   - 其他关键字内容：`SUM(Qty)`

3. 测试答案：

   - 视图：`Cux.AiQueryPartOnHandV`
   - 筛选条件：`PartDescription = 'GCr15圆钢Φ45'`
   - 查询字段：`PartNum`、`PartDescription`、`Qty`
   - 其他关键字内容：空

4. 错的地方在哪：

   - 其他关键字或操作缺失：标准答案要求使用 `SUM(Qty)` 汇总成品库存；测试答案只返回库存明细，没有计算总库存量。


### 8.8

1. 问题：查询GCr15圆钢Φ45还有多少库存

2. 标准答案：

   - 视图：`Cux.AiQueryPartOnHandV`
   - 筛选条件：`PartDescription = 'GCr15圆钢Φ45'`
   - 查询字段：`Qty`
   - 其他关键字内容：`SUM(Qty)`

3. 测试答案：

   - 视图：`Cux.AiQueryPartOnHandV`
   - 筛选条件：`PartDescription = 'GCr15圆钢Φ45'`
   - 查询字段：`PartNum`、`PartDescription`、`Qty`
   - 其他关键字内容：空

4. 错的地方在哪：

   - 其他关键字或操作缺失：标准答案要求使用 `SUM(Qty)` 汇总成品库存；测试答案只返回库存明细，没有计算总库存量。


### 10.6

1. 问题：查询工单000023的完工入库数量

2. 标准答案：

   - 视图：`Cux.AiQueryProjectJobV`
   - 筛选条件：`JobHead_JobNum = '000023'`
   - 查询字段：`CompleteQty`
   - 其他关键字内容：空

3. 测试答案：

   - 视图：`Cux.AiQueryJobProgressV`
   - 筛选条件：`JobNum = '000023'`
   - 查询字段：`JobNum`、`PartNum`、`PartDescription`、`JobOprCompQty`
   - 其他关键字内容：空

4. 错的地方在哪：

   - 视图不一致：标准答案使用 `Cux.AiQueryProjectJobV`，测试答案使用 `Cux.AiQueryJobProgressV`。
   - 筛选字段不一致：标准答案按 `JobHead_JobNum = '000023'` 筛选，测试答案按 `JobNum = '000023'` 筛选。
   - 查询字段不正确：问题要求“完工入库数量”，标准字段是 `CompleteQty`；测试答案返回的是 `JobNum`、`PartNum`、`PartDescription`、`JobOprCompQty`，其中 `JobOprCompQty` 表示工序完工数量，不能替代完工入库数量。


### 13.1

1. 问题：查询项目24M148-H的完工入库数量

2. 标准答案：

   - 视图：`Cux.AiQueryProjectJobV`
   - 筛选条件：`ProjectID = '24M148-H'`
   - 查询字段：`CompleteQty`
   - 其他关键字内容：`SUM(CompleteQty)`

3. 测试答案：

   - 视图：`Cux.AiQueryProjectJobV`
   - 筛选条件：`ProjectID = '24M148-H' AND JobHead_JobNum NOT LIKE '%[^0-9]%'`
   - 查询字段：`ProjectID`、`CompleteQty`
   - 其他关键字内容：`SUM(ISNULL(CompleteQty, 0))`、`GROUP BY ProjectID`

4. 错的地方在哪：

   - 筛选条件多加了限制：标准答案只要求 `ProjectID = '24M148-H'`；测试答案增加了 `JobHead_JobNum NOT LIKE '%[^0-9]%'`，会排除项目中的非纯数字工单，改变问题原本的查询范围。


### 13.4

1. 问题：查询项目24M148-A的完工入库数量

2. 标准答案：

   - 视图：`Cux.AiQueryProjectJobV`
   - 筛选条件：`ProjectID = '24M148-A'`
   - 查询字段：`CompleteQty`
   - 其他关键字内容：`SUM(CompleteQty)`

3. 测试答案：

   - 视图：`Cux.AiQueryProjectJobV`
   - 筛选条件：`ProjectID = '24M148-A' AND JobHead_JobNum NOT LIKE '%[^0-9]%'`
   - 查询字段：`ProjectID`、`CompleteQty`
   - 其他关键字内容：`SUM(ISNULL(CompleteQty, 0))`、`GROUP BY ProjectID`

4. 错的地方在哪：

   - 筛选条件多加了限制：标准答案只要求 `ProjectID = '24M148-A'`；测试答案增加了 `JobHead_JobNum NOT LIKE '%[^0-9]%'`，会排除项目中的非纯数字工单，改变问题原本的查询范围。


### 13.8

1. 问题：查询24M148-H是否全部完成

2. 标准答案：

   - 视图：`Cux.AiQueryProjectJobV`
   - 筛选条件：`ProjectID = '24M148-H'`
   - 查询字段：`JobHead_ProdQty`、`CompleteQty`
   - 其他关键字内容：`COUNT(*)`、`MIN(CASE WHEN CompleteQty >= JobHead_ProdQty AND JobHead_ProdQty > 0 THEN 1 ELSE 0 END)`、`CASE WHEN COUNT(*) > 0 AND MIN(...) = 1 THEN '是' ELSE '否' END`

3. 测试答案：

   - 视图：`Cux.AiQueryProjectJobV`
   - 筛选条件：`ProjectID = '24M148-H' AND JobHead_JobNum NOT LIKE '%[^0-9]%'`
   - 查询字段：`ProjectID`、`JobHead_ProdQty`、`CompleteQty`
   - 其他关键字内容：`SUM(ISNULL(JobHead_ProdQty, 0))`、`SUM(ISNULL(CompleteQty, 0))`、`CASE WHEN SUM(ISNULL(CompleteQty, 0)) >= SUM(ISNULL(JobHead_ProdQty, 0)) AND SUM(ISNULL(JobHead_ProdQty, 0)) > 0 THEN '是' ELSE '否' END`、`GROUP BY ProjectID`

4. 错的地方在哪：

   - 筛选条件多加了限制：标准答案只要求 `ProjectID = '24M148-H'`；测试答案增加了 `JobHead_JobNum NOT LIKE '%[^0-9]%'`，会排除项目中的部分工单。
   - 完成判断逻辑不正确：标准答案逐工单判断 `CompleteQty >= JobHead_ProdQty`，再用 `MIN(CASE...)` 确认所有工单都完成；测试答案只比较项目级总完成量和总生产量，某个工单超额完成时可能掩盖另一个未完成工单。


### 13.9

1. 问题：查询24M148-A是否全部完成

2. 标准答案：

   - 视图：`Cux.AiQueryProjectJobV`
   - 筛选条件：`ProjectID = '24M148-A'`
   - 查询字段：`JobHead_ProdQty`、`CompleteQty`
   - 其他关键字内容：`COUNT(*)`、`MIN(CASE WHEN CompleteQty >= JobHead_ProdQty AND JobHead_ProdQty > 0 THEN 1 ELSE 0 END)`、`CASE WHEN COUNT(*) > 0 AND MIN(...) = 1 THEN '是' ELSE '否' END`

3. 测试答案：

   - 视图：`Cux.AiQueryProjectJobV`
   - 筛选条件：`ProjectID = '24M148-A' AND JobHead_JobNum NOT LIKE '%[^0-9]%'`
   - 查询字段：`ProjectID`、`JobHead_ProdQty`、`CompleteQty`
   - 其他关键字内容：`SUM(ISNULL(JobHead_ProdQty, 0))`、`SUM(ISNULL(CompleteQty, 0))`、`CASE WHEN SUM(ISNULL(CompleteQty, 0)) >= SUM(ISNULL(JobHead_ProdQty, 0)) AND SUM(ISNULL(JobHead_ProdQty, 0)) > 0 THEN '是' ELSE '否' END`、`GROUP BY ProjectID`

4. 错的地方在哪：

   - 筛选条件多加了限制：标准答案只要求 `ProjectID = '24M148-A'`；测试答案增加了 `JobHead_JobNum NOT LIKE '%[^0-9]%'`，会排除项目中的部分工单。
   - 完成判断逻辑不正确：标准答案逐工单判断 `CompleteQty >= JobHead_ProdQty`，再用 `MIN(CASE...)` 确认所有工单都完成；测试答案只比较项目级总完成量和总生产量，某个工单超额完成时可能掩盖另一个未完成工单。


### 13.10

1. 问题：查询项目24M148-H和24M148-A的完工入库数量

2. 标准答案：

   - 视图：`Cux.AiQueryProjectJobV`
   - 筛选条件：`ProjectID IN ('24M148-H', '24M148-A')`
   - 查询字段：`ProjectID`、`CompleteQty`
   - 其他关键字内容：`SUM(CompleteQty)`、`GROUP BY ProjectID`

3. 测试答案：

   - 视图：`Cux.AiQueryProjectJobV`
   - 筛选条件：`ProjectID IN ('24M148-H', '24M148-A') AND JobHead_JobNum NOT LIKE '%[^0-9]%'`
   - 查询字段：`ProjectID`、`CompleteQty`
   - 其他关键字内容：`SUM(ISNULL(CompleteQty, 0))`、`GROUP BY ProjectID`

4. 错的地方在哪：

   - 筛选条件多加了限制：标准答案只要求 `ProjectID IN ('24M148-H', '24M148-A')`；测试答案增加了 `JobHead_JobNum NOT LIKE '%[^0-9]%'`，会排除项目中的非纯数字工单，改变问题原本的查询范围。


### 18.3

1. 问题：查询211.181L-01-01-003-A的时间轴明细

2. 标准答案：

   - 视图：`Cux.AiQueryPartTimeTrackingV`
   - 筛选条件：`PartNum = '211.181L-01-01-003-A'`
   - 查询字段：`DueDate`、`ReceiptQty`、`RequiredQty`、`BalanceQty`、`SourceName`
   - 其他关键字内容：`ORDER BY DueDate ASC`

3. 测试答案：

   - 视图：`Cux.AiQueryPartTimeTrackingV`
   - 筛选条件：`PartNum = '211.181L-01-01-003-A'`
   - 查询字段：`DueDate`、`ReceiptQty`、`RequiredQty`、`BalanceQty`、`SourceName`
   - 其他关键字内容：空

4. 错的地方在哪：

   - 其他关键字或操作缺失：标准答案要求使用 `ORDER BY DueDate ASC` 按日期升序展示供需变化；测试答案没有排序。


### 18.9

1. 问题：查询物料211.181L-01-01-003-A后续供需变化

2. 标准答案：

   - 视图：`Cux.AiQueryPartTimeTrackingV`
   - 筛选条件：`PartNum = '211.181L-01-01-003-A' AND DueDate >= CURRENT_DATE`
   - 查询字段：`DueDate`、`ReceiptQty`、`RequiredQty`、`BalanceQty`、`SourceName`
   - 其他关键字内容：`ORDER BY DueDate ASC`

3. 测试答案：

   - 视图：`Cux.AiQueryPartTimeTrackingV`
   - 筛选条件：`PartNum = '211.181L-01-01-003-A' AND DueDate IS NOT NULL`
   - 查询字段：`DueDate`、`ReceiptQty`、`RequiredQty`、`BalanceQty`、`SourceName`
   - 其他关键字内容：空

4. 错的地方在哪：

   - 筛选条件不正确：标准答案使用 `PartNum = '211.181L-01-01-003-A' AND DueDate >= CURRENT_DATE`，只查询当前日期及之后的记录；测试答案使用 `PartNum = '211.181L-01-01-003-A' AND DueDate IS NOT NULL`，会把所有非空日期的历史记录也查出来。
   - 其他关键字或操作缺失：标准答案要求使用 `ORDER BY DueDate ASC` 按日期升序展示后续供需变化；测试答案没有排序。
