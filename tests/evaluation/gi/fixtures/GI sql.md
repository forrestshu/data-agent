## 1.1 查询描述为JX不锈钢堵头10X1的平均单价

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], ISNULL([AvgPrice], 0) AS [AvgPrice] FROM [Cux].[AiQueryPoPriceV] WITH(NOLOCK) WHERE LTRIM(RTRIM([LineDesc])) = N'JX不锈钢堵头10X1'
```

1. 视图：`Cux.AiQueryPoPriceV`
2. 筛选条件：`LineDesc = 'JX不锈钢堵头10X1'`
3. 查询字段：`PartNum`、`LineDesc`、`AvgPrice`
4. 其他关键字内容：空

## 1.2 查询描述为JX不锈钢堵头10X1的最新采购价

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], ISNULL([NewPrice], 0) AS [NewPrice], LTRIM(RTRIM([NewVendorName])) AS [NewVendorName], ISNULL([NewPONum], 0) AS [NewPONum] FROM [Cux].[AiQueryPoPriceV] WITH(NOLOCK) WHERE LTRIM(RTRIM([LineDesc])) = N'JX不锈钢堵头10X1'
```

1. 视图：`Cux.AiQueryPoPriceV`
2. 筛选条件：`LineDesc = 'JX不锈钢堵头10X1'`
3. 查询字段：`PartNum`、`LineDesc`、`NewPrice`、`NewVendorName`、`NewPONum`
4. 其他关键字内容：空

## 1.3 查询描述为JX不锈钢堵头10X1的采购提前期

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], [LeadTime] AS [LeadTime] FROM [Cux].[AiQueryPoPriceV] WITH(NOLOCK) WHERE LTRIM(RTRIM([LineDesc])) = N'JX不锈钢堵头10X1'
```

1. 视图：`Cux.AiQueryPoPriceV`
2. 筛选条件：`LineDesc = 'JX不锈钢堵头10X1'`
3. 查询字段：`PartNum`、`LineDesc`、`LeadTime`
4. 其他关键字内容：空

## 1.4 查询编码1100000144的平均单价

```sql
SELECT DISTINCT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], ISNULL([AvgPrice], 0) AS [AvgPrice] FROM [Cux].[AiQueryPoPriceV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'1100000144'
```

1. 视图：`Cux.AiQueryPoPriceV`
2. 筛选条件：`PartNum = '1100000144'`
3. 查询字段：`PartNum`、`LineDesc`、`AvgPrice`
4. 其他关键字内容：`DISTINCT`

## 1.5 查询编码1100000144的最新采购价

```sql
SELECT DISTINCT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], ISNULL([NewPrice], 0) AS [NewPrice], LTRIM(RTRIM([NewVendorName])) AS [NewVendorName], ISNULL([NewPONum], 0) AS [NewPONum] FROM [Cux].[AiQueryPoPriceV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'1100000144'
```

1. 视图：`Cux.AiQueryPoPriceV`
2. 筛选条件：`PartNum = '1100000144'`
3. 查询字段：`PartNum`、`LineDesc`、`NewPrice`、`NewVendorName`、`NewPONum`
4. 其他关键字内容：`DISTINCT`

## 1.6 查询编码1100000144的采购提前期

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], ISNULL([LeadTime], 0) AS [LeadTime] FROM [Cux].[AiQueryPoPriceV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'1100000144'
```

1. 视图：`Cux.AiQueryPoPriceV`
2. 筛选条件：`PartNum = '1100000144'`
3. 查询字段：`PartNum`、`LineDesc`、`LeadTime`
4. 其他关键字内容：空

## 1.7 查询描述包含钢丝网的平均单价

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], ISNULL([AvgPrice], 0) AS [AvgPrice] FROM [Cux].[AiQueryPoPriceV] WITH(NOLOCK) WHERE [LineDesc] LIKE N'%钢丝网%'
```

1. 视图：`Cux.AiQueryPoPriceV`
2. 筛选条件：`LineDesc LIKE '%钢丝网%'`
3. 查询字段：`PartNum`、`LineDesc`、`AvgPrice`
4. 其他关键字内容：空

## 1.8 查询描述包含钢丝网的最新采购价

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], ISNULL([NewPrice], 0) AS [NewPrice], LTRIM(RTRIM([NewVendorName])) AS [NewVendorName], ISNULL([NewPONum], 0) AS [NewPONum] FROM [Cux].[AiQueryPoPriceV] WITH(NOLOCK) WHERE [LineDesc] LIKE N'%钢丝网%'
```

1. 视图：`Cux.AiQueryPoPriceV`
2. 筛选条件：`LineDesc LIKE '%钢丝网%'`
3. 查询字段：`PartNum`、`LineDesc`、`NewPrice`、`NewVendorName`、`NewPONum`
4. 其他关键字内容：空

## 1.9 查询描述为12寸中齿平板锉刀-机加的平均单价

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], ISNULL([AvgPrice], 0) AS [AvgPrice] FROM [Cux].[AiQueryPoPriceV] WITH(NOLOCK) WHERE LTRIM(RTRIM([LineDesc])) = N'12寸中齿平板锉刀-机加'
```

1. 视图：`Cux.AiQueryPoPriceV`
2. 筛选条件：`LineDesc = '12寸中齿平板锉刀-机加'`
3. 查询字段：`PartNum`、`LineDesc`、`AvgPrice`
4. 其他关键字内容：空

## 1.10 查询描述包含雨布6500*4300的平均单价

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], ISNULL([AvgPrice], 0) AS [AvgPrice] FROM [Cux].[AiQueryPoPriceV] WITH(NOLOCK) WHERE [LineDesc] LIKE N'%雨布6500*4300%'
```

1. 视图：`Cux.AiQueryPoPriceV`
2. 筛选条件：`LineDesc LIKE '%雨布6500*4300%'`
3. 查询字段：`PartNum`、`LineDesc`、`AvgPrice`
4. 其他关键字内容：空

## 2.1 查询物料编码120000019的现有量

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([Qty], 0) AS [Qty] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'120000019'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartNum = '120000019'`
3. 查询字段：`PartNum`、`PartDescription`、`Qty`
4. 其他关键字内容：空

## 2.2 查询物料编码120000019的库位

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], LTRIM(RTRIM([BinNum])) AS [BinNum] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'120000019'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartNum = '120000019'`
3. 查询字段：`PartNum`、`PartDescription`、`BinNum`
4. 其他关键字内容：空

## 2.3 查询物料编码120000019的库位名称

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], LTRIM(RTRIM([BinName])) AS [BinName] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'120000019'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartNum = '120000019'`
3. 查询字段：`PartNum`、`PartDescription`、`BinName`
4. 其他关键字内容：空

## 2.4 查询物料编码120000019的现有量

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([Qty], 0) AS [Qty] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'120000019'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartNum = '120000019'`
3. 查询字段：`PartNum`、`PartDescription`、`Qty`
4. 其他关键字内容：空

## 2.5 查询物料编码120000019的库位

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], LTRIM(RTRIM([BinNum])) AS [BinNum] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'120000019'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartNum = '120000019'`
3. 查询字段：`PartNum`、`PartDescription`、`BinNum`
4. 其他关键字内容：空

## 2.6 查询物料编码120000019的现有量和库位

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([Qty], 0) AS [Qty], LTRIM(RTRIM([BinNum])) AS [BinNum] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'120000019'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartNum = '120000019'`
3. 查询字段：`PartNum`、`PartDescription`、`Qty`、`BinNum`
4. 其他关键字内容：空

## 2.7 查询物料编码120000019有没有库存

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([Qty], 0) AS [Qty], LTRIM(RTRIM([BinNum])) AS [BinNum], LTRIM(RTRIM([BinName])) AS [BinName], CASE WHEN ISNULL([Qty], 0) > 0 THEN N'是' ELSE N'否' END AS [HasInventory] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'120000019'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartNum = '120000019'`
3. 查询字段：`PartNum`、`PartDescription`、`Qty`、`BinNum`、`BinName`
4. 其他关键字内容：`CASE WHEN ISNULL(Qty, 0) > 0 THEN '是' ELSE '否' END`

## 2.8 查询120000019当前库存数量是多少

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([Qty], 0) AS [Qty] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'120000019'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartNum = '120000019'`
3. 查询字段：`PartNum`、`PartDescription`、`Qty`
4. 其他关键字内容：空

## 2.9 查询120000019存放在哪个库位

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], LTRIM(RTRIM([BinNum])) AS [BinNum], LTRIM(RTRIM([BinName])) AS [BinName] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'120000019'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartNum = '120000019'`
3. 查询字段：`PartNum`、`PartDescription`、`BinNum`、`BinName`
4. 其他关键字内容：空

## 2.10 查询120000019的库存数量和库位名称

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([Qty], 0) AS [Qty], LTRIM(RTRIM([BinName])) AS [BinName] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'120000019'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartNum = '120000019'`
3. 查询字段：`PartNum`、`PartDescription`、`Qty`、`BinName`
4. 其他关键字内容：空

## 3.1 查询项目号24M148-H的工单数量

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], COUNT(DISTINCT LTRIM(RTRIM([JobNum]))) AS [JobCount] FROM [Cux].[AiQueryJobV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'24M148-H' GROUP BY LTRIM(RTRIM([ProjectID]))
```

1. 视图：`Cux.AiQueryJobV`
2. 筛选条件：`ProjectID = '24M148-H'`
3. 查询字段：`ProjectID`、`JobNum`
4. 其他关键字内容：`COUNT(DISTINCT JobNum)`、`GROUP BY ProjectID`

## 3.2 查询项目号24M148-H的合交期

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([JobNum])) AS [JobNum], [ReqDueDate] AS [ReqDueDate] FROM [Cux].[AiQueryJobV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'24M148-H'
```

1. 视图：`Cux.AiQueryJobV`
2. 筛选条件：`ProjectID = '24M148-H'`
3. 查询字段：`ProjectID`、`JobNum`、`ReqDueDate`
4. 其他关键字内容：空

## 3.3 查询项目24M148-H有哪些工单

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([JobNum])) AS [JobNum] FROM [Cux].[AiQueryJobV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'24M148-H'
```

1. 视图：`Cux.AiQueryJobV`
2. 筛选条件：`ProjectID = '24M148-H'`
3. 查询字段：`ProjectID`、`JobNum`
4. 其他关键字内容：空

## 3.4 查询24M148-H共有多少张工单

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], COUNT(DISTINCT LTRIM(RTRIM([JobNum]))) AS [JobCount] FROM [Cux].[AiQueryJobV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'24M148-H' GROUP BY LTRIM(RTRIM([ProjectID]))
```

1. 视图：`Cux.AiQueryJobV`
2. 筛选条件：`ProjectID = '24M148-H'`
3. 查询字段：`ProjectID`、`JobNum`
4. 其他关键字内容：`COUNT(DISTINCT JobNum)`、`GROUP BY ProjectID`

## 3.5 查询项目24M148-H最早合交期

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], MIN([ReqDueDate]) AS [EarliestReqDueDate] FROM [Cux].[AiQueryJobV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'24M148-H' GROUP BY LTRIM(RTRIM([ProjectID]))
```

1. 视图：`Cux.AiQueryJobV`
2. 筛选条件：`ProjectID = '24M148-H'`
3. 查询字段：`ProjectID`、`ReqDueDate`
4. 其他关键字内容：`MIN(ReqDueDate)`、`GROUP BY ProjectID`

## 3.6 查询项目24M148-H最晚合交期

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], MAX([ReqDueDate]) AS [LatestReqDueDate] FROM [Cux].[AiQueryJobV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'24M148-H' GROUP BY LTRIM(RTRIM([ProjectID]))
```

1. 视图：`Cux.AiQueryJobV`
2. 筛选条件：`ProjectID = '24M148-H'`
3. 查询字段：`ProjectID`、`ReqDueDate`
4. 其他关键字内容：`MAX(ReqDueDate)`、`GROUP BY ProjectID`

## 3.7 查询项目号24M148-A的工单数量

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], COUNT(DISTINCT LTRIM(RTRIM([JobNum]))) AS [JobCount] FROM [Cux].[AiQueryJobV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'24M148-A' GROUP BY LTRIM(RTRIM([ProjectID]))
```

1. 视图：`Cux.AiQueryJobV`
2. 筛选条件：`ProjectID = '24M148-A'`
3. 查询字段：`ProjectID`、`JobNum`
4. 其他关键字内容：`COUNT(DISTINCT JobNum)`、`GROUP BY ProjectID`

## 3.8 查询项目24M148-A的合交期

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([JobNum])) AS [JobNum], [ReqDueDate] AS [ReqDueDate] FROM [Cux].[AiQueryJobV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'24M148-A'
```

1. 视图：`Cux.AiQueryJobV`
2. 筛选条件：`ProjectID = '24M148-A'`
3. 查询字段：`ProjectID`、`JobNum`、`ReqDueDate`
4. 其他关键字内容：空

## 3.9 查询A240024对应的工单数量

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], COUNT(DISTINCT LTRIM(RTRIM([JobNum]))) AS [JobCount] FROM [Cux].[AiQueryJobV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'A240024' GROUP BY LTRIM(RTRIM([ProjectID]))
```

1. 视图：`Cux.AiQueryJobV`
2. 筛选条件：`ProjectID = 'A240024'`
3. 查询字段：`ProjectID`、`JobNum`
4. 其他关键字内容：`COUNT(DISTINCT JobNum)`、`GROUP BY ProjectID`

## 3.10 查询A240024的合交期

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([JobNum])) AS [JobNum], [ReqDueDate] AS [ReqDueDate] FROM [Cux].[AiQueryJobV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'A240024'
```

1. 视图：`Cux.AiQueryJobV`
2. 筛选条件：`ProjectID = 'A240024'`
3. 查询字段：`ProjectID`、`JobNum`、`ReqDueDate`
4. 其他关键字内容：空

## 4.1 查询描述为16Mn钢板30的物料编码

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartDescription])) = N'16Mn钢板30'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription = '16Mn钢板30'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 4.2 查询描述为40Cr钢板55的物料编码

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartDescription])) = N'40Cr钢板55'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription = '40Cr钢板55'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 4.3 查询描述为45#钢板12的物料编码

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartDescription])) = N'45#钢板12'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription = '45#钢板12'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 4.4 查询描述包含钢板的物料编码

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE [PartDescription] LIKE N'%钢板%'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription LIKE '%钢板%'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 4.5 查询描述包含40Cr的物料编码

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE [PartDescription] LIKE N'%40Cr%'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription LIKE '%40Cr%'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 4.6 查询16Mn钢板30对应的编码

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartDescription])) = N'16Mn钢板30'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription = '16Mn钢板30'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 4.7 帮我找一下40Cr钢板55的料号

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartDescription])) = N'40Cr钢板55'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription = '40Cr钢板55'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 4.8 查询名称为45#钢板12的物料编号

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartDescription])) = N'45#钢板12'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription = '45#钢板12'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 4.9 描述里有钢板30的物料编码有哪些

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE [PartDescription] LIKE N'%钢板30%'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription LIKE '%钢板30%'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 4.10 查询16Mn钢板30是否已有物料编码

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartDescription])) = N'16Mn钢板30'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription = '16Mn钢板30'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 5.1 查询描述为齿条,M5L1200H50S75的采购订单号

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], ISNULL([PONum], 0) AS [PONum] FROM [Cux].[AiQueryPoProgressV] WITH(NOLOCK) WHERE LTRIM(RTRIM([LineDesc])) = N'齿条,M5L1200H50S75'
```

1. 视图：`Cux.AiQueryPoProgressV`
2. 筛选条件：`LineDesc = '齿条,M5L1200H50S75'`
3. 查询字段：`PartNum`、`LineDesc`、`PONum`
4. 其他关键字内容：空

## 5.2 查询描述为齿条,M5L1200H50S75的供应商

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], LTRIM(RTRIM([VendorName])) AS [VendorName], ISNULL([PONum], 0) AS [PONum] FROM [Cux].[AiQueryPoProgressV] WITH(NOLOCK) WHERE LTRIM(RTRIM([LineDesc])) = N'齿条,M5L1200H50S75'
```

1. 视图：`Cux.AiQueryPoProgressV`
2. 筛选条件：`LineDesc = '齿条,M5L1200H50S75'`
3. 查询字段：`PartNum`、`LineDesc`、`VendorName`、`PONum`
4. 其他关键字内容：空

## 5.3 查询描述为齿条,M5L1200H50S75的下单时间和需求时间

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], [OrderDate] AS [OrderDate], [DueDate] AS [DueDate] FROM [Cux].[AiQueryPoProgressV] WITH(NOLOCK) WHERE LTRIM(RTRIM([LineDesc])) = N'齿条,M5L1200H50S75'
```

1. 视图：`Cux.AiQueryPoProgressV`
2. 筛选条件：`LineDesc = '齿条,M5L1200H50S75'`
3. 查询字段：`PartNum`、`LineDesc`、`OrderDate`、`DueDate`
4. 其他关键字内容：空

## 5.4 查询描述为齿条,M5L1200H50S75的收货数量和在检数量

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], ISNULL([ReceivedQty], 0) AS [ReceivedQty], ISNULL([InspectionQty], 0) AS [InspectionQty] FROM [Cux].[AiQueryPoProgressV] WITH(NOLOCK) WHERE LTRIM(RTRIM([LineDesc])) = N'齿条,M5L1200H50S75'
```

1. 视图：`Cux.AiQueryPoProgressV`
2. 筛选条件：`LineDesc = '齿条,M5L1200H50S75'`
3. 查询字段：`PartNum`、`LineDesc`、`ReceivedQty`、`InspectionQty`
4. 其他关键字内容：空

## 5.5 查询描述为齿条,M5L1200H50S75的收货净值

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], ISNULL([NetReceivedQty], 0) AS [NetReceivedQty] FROM [Cux].[AiQueryPoProgressV] WITH(NOLOCK) WHERE LTRIM(RTRIM([LineDesc])) = N'齿条,M5L1200H50S75'
```

1. 视图：`Cux.AiQueryPoProgressV`
2. 筛选条件：`LineDesc = '齿条,M5L1200H50S75'`
3. 查询字段：`PartNum`、`LineDesc`、`NetReceivedQty`
4. 其他关键字内容：空

## 5.6 查询描述为瓷管,φ30*φ24*500的采购订单和供应商

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], LTRIM(RTRIM([VendorName])) AS [VendorName], ISNULL([PONum], 0) AS [PONum] FROM [Cux].[AiQueryPoProgressV] WITH(NOLOCK) WHERE LTRIM(RTRIM([LineDesc])) = N'瓷管,φ30*φ24*500'
```

1. 视图：`Cux.AiQueryPoProgressV`
2. 筛选条件：`LineDesc = '瓷管,φ30*φ24*500'`
3. 查询字段：`PartNum`、`LineDesc`、`VendorName`、`PONum`
4. 其他关键字内容：空

## 5.7 查询描述为瓷管,φ30*φ24*500的下单时间

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], [OrderDate] AS [OrderDate] FROM [Cux].[AiQueryPoProgressV] WITH(NOLOCK) WHERE LTRIM(RTRIM([LineDesc])) = N'瓷管,φ30*φ24*500'
```

1. 视图：`Cux.AiQueryPoProgressV`
2. 筛选条件：`LineDesc = '瓷管,φ30*φ24*500'`
3. 查询字段：`PartNum`、`LineDesc`、`OrderDate`
4. 其他关键字内容：空

## 5.8 查询描述为瓷管,φ30*φ24*500的收货数量

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], ISNULL([ReceivedQty], 0) AS [ReceivedQty] FROM [Cux].[AiQueryPoProgressV] WITH(NOLOCK) WHERE LTRIM(RTRIM([LineDesc])) = N'瓷管,φ30*φ24*500'
```

1. 视图：`Cux.AiQueryPoProgressV`
2. 筛选条件：`LineDesc = '瓷管,φ30*φ24*500'`
3. 查询字段：`PartNum`、`LineDesc`、`ReceivedQty`
4. 其他关键字内容：空

## 5.9 查询物料Z01.02.0026的采购到货进度

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], ISNULL([PONum], 0) AS [PONum], LTRIM(RTRIM([VendorName])) AS [VendorName], [OrderDate] AS [OrderDate], [DueDate] AS [DueDate], ISNULL([OrderQty], 0) AS [OrderQty], ISNULL([ReceivedQty], 0) AS [ReceivedQty], ISNULL([InspectionQty], 0) AS [InspectionQty], ISNULL([NetReceivedQty], 0) AS [NetReceivedQty] FROM [Cux].[AiQueryPoProgressV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'Z01.02.0026'
```

1. 视图：`Cux.AiQueryPoProgressV`
2. 筛选条件：`PartNum = 'Z01.02.0026'`
3. 查询字段：`PartNum`、`LineDesc`、`PONum`、`VendorName`、`OrderDate`、`DueDate`、`OrderQty`、`ReceivedQty`、`InspectionQty`、`NetReceivedQty`
4. 其他关键字内容：空

## 5.10 查询物料Z440300054的采购进度明细

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], ISNULL([PONum], 0) AS [PONum], LTRIM(RTRIM([VendorName])) AS [VendorName], [OrderDate] AS [OrderDate], [DueDate] AS [DueDate], ISNULL([OrderQty], 0) AS [OrderQty], ISNULL([ReceivedQty], 0) AS [ReceivedQty], ISNULL([InspectionQty], 0) AS [InspectionQty], ISNULL([NetReceivedQty], 0) AS [NetReceivedQty] FROM [Cux].[AiQueryPoProgressV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'Z440300054'
```

1. 视图：`Cux.AiQueryPoProgressV`
2. 筛选条件：`PartNum = 'Z440300054'`
3. 查询字段：`PartNum`、`LineDesc`、`PONum`、`VendorName`、`OrderDate`、`DueDate`、`OrderQty`、`ReceivedQty`、`InspectionQty`、`NetReceivedQty`
4. 其他关键字内容：空

## 6.1 查询描述为Q235钢板8的物料编码

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartDescription])) = N'Q235钢板8'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription = 'Q235钢板8'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 6.2 查询描述为GCr15圆钢Φ45的库位

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], LTRIM(RTRIM([BinNum])) AS [BinNum] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartDescription])) = N'GCr15圆钢Φ45'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartDescription = 'GCr15圆钢Φ45'`
3. 查询字段：`PartNum`、`PartDescription`、`BinNum`
4. 其他关键字内容：空

## 6.3 查询描述为GCr15圆钢Φ45的库位名称

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], LTRIM(RTRIM([BinName])) AS [BinName] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartDescription])) = N'GCr15圆钢Φ45'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartDescription = 'GCr15圆钢Φ45'`
3. 查询字段：`PartNum`、`PartDescription`、`BinName`
4. 其他关键字内容：空

## 6.4 查询描述为20#无缝管Φ180x40的物料编码

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartDescription])) = N'20#无缝管Φ180x40'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription = '20#无缝管Φ180x40'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 6.5 查询描述为GCr15圆钢Φ45的库位

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], LTRIM(RTRIM([BinNum])) AS [BinNum] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartDescription])) = N'GCr15圆钢Φ45'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartDescription = 'GCr15圆钢Φ45'`
3. 查询字段：`PartNum`、`PartDescription`、`BinNum`
4. 其他关键字内容：空

## 6.6 查询描述为GCr15圆钢Φ45的库位名称

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], LTRIM(RTRIM([BinName])) AS [BinName] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartDescription])) = N'GCr15圆钢Φ45'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartDescription = 'GCr15圆钢Φ45'`
3. 查询字段：`PartNum`、`PartDescription`、`BinName`
4. 其他关键字内容：空

## 6.7 查询描述包含钢板8的物料编码和库位

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], LTRIM(RTRIM([BinNum])) AS [BinNum] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE [PartDescription] LIKE N'%钢板8%'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartDescription LIKE '%钢板8%'`
3. 查询字段：`PartNum`、`PartDescription`、`BinNum`
4. 其他关键字内容：空

## 6.8 查询描述包含无缝管的物料编码和库位

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], LTRIM(RTRIM([BinNum])) AS [BinNum] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE [PartDescription] LIKE N'%无缝管%'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartDescription LIKE '%无缝管%'`
3. 查询字段：`PartNum`、`PartDescription`、`BinNum`
4. 其他关键字内容：空

## 6.9 查询GCr15圆钢Φ45存放在哪个库位

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], LTRIM(RTRIM([BinNum])) AS [BinNum], LTRIM(RTRIM([BinName])) AS [BinName] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartDescription])) = N'GCr15圆钢Φ45'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartDescription = 'GCr15圆钢Φ45'`
3. 查询字段：`PartNum`、`PartDescription`、`BinNum`、`BinName`
4. 其他关键字内容：空

## 6.10 查询GCr15圆钢Φ45在哪个库位

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], LTRIM(RTRIM([BinNum])) AS [BinNum], LTRIM(RTRIM([BinName])) AS [BinName] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartDescription])) = N'GCr15圆钢Φ45'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartDescription = 'GCr15圆钢Φ45'`
3. 查询字段：`PartNum`、`PartDescription`、`BinNum`、`BinName`
4. 其他关键字内容：空

## 7.1 查询描述为16Mn钢板30的物料编码

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartDescription])) = N'16Mn钢板30'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription = '16Mn钢板30'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 7.2 查询描述为40Cr钢板55的物料编码

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartDescription])) = N'40Cr钢板55'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription = '40Cr钢板55'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 7.3 查询编码110000001的物料描述

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'110000001'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartNum = '110000001'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 7.4 查询编码110000002的物料描述

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'110000002'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartNum = '110000002'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 7.5 查询编码包含11000000的物料描述

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE [PartNum] LIKE N'%11000000%'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartNum LIKE '%11000000%'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 7.6 查询编码包含11000001的物料描述

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE [PartNum] LIKE N'%11000001%'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartNum LIKE '%11000001%'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 7.7 查询16Mn钢板30对应的料号

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartDescription])) = N'16Mn钢板30'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription = '16Mn钢板30'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 7.8 查询110000001是什么物料

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'110000001'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartNum = '110000001'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 7.9 通过部分编码1100000查询物料描述

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE [PartNum] LIKE N'%1100000%'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartNum LIKE '%1100000%'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 7.10 通过描述包含钢板查询物料编码

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE [PartDescription] LIKE N'%钢板%'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription LIKE '%钢板%'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 8.1 查询物料编码120000019的现有量

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([Qty], 0) AS [Qty] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'120000019'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartNum = '120000019'`
3. 查询字段：`PartNum`、`PartDescription`、`Qty`
4. 其他关键字内容：空

## 8.2 查询物料编码120000019的现有量

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([Qty], 0) AS [Qty] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'120000019'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartNum = '120000019'`
3. 查询字段：`PartNum`、`PartDescription`、`Qty`
4. 其他关键字内容：空

## 8.3 查询物料描述GCr15圆钢Φ45的现有量

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([Qty], 0) AS [Qty] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartDescription])) = N'GCr15圆钢Φ45'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartDescription = 'GCr15圆钢Φ45'`
3. 查询字段：`PartNum`、`PartDescription`、`Qty`
4. 其他关键字内容：空

## 8.4 查询物料描述GCr15圆钢Φ45的现有量

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([Qty], 0) AS [Qty] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartDescription])) = N'GCr15圆钢Φ45'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartDescription = 'GCr15圆钢Φ45'`
3. 查询字段：`PartNum`、`PartDescription`、`Qty`
4. 其他关键字内容：空

## 8.5 查询120000019当前库存有多少

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([Qty], 0) AS [Qty] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'120000019'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartNum = '120000019'`
3. 查询字段：`PartNum`、`PartDescription`、`Qty`
4. 其他关键字内容：空

## 8.6 查询120000019库存数量

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([Qty], 0) AS [Qty] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'120000019'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartNum = '120000019'`
3. 查询字段：`PartNum`、`PartDescription`、`Qty`
4. 其他关键字内容：空

## 8.7 查询GCr15圆钢Φ45库存数量

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([Qty], 0) AS [Qty] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartDescription])) = N'GCr15圆钢Φ45'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartDescription = 'GCr15圆钢Φ45'`
3. 查询字段：`PartNum`、`PartDescription`、`Qty`
4. 其他关键字内容：空

## 8.8 查询GCr15圆钢Φ45还有多少库存

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([Qty], 0) AS [Qty] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartDescription])) = N'GCr15圆钢Φ45'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartDescription = 'GCr15圆钢Φ45'`
3. 查询字段：`PartNum`、`PartDescription`、`Qty`
4. 其他关键字内容：空

## 8.9 查询编码120000019和描述GCr15圆钢Φ45的现有量

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([Qty], 0) AS [Qty] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'120000019' AND LTRIM(RTRIM([PartDescription])) = N'GCr15圆钢Φ45'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartNum = '120000019' AND PartDescription = 'GCr15圆钢Φ45'`
3. 查询字段：`PartNum`、`PartDescription`、`Qty`
4. 其他关键字内容：空

## 8.10 查询描述包含无缝管的现有量

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([Qty], 0) AS [Qty] FROM [Cux].[AiQueryPartOnHandV] WITH(NOLOCK) WHERE [PartDescription] LIKE N'%无缝管%'
```

1. 视图：`Cux.AiQueryPartOnHandV`
2. 筛选条件：`PartDescription LIKE '%无缝管%'`
3. 查询字段：`PartNum`、`PartDescription`、`Qty`
4. 其他关键字内容：空

## 9.1 查询物料编码6100002502用于哪个上级部件

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryBomV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ECOMtl_MtlPartNum])) = N'6100002502'
```

1. 视图：`Cux.AiQueryBomV`
2. 筛选条件：`ECOMtl_MtlPartNum = '6100002502'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 9.2 查询物料编码6100002529用于哪个上级部件

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryBomV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ECOMtl_MtlPartNum])) = N'6100002529'
```

1. 视图：`Cux.AiQueryBomV`
2. 筛选条件：`ECOMtl_MtlPartNum = '6100002529'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 9.3 查询描述包含KTP700 Basic的物料用于哪个部件

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryBomV] WITH(NOLOCK) WHERE [MtlPartDescription] LIKE N'%KTP700 Basic%'
```

1. 视图：`Cux.AiQueryBomV`
2. 筛选条件：`MtlPartDescription LIKE '%KTP700 Basic%'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 9.4 查询描述包含CPU 1512C-1PN的物料用于哪个部件

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryBomV] WITH(NOLOCK) WHERE [MtlPartDescription] LIKE N'%CPU 1512C-1PN%'
```

1. 视图：`Cux.AiQueryBomV`
2. 筛选条件：`MtlPartDescription LIKE '%CPU 1512C-1PN%'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 9.5 查询6100002502对应的上级部件名称

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryBomV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ECOMtl_MtlPartNum])) = N'6100002502'
```

1. 视图：`Cux.AiQueryBomV`
2. 筛选条件：`ECOMtl_MtlPartNum = '6100002502'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 9.6 查询6100002529的上级部件描述

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryBomV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ECOMtl_MtlPartNum])) = N'6100002529'
```

1. 视图：`Cux.AiQueryBomV`
2. 筛选条件：`ECOMtl_MtlPartNum = '6100002529'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 9.7 查询HMI这项物料属于哪个部件

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryBomV] WITH(NOLOCK) WHERE [MtlPartDescription] LIKE N'%HMI%'
```

1. 视图：`Cux.AiQueryBomV`
2. 筛选条件：`MtlPartDescription LIKE '%HMI%'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 9.8 查询PLC这项物料属于哪个上级部件

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryBomV] WITH(NOLOCK) WHERE [MtlPartDescription] LIKE N'%PLC%'
```

1. 视图：`Cux.AiQueryBomV`
2. 筛选条件：`MtlPartDescription LIKE '%PLC%'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 9.9 查询物料描述包含Siemens的子件用于哪个部件

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryBomV] WITH(NOLOCK) WHERE [MtlPartDescription] LIKE N'%Siemens%'
```

1. 视图：`Cux.AiQueryBomV`
2. 筛选条件：`MtlPartDescription LIKE '%Siemens%'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 9.10 查询物料描述包含触摸式操作的物料用于哪个上级部件

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryBomV] WITH(NOLOCK) WHERE [MtlPartDescription] LIKE N'%触摸式操作%'
```

1. 视图：`Cux.AiQueryBomV`
2. 筛选条件：`MtlPartDescription LIKE '%触摸式操作%'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 10.1 查询工单000022的报工数量

```sql
SELECT LTRIM(RTRIM([JobNum])) AS [JobNum], LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([LaborQty], 0) AS [LaborQty] FROM [Cux].[AiQueryJobProgressV] WITH(NOLOCK) WHERE LTRIM(RTRIM([JobNum])) = N'000022'
```

1. 视图：`Cux.AiQueryJobProgressV`
2. 筛选条件：`JobNum = '000022'`
3. 查询字段：`JobNum`、`PartNum`、`PartDescription`、`LaborQty`
4. 其他关键字内容：空

## 10.2 查询工单000022的末道工序完工数量

```sql
SELECT LTRIM(RTRIM([JobNum])) AS [JobNum], LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([JobOprCompQty], 0) AS [JobOprCompQty] FROM [Cux].[AiQueryJobProgressV] WITH(NOLOCK) WHERE LTRIM(RTRIM([JobNum])) = N'000022'
```

1. 视图：`Cux.AiQueryJobProgressV`
2. 筛选条件：`JobNum = '000022'`
3. 查询字段：`JobNum`、`PartNum`、`PartDescription`、`JobOprCompQty`
4. 其他关键字内容：空

## 10.3 查询工单000022的报工数量和末道工序完工数量

```sql
SELECT LTRIM(RTRIM([JobNum])) AS [JobNum], LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([LaborQty], 0) AS [LaborQty], ISNULL([JobOprCompQty], 0) AS [JobOprCompQty] FROM [Cux].[AiQueryJobProgressV] WITH(NOLOCK) WHERE LTRIM(RTRIM([JobNum])) = N'000022'
```

1. 视图：`Cux.AiQueryJobProgressV`
2. 筛选条件：`JobNum = '000022'`
3. 查询字段：`JobNum`、`PartNum`、`PartDescription`、`LaborQty`、`JobOprCompQty`
4. 其他关键字内容：空

## 10.4 查询工单000023的报工数量

```sql
SELECT LTRIM(RTRIM([JobNum])) AS [JobNum], LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([LaborQty], 0) AS [LaborQty] FROM [Cux].[AiQueryJobProgressV] WITH(NOLOCK) WHERE LTRIM(RTRIM([JobNum])) = N'000023'
```

1. 视图：`Cux.AiQueryJobProgressV`
2. 筛选条件：`JobNum = '000023'`
3. 查询字段：`JobNum`、`PartNum`、`PartDescription`、`LaborQty`
4. 其他关键字内容：空

## 10.5 查询工单000023的末道工序完工数量

```sql
SELECT LTRIM(RTRIM([JobNum])) AS [JobNum], LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([JobOprCompQty], 0) AS [JobOprCompQty] FROM [Cux].[AiQueryJobProgressV] WITH(NOLOCK) WHERE LTRIM(RTRIM([JobNum])) = N'000023'
```

1. 视图：`Cux.AiQueryJobProgressV`
2. 筛选条件：`JobNum = '000023'`
3. 查询字段：`JobNum`、`PartNum`、`PartDescription`、`JobOprCompQty`
4. 其他关键字内容：空

## 10.6 查询工单000023的完工入库数量

```sql
SELECT LTRIM(RTRIM([JobNum])) AS [JobNum], LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([JobOprCompQty], 0) AS [JobOprCompQty] FROM [Cux].[AiQueryJobProgressV] WITH(NOLOCK) WHERE LTRIM(RTRIM([JobNum])) = N'000023'
```

1. 视图：`Cux.AiQueryJobProgressV`
2. 筛选条件：`JobNum = '000023'`
3. 查询字段：`JobNum`、`PartNum`、`PartDescription`、`JobOprCompQty`
4. 其他关键字内容：空

## 10.7 查询000022目前报工到多少

```sql
SELECT LTRIM(RTRIM([JobNum])) AS [JobNum], LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([LaborQty], 0) AS [LaborQty] FROM [Cux].[AiQueryJobProgressV] WITH(NOLOCK) WHERE LTRIM(RTRIM([JobNum])) = N'000022'
```

1. 视图：`Cux.AiQueryJobProgressV`
2. 筛选条件：`JobNum = '000022'`
3. 查询字段：`JobNum`、`PartNum`、`PartDescription`、`LaborQty`
4. 其他关键字内容：空

## 10.8 查询000022最后一道工序完工多少

```sql
SELECT LTRIM(RTRIM([JobNum])) AS [JobNum], LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([JobOprCompQty], 0) AS [JobOprCompQty] FROM [Cux].[AiQueryJobProgressV] WITH(NOLOCK) WHERE LTRIM(RTRIM([JobNum])) = N'000022'
```

1. 视图：`Cux.AiQueryJobProgressV`
2. 筛选条件：`JobNum = '000022'`
3. 查询字段：`JobNum`、`PartNum`、`PartDescription`、`JobOprCompQty`
4. 其他关键字内容：空

## 10.9 查询000023的工单进度

```sql
SELECT LTRIM(RTRIM([JobNum])) AS [JobNum], LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([JobQty], 0) AS [JobQty], ISNULL([LaborQty], 0) AS [LaborQty], ISNULL([JobOprCompQty], 0) AS [JobOprCompQty] FROM [Cux].[AiQueryJobProgressV] WITH(NOLOCK) WHERE LTRIM(RTRIM([JobNum])) = N'000023'
```

1. 视图：`Cux.AiQueryJobProgressV`
2. 筛选条件：`JobNum = '000023'`
3. 查询字段：`JobNum`、`PartNum`、`PartDescription`、`JobQty`、`LaborQty`、`JobOprCompQty`
4. 其他关键字内容：空

## 10.10 查询工单000023的报工和完工情况

```sql
SELECT LTRIM(RTRIM([JobNum])) AS [JobNum], LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([LaborQty], 0) AS [LaborQty], ISNULL([JobOprCompQty], 0) AS [JobOprCompQty] FROM [Cux].[AiQueryJobProgressV] WITH(NOLOCK) WHERE LTRIM(RTRIM([JobNum])) = N'000023'
```

1. 视图：`Cux.AiQueryJobProgressV`
2. 筛选条件：`JobNum = '000023'`
3. 查询字段：`JobNum`、`PartNum`、`PartDescription`、`LaborQty`、`JobOprCompQty`
4. 其他关键字内容：空

## 11.1 查询采购订单300018332的订单数量、收货数量、开票数量和未结数量

```sql
SELECT ISNULL([PONum], 0) AS [PONum], ISNULL([OrderQty], 0) AS [OrderQty], ISNULL([ReceivedQty], 0) AS [ReceivedQty], ISNULL([InvoiceQty], 0) AS [InvoiceQty], ISNULL([RemainQty], 0) AS [RemainQty] FROM [Cux].[AiQueryPoOverViewV] WITH(NOLOCK) WHERE [PONum] = 300018332
```

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`PONum = 300018332`
3. 查询字段：`PONum`、`OrderQty`、`ReceivedQty`、`InvoiceQty`、`RemainQty`
4. 其他关键字内容：空

## 11.2 查询采购订单300018845的订单数量、收货数量、开票数量和未结数量

```sql
SELECT ISNULL([PONum], 0) AS [PONum], ISNULL([OrderQty], 0) AS [OrderQty], ISNULL([ReceivedQty], 0) AS [ReceivedQty], ISNULL([InvoiceQty], 0) AS [InvoiceQty], ISNULL([RemainQty], 0) AS [RemainQty] FROM [Cux].[AiQueryPoOverViewV] WITH(NOLOCK) WHERE [PONum] = 300018845
```

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`PONum = 300018845`
3. 查询字段：`PONum`、`OrderQty`、`ReceivedQty`、`InvoiceQty`、`RemainQty`
4. 其他关键字内容：空

## 11.3 查询物料编码6206320的采购追踪信息

```sql
SELECT ISNULL([PONum], 0) AS [PONum], LTRIM(RTRIM([Vendor_Name])) AS [Vendor_Name], [OrderDate] AS [OrderDate], LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], ISNULL([OrderQty], 0) AS [OrderQty], [DueDate] AS [DueDate], ISNULL([ReceivedQty], 0) AS [ReceivedQty], ISNULL([InvoiceQty], 0) AS [InvoiceQty], ISNULL([RemainQty], 0) AS [RemainQty], LTRIM(RTRIM([ApproveStatus_c])) AS [ApproveStatus_c] FROM [Cux].[AiQueryPoOverViewV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'6206320'
```

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`PartNum = '6206320'`
3. 查询字段：`PONum`、`Vendor_Name`、`OrderDate`、`PartNum`、`LineDesc`、`OrderQty`、`DueDate`、`ReceivedQty`、`InvoiceQty`、`RemainQty`、`ApproveStatus_c`
4. 其他关键字内容：空

## 11.4 查询描述为威图悬臂箱底座，A250063的采购追踪信息

```sql
SELECT ISNULL([PONum], 0) AS [PONum], LTRIM(RTRIM([Vendor_Name])) AS [Vendor_Name], [OrderDate] AS [OrderDate], LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], ISNULL([OrderQty], 0) AS [OrderQty], [DueDate] AS [DueDate], ISNULL([ReceivedQty], 0) AS [ReceivedQty], ISNULL([InvoiceQty], 0) AS [InvoiceQty], ISNULL([RemainQty], 0) AS [RemainQty], LTRIM(RTRIM([ApproveStatus_c])) AS [ApproveStatus_c] FROM [Cux].[AiQueryPoOverViewV] WITH(NOLOCK) WHERE LTRIM(RTRIM([LineDesc])) = N'威图悬臂箱底座，A250063'
```

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`LineDesc = '威图悬臂箱底座，A250063'`
3. 查询字段：`PONum`、`Vendor_Name`、`OrderDate`、`PartNum`、`LineDesc`、`OrderQty`、`DueDate`、`ReceivedQty`、`InvoiceQty`、`RemainQty`、`ApproveStatus_c`
4. 其他关键字内容：空

## 11.5 查询描述为施瓦茨项目悬臂使用底座的采购追踪信息

```sql
SELECT ISNULL([PONum], 0) AS [PONum], LTRIM(RTRIM([Vendor_Name])) AS [Vendor_Name], [OrderDate] AS [OrderDate], LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], ISNULL([OrderQty], 0) AS [OrderQty], [DueDate] AS [DueDate], ISNULL([ReceivedQty], 0) AS [ReceivedQty], ISNULL([InvoiceQty], 0) AS [InvoiceQty], ISNULL([RemainQty], 0) AS [RemainQty], LTRIM(RTRIM([ApproveStatus_c])) AS [ApproveStatus_c] FROM [Cux].[AiQueryPoOverViewV] WITH(NOLOCK) WHERE LTRIM(RTRIM([LineDesc])) = N'施瓦茨项目悬臂使用底座'
```

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`LineDesc = '施瓦茨项目悬臂使用底座'`
3. 查询字段：`PONum`、`Vendor_Name`、`OrderDate`、`PartNum`、`LineDesc`、`OrderQty`、`DueDate`、`ReceivedQty`、`InvoiceQty`、`RemainQty`、`ApproveStatus_c`
4. 其他关键字内容：空

## 11.6 查询供应商卡尔松（常州）电气有限公司的采购订单数量和收货数量

```sql
SELECT ISNULL([PONum], 0) AS [PONum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], ISNULL([OrderQty], 0) AS [OrderQty], ISNULL([ReceivedQty], 0) AS [ReceivedQty] FROM [Cux].[AiQueryPoOverViewV] WITH(NOLOCK) WHERE LTRIM(RTRIM([Vendor_Name])) = N'卡尔松（常州）电气有限公司'
```

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`Vendor_Name = '卡尔松（常州）电气有限公司'`
3. 查询字段：`PONum`、`LineDesc`、`OrderQty`、`ReceivedQty`
4. 其他关键字内容：空

## 11.7 查询2025年12月29日下单的采购记录

```sql
SELECT ISNULL([PONum], 0) AS [PONum], LTRIM(RTRIM([Vendor_Name])) AS [Vendor_Name], [OrderDate] AS [OrderDate], LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], ISNULL([OrderQty], 0) AS [OrderQty], [DueDate] AS [DueDate], ISNULL([ReceivedQty], 0) AS [ReceivedQty], ISNULL([InvoiceQty], 0) AS [InvoiceQty], ISNULL([RemainQty], 0) AS [RemainQty] FROM [Cux].[AiQueryPoOverViewV] WITH(NOLOCK) WHERE [OrderDate] >= '2025-12-29' AND [OrderDate] < '2025-12-30'
```

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`OrderDate >= '2025-12-29' AND OrderDate < '2025-12-30'`
3. 查询字段：`PONum`、`Vendor_Name`、`OrderDate`、`PartNum`、`LineDesc`、`OrderQty`、`DueDate`、`ReceivedQty`、`InvoiceQty`、`RemainQty`
4. 其他关键字内容：空

## 11.8 查询2026年1月8日下单的采购记录

```sql
SELECT ISNULL([PONum], 0) AS [PONum], LTRIM(RTRIM([Vendor_Name])) AS [Vendor_Name], [OrderDate] AS [OrderDate], LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], ISNULL([OrderQty], 0) AS [OrderQty], [DueDate] AS [DueDate], ISNULL([ReceivedQty], 0) AS [ReceivedQty], ISNULL([InvoiceQty], 0) AS [InvoiceQty], ISNULL([RemainQty], 0) AS [RemainQty] FROM [Cux].[AiQueryPoOverViewV] WITH(NOLOCK) WHERE [OrderDate] >= '2026-01-08' AND [OrderDate] < '2026-01-09'
```

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`OrderDate >= '2026-01-08' AND OrderDate < '2026-01-09'`
3. 查询字段：`PONum`、`Vendor_Name`、`OrderDate`、`PartNum`、`LineDesc`、`OrderQty`、`DueDate`、`ReceivedQty`、`InvoiceQty`、`RemainQty`
4. 其他关键字内容：空

## 11.9 查询采购单300018332的开票数量和未结数量

```sql
SELECT ISNULL([PONum], 0) AS [PONum], ISNULL([InvoiceQty], 0) AS [InvoiceQty], ISNULL([RemainQty], 0) AS [RemainQty] FROM [Cux].[AiQueryPoOverViewV] WITH(NOLOCK) WHERE [PONum] = 300018332
```

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`PONum = 300018332`
3. 查询字段：`PONum`、`InvoiceQty`、`RemainQty`
4. 其他关键字内容：空

## 11.10 查询供应商卡尔松（常州）电气有限公司在2026年1月的采购收货情况

```sql
SELECT ISNULL([PONum], 0) AS [PONum], [OrderDate] AS [OrderDate], LTRIM(RTRIM([LineDesc])) AS [LineDesc], ISNULL([OrderQty], 0) AS [OrderQty], ISNULL([ReceivedQty], 0) AS [ReceivedQty], ISNULL([InvoiceQty], 0) AS [InvoiceQty], ISNULL([RemainQty], 0) AS [RemainQty] FROM [Cux].[AiQueryPoOverViewV] WITH(NOLOCK) WHERE LTRIM(RTRIM([Vendor_Name])) = N'卡尔松（常州）电气有限公司' AND [OrderDate] >= '2026-01-01' AND [OrderDate] < '2026-02-01'
```

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`Vendor_Name = '卡尔松（常州）电气有限公司' AND OrderDate >= '2026-01-01' AND OrderDate < '2026-02-01'`
3. 查询字段：`PONum`、`OrderDate`、`LineDesc`、`OrderQty`、`ReceivedQty`、`InvoiceQty`、`RemainQty`
4. 其他关键字内容：空

## 12.1 查询采购订单300018332的审批状态

```sql
SELECT ISNULL([PONum], 0) AS [PONum], LTRIM(RTRIM([ApproveStatus_c])) AS [ApproveStatus_c] FROM [Cux].[AiQueryPoOverViewV] WITH(NOLOCK) WHERE [PONum] = 300018332
```

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`PONum = 300018332`
3. 查询字段：`PONum`、`ApproveStatus_c`
4. 其他关键字内容：空

## 12.2 查询采购订单300018332的审批状态和收货数量

```sql
SELECT ISNULL([PONum], 0) AS [PONum], LTRIM(RTRIM([ApproveStatus_c])) AS [ApproveStatus_c], ISNULL([ReceivedQty], 0) AS [ReceivedQty] FROM [Cux].[AiQueryPoOverViewV] WITH(NOLOCK) WHERE [PONum] = 300018332
```

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`PONum = 300018332`
3. 查询字段：`PONum`、`ApproveStatus_c`、`ReceivedQty`
4. 其他关键字内容：空

## 12.3 查询采购订单300018332的审批状态和开票数量

```sql
SELECT ISNULL([PONum], 0) AS [PONum], LTRIM(RTRIM([ApproveStatus_c])) AS [ApproveStatus_c], ISNULL([InvoiceQty], 0) AS [InvoiceQty] FROM [Cux].[AiQueryPoOverViewV] WITH(NOLOCK) WHERE [PONum] = 300018332
```

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`PONum = 300018332`
3. 查询字段：`PONum`、`ApproveStatus_c`、`InvoiceQty`
4. 其他关键字内容：空

## 12.4 查询采购订单300018845的审批状态

```sql
SELECT ISNULL([PONum], 0) AS [PONum], LTRIM(RTRIM([ApproveStatus_c])) AS [ApproveStatus_c] FROM [Cux].[AiQueryPoOverViewV] WITH(NOLOCK) WHERE [PONum] = 300018845
```

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`PONum = 300018845`
3. 查询字段：`PONum`、`ApproveStatus_c`
4. 其他关键字内容：空

## 12.5 查询采购订单300018845的审批状态和未结数量

```sql
SELECT ISNULL([PONum], 0) AS [PONum], LTRIM(RTRIM([ApproveStatus_c])) AS [ApproveStatus_c], ISNULL([RemainQty], 0) AS [RemainQty] FROM [Cux].[AiQueryPoOverViewV] WITH(NOLOCK) WHERE [PONum] = 300018845
```

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`PONum = 300018845`
3. 查询字段：`PONum`、`ApproveStatus_c`、`RemainQty`
4. 其他关键字内容：空

## 12.6 查询采购订单300018845的订单进度和审批状态

```sql
SELECT ISNULL([PONum], 0) AS [PONum], ISNULL([OrderQty], 0) AS [OrderQty], ISNULL([ReceivedQty], 0) AS [ReceivedQty], ISNULL([InvoiceQty], 0) AS [InvoiceQty], ISNULL([RemainQty], 0) AS [RemainQty], LTRIM(RTRIM([ApproveStatus_c])) AS [ApproveStatus_c] FROM [Cux].[AiQueryPoOverViewV] WITH(NOLOCK) WHERE [PONum] = 300018845
```

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`PONum = 300018845`
3. 查询字段：`PONum`、`OrderQty`、`ReceivedQty`、`InvoiceQty`、`RemainQty`、`ApproveStatus_c`
4. 其他关键字内容：空

## 12.7 查询300018332是否已审批

```sql
SELECT ISNULL([PONum], 0) AS [PONum], LTRIM(RTRIM([ApproveStatus_c])) AS [ApproveStatus_c], CASE WHEN LTRIM(RTRIM([ApproveStatus_c])) = N'Approved' THEN N'是' ELSE N'否' END AS [IsApproved] FROM [Cux].[AiQueryPoOverViewV] WITH(NOLOCK) WHERE [PONum] = 300018332
```

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`PONum = 300018332`
3. 查询字段：`PONum`、`ApproveStatus_c`
4. 其他关键字内容：`CASE WHEN ApproveStatus_c = 'Approved' THEN '是' ELSE '否' END`

## 12.8 查询300018845是否已审批

```sql
SELECT ISNULL([PONum], 0) AS [PONum], LTRIM(RTRIM([ApproveStatus_c])) AS [ApproveStatus_c], CASE WHEN LTRIM(RTRIM([ApproveStatus_c])) = N'Approved' THEN N'是' ELSE N'否' END AS [IsApproved] FROM [Cux].[AiQueryPoOverViewV] WITH(NOLOCK) WHERE [PONum] = 300018845
```

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`PONum = 300018845`
3. 查询字段：`PONum`、`ApproveStatus_c`
4. 其他关键字内容：`CASE WHEN ApproveStatus_c = 'Approved' THEN '是' ELSE '否' END`

## 12.9 查询采购订单300018332的审批状态、订单数量、收货数量

```sql
SELECT ISNULL([PONum], 0) AS [PONum], LTRIM(RTRIM([ApproveStatus_c])) AS [ApproveStatus_c], ISNULL([OrderQty], 0) AS [OrderQty], ISNULL([ReceivedQty], 0) AS [ReceivedQty] FROM [Cux].[AiQueryPoOverViewV] WITH(NOLOCK) WHERE [PONum] = 300018332
```

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`PONum = 300018332`
3. 查询字段：`PONum`、`ApproveStatus_c`、`OrderQty`、`ReceivedQty`
4. 其他关键字内容：空

## 12.10 查询采购订单300018845的审批状态、开票数量、未结数量

```sql
SELECT ISNULL([PONum], 0) AS [PONum], LTRIM(RTRIM([ApproveStatus_c])) AS [ApproveStatus_c], ISNULL([InvoiceQty], 0) AS [InvoiceQty], ISNULL([RemainQty], 0) AS [RemainQty] FROM [Cux].[AiQueryPoOverViewV] WITH(NOLOCK) WHERE [PONum] = 300018845
```

1. 视图：`Cux.AiQueryPoOverViewV`
2. 筛选条件：`PONum = 300018845`
3. 查询字段：`PONum`、`ApproveStatus_c`、`InvoiceQty`、`RemainQty`
4. 其他关键字内容：空

## 13.1 查询项目24M148-H的完工入库数量

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], SUM(ISNULL([CompleteQty], 0)) AS [TotalCompleteQty] FROM [Cux].[AiQueryProjectJobV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'24M148-H' AND LTRIM(RTRIM([JobHead_JobNum])) NOT LIKE N'%[^0-9]%' GROUP BY LTRIM(RTRIM([ProjectID]))
```

1. 视图：`Cux.AiQueryProjectJobV`
2. 筛选条件：`ProjectID = '24M148-H' AND JobHead_JobNum NOT LIKE '%[^0-9]%'`
3. 查询字段：`ProjectID`、`CompleteQty`
4. 其他关键字内容：`SUM(ISNULL(CompleteQty, 0))`、`GROUP BY ProjectID`

## 13.2 查询项目24M148-H的工单完工数量

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([JobHead_JobNum])) AS [JobHead_JobNum], ISNULL([CompleteQty], 0) AS [CompleteQty] FROM [Cux].[AiQueryProjectJobV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'24M148-H'
```

1. 视图：`Cux.AiQueryProjectJobV`
2. 筛选条件：`ProjectID = '24M148-H'`
3. 查询字段：`ProjectID`、`JobHead_JobNum`、`CompleteQty`
4. 其他关键字内容：空

## 13.3 查询项目24M148-H各工单完工数量

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([JobHead_JobNum])) AS [JobHead_JobNum], ISNULL([CompleteQty], 0) AS [CompleteQty] FROM [Cux].[AiQueryProjectJobV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'24M148-H'
```

1. 视图：`Cux.AiQueryProjectJobV`
2. 筛选条件：`ProjectID = '24M148-H'`
3. 查询字段：`ProjectID`、`JobHead_JobNum`、`CompleteQty`
4. 其他关键字内容：空

## 13.4 查询项目24M148-A的完工入库数量

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], SUM(ISNULL([CompleteQty], 0)) AS [TotalCompleteQty] FROM [Cux].[AiQueryProjectJobV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'24M148-A' AND LTRIM(RTRIM([JobHead_JobNum])) NOT LIKE N'%[^0-9]%' GROUP BY LTRIM(RTRIM([ProjectID]))
```

1. 视图：`Cux.AiQueryProjectJobV`
2. 筛选条件：`ProjectID = '24M148-A' AND JobHead_JobNum NOT LIKE '%[^0-9]%'`
3. 查询字段：`ProjectID`、`CompleteQty`
4. 其他关键字内容：`SUM(ISNULL(CompleteQty, 0))`、`GROUP BY ProjectID`

## 13.5 查询项目24M148-A的工单完工情况

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([JobHead_JobNum])) AS [JobHead_JobNum], ISNULL([JobHead_ProdQty], 0) AS [JobHead_ProdQty], ISNULL([CompleteQty], 0) AS [CompleteQty] FROM [Cux].[AiQueryProjectJobV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'24M148-A'
```

1. 视图：`Cux.AiQueryProjectJobV`
2. 筛选条件：`ProjectID = '24M148-A'`
3. 查询字段：`ProjectID`、`JobHead_JobNum`、`JobHead_ProdQty`、`CompleteQty`
4. 其他关键字内容：空

## 13.6 查询项目24M148-H对应工单000022的完工数量

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([JobHead_JobNum])) AS [JobHead_JobNum], ISNULL([CompleteQty], 0) AS [CompleteQty] FROM [Cux].[AiQueryProjectJobV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'24M148-H' AND LTRIM(RTRIM([JobHead_JobNum])) = N'000022'
```

1. 视图：`Cux.AiQueryProjectJobV`
2. 筛选条件：`ProjectID = '24M148-H' AND JobHead_JobNum = '000022'`
3. 查询字段：`ProjectID`、`JobHead_JobNum`、`CompleteQty`
4. 其他关键字内容：空

## 13.7 查询项目24M148-A对应工单000032的完工数量

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([JobHead_JobNum])) AS [JobHead_JobNum], ISNULL([CompleteQty], 0) AS [CompleteQty] FROM [Cux].[AiQueryProjectJobV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'24M148-A' AND LTRIM(RTRIM([JobHead_JobNum])) = N'000032'
```

1. 视图：`Cux.AiQueryProjectJobV`
2. 筛选条件：`ProjectID = '24M148-A' AND JobHead_JobNum = '000032'`
3. 查询字段：`ProjectID`、`JobHead_JobNum`、`CompleteQty`
4. 其他关键字内容：空

## 13.8 查询24M148-H是否全部完成

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], SUM(ISNULL([JobHead_ProdQty], 0)) AS [TotalProdQty], SUM(ISNULL([CompleteQty], 0)) AS [TotalCompleteQty], CASE WHEN SUM(ISNULL([CompleteQty], 0)) >= SUM(ISNULL([JobHead_ProdQty], 0)) AND SUM(ISNULL([JobHead_ProdQty], 0)) > 0 THEN N'是' ELSE N'否' END AS [IsFullyCompleted] FROM [Cux].[AiQueryProjectJobV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'24M148-H' AND LTRIM(RTRIM([JobHead_JobNum])) NOT LIKE N'%[^0-9]%' GROUP BY LTRIM(RTRIM([ProjectID]))
```

1. 视图：`Cux.AiQueryProjectJobV`
2. 筛选条件：`ProjectID = '24M148-H' AND JobHead_JobNum NOT LIKE '%[^0-9]%'`
3. 查询字段：`ProjectID`、`JobHead_ProdQty`、`CompleteQty`
4. 其他关键字内容：`SUM(ISNULL(JobHead_ProdQty, 0))`、`SUM(ISNULL(CompleteQty, 0))`、`CASE WHEN SUM(ISNULL(CompleteQty, 0)) >= SUM(ISNULL(JobHead_ProdQty, 0)) AND SUM(ISNULL(JobHead_ProdQty, 0)) > 0 THEN '是' ELSE '否' END`、`GROUP BY ProjectID`

## 13.9 查询24M148-A是否全部完成

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], SUM(ISNULL([JobHead_ProdQty], 0)) AS [TotalProdQty], SUM(ISNULL([CompleteQty], 0)) AS [TotalCompleteQty], CASE WHEN SUM(ISNULL([CompleteQty], 0)) >= SUM(ISNULL([JobHead_ProdQty], 0)) AND SUM(ISNULL([JobHead_ProdQty], 0)) > 0 THEN N'是' ELSE N'否' END AS [IsFullyCompleted] FROM [Cux].[AiQueryProjectJobV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'24M148-A' AND LTRIM(RTRIM([JobHead_JobNum])) NOT LIKE N'%[^0-9]%' GROUP BY LTRIM(RTRIM([ProjectID]))
```

1. 视图：`Cux.AiQueryProjectJobV`
2. 筛选条件：`ProjectID = '24M148-A' AND JobHead_JobNum NOT LIKE '%[^0-9]%'`
3. 查询字段：`ProjectID`、`JobHead_ProdQty`、`CompleteQty`
4. 其他关键字内容：`SUM(ISNULL(JobHead_ProdQty, 0))`、`SUM(ISNULL(CompleteQty, 0))`、`CASE WHEN SUM(ISNULL(CompleteQty, 0)) >= SUM(ISNULL(JobHead_ProdQty, 0)) AND SUM(ISNULL(JobHead_ProdQty, 0)) > 0 THEN '是' ELSE '否' END`、`GROUP BY ProjectID`

## 13.10 查询项目24M148-H和24M148-A的完工入库数量

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], SUM(ISNULL([CompleteQty], 0)) AS [TotalCompleteQty] FROM [Cux].[AiQueryProjectJobV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) IN (N'24M148-H', N'24M148-A') AND LTRIM(RTRIM([JobHead_JobNum])) NOT LIKE N'%[^0-9]%' GROUP BY LTRIM(RTRIM([ProjectID]))
```

1. 视图：`Cux.AiQueryProjectJobV`
2. 筛选条件：`ProjectID IN ('24M148-H', '24M148-A') AND JobHead_JobNum NOT LIKE '%[^0-9]%'`
3. 查询字段：`ProjectID`、`CompleteQty`
4. 其他关键字内容：`SUM(ISNULL(CompleteQty, 0))`、`GROUP BY ProjectID`

## 14.1 查询描述包含钢板的物料编码

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE [PartDescription] LIKE N'%钢板%'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription LIKE '%钢板%'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 14.2 查询描述包含无缝管的物料编码

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE [PartDescription] LIKE N'%无缝管%'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription LIKE '%无缝管%'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 14.3 查询描述包含16Mn的物料编码

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE [PartDescription] LIKE N'%16Mn%'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription LIKE '%16Mn%'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 14.4 查询描述包含40Cr的物料编码

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE [PartDescription] LIKE N'%40Cr%'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription LIKE '%40Cr%'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 14.5 查询描述包含角钢的物料编码

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE [PartDescription] LIKE N'%角钢%'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription LIKE '%角钢%'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 14.6 查询描述包含钢板30的物料是否存在

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE [PartDescription] LIKE N'%钢板30%'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription LIKE '%钢板30%'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 14.7 查询描述包含无缝管89x6的物料是否有编码

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE [PartDescription] LIKE N'%无缝管89x6%'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription LIKE '%无缝管89x6%'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 14.8 查询描述里有钢板8的物料编码

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE [PartDescription] LIKE N'%钢板8%'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription LIKE '%钢板8%'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 14.9 模糊查找描述包含45#钢板的料号

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE [PartDescription] LIKE N'%45#钢板%'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription LIKE '%45#钢板%'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 14.10 查询名称里带无缝管的物料编码列表

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription] FROM [Cux].[AiQueryPartV] WITH(NOLOCK) WHERE [PartDescription] LIKE N'%无缝管%'
```

1. 视图：`Cux.AiQueryPartV`
2. 筛选条件：`PartDescription LIKE '%无缝管%'`
3. 查询字段：`PartNum`、`PartDescription`
4. 其他关键字内容：空

## 15.1 查询销售订单293的订单日期和客户名称

```sql
SELECT ISNULL([OrderNum], 0) AS [OrderNum], [OrderDate] AS [OrderDate], LTRIM(RTRIM([Customer_Name])) AS [Customer_Name] FROM [Cux].[AiQuerySoOverViewV] WITH(NOLOCK) WHERE [OrderNum] = 293
```

1. 视图：`Cux.AiQuerySoOverViewV`
2. 筛选条件：`OrderNum = 293`
3. 查询字段：`OrderNum`、`OrderDate`、`Customer_Name`
4. 其他关键字内容：空

## 15.2 查询销售订单293的物料描述和订单数量

```sql
SELECT ISNULL([OrderNum], 0) AS [OrderNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], ISNULL([OrderQty], 0) AS [OrderQty] FROM [Cux].[AiQuerySoOverViewV] WITH(NOLOCK) WHERE [OrderNum] = 293
```

1. 视图：`Cux.AiQuerySoOverViewV`
2. 筛选条件：`OrderNum = 293`
3. 查询字段：`OrderNum`、`LineDesc`、`OrderQty`
4. 其他关键字内容：空

## 15.3 查询销售订单293的行金额和订单金额

```sql
SELECT ISNULL([OrderNum], 0) AS [OrderNum], LTRIM(RTRIM([CurrencyCode])) AS [CurrencyCode], ISNULL([DocLineAmount], 0) AS [DocLineAmount], ISNULL([LineAmount], 0) AS [LineAmount], ISNULL([DocOrderAmt], 0) AS [DocOrderAmt], ISNULL([OrderAmt], 0) AS [OrderAmt] FROM [Cux].[AiQuerySoOverViewV] WITH(NOLOCK) WHERE [OrderNum] = 293
```

1. 视图：`Cux.AiQuerySoOverViewV`
2. 筛选条件：`OrderNum = 293`
3. 查询字段：`OrderNum`、`CurrencyCode`、`DocLineAmount`、`LineAmount`、`DocOrderAmt`、`OrderAmt`
4. 其他关键字内容：空

## 15.4 查询销售订单293的需求日期和发货数量

```sql
SELECT ISNULL([OrderNum], 0) AS [OrderNum], [NeedByDate] AS [NeedByDate], ISNULL([ShipQty], 0) AS [ShipQty] FROM [Cux].[AiQuerySoOverViewV] WITH(NOLOCK) WHERE [OrderNum] = 293
```

1. 视图：`Cux.AiQuerySoOverViewV`
2. 筛选条件：`OrderNum = 293`
3. 查询字段：`OrderNum`、`NeedByDate`、`ShipQty`
4. 其他关键字内容：空

## 15.5 查询销售订单293的退货数量、红票数量和开票数量

```sql
SELECT ISNULL([OrderNum], 0) AS [OrderNum], ISNULL([ReturnQty], 0) AS [ReturnQty], ISNULL([RedQty], 0) AS [RedQty], ISNULL([InvoiceQty], 0) AS [InvoiceQty] FROM [Cux].[AiQuerySoOverViewV] WITH(NOLOCK) WHERE [OrderNum] = 293
```

1. 视图：`Cux.AiQuerySoOverViewV`
2. 筛选条件：`OrderNum = 293`
3. 查询字段：`OrderNum`、`ReturnQty`、`RedQty`、`InvoiceQty`
4. 其他关键字内容：空

## 15.6 查询销售订单293的客户采购订单号和货币代码

```sql
SELECT ISNULL([OrderNum], 0) AS [OrderNum], ISNULL([PONum], 0) AS [PONum], LTRIM(RTRIM([CurrencyCode])) AS [CurrencyCode] FROM [Cux].[AiQuerySoOverViewV] WITH(NOLOCK) WHERE [OrderNum] = 293
```

1. 视图：`Cux.AiQuerySoOverViewV`
2. 筛选条件：`OrderNum = 293`
3. 查询字段：`OrderNum`、`PONum`、`CurrencyCode`
4. 其他关键字内容：空

## 15.7 查询销售订单782的订单日期和客户名称

```sql
SELECT ISNULL([OrderNum], 0) AS [OrderNum], [OrderDate] AS [OrderDate], LTRIM(RTRIM([Customer_Name])) AS [Customer_Name] FROM [Cux].[AiQuerySoOverViewV] WITH(NOLOCK) WHERE [OrderNum] = 782
```

1. 视图：`Cux.AiQuerySoOverViewV`
2. 筛选条件：`OrderNum = 782`
3. 查询字段：`OrderNum`、`OrderDate`、`Customer_Name`
4. 其他关键字内容：空

## 15.8 查询销售订单782的物料描述、订单数量和行金额

```sql
SELECT ISNULL([OrderNum], 0) AS [OrderNum], LTRIM(RTRIM([LineDesc])) AS [LineDesc], ISNULL([OrderQty], 0) AS [OrderQty], LTRIM(RTRIM([CurrencyCode])) AS [CurrencyCode], ISNULL([DocLineAmount], 0) AS [DocLineAmount], ISNULL([LineAmount], 0) AS [LineAmount] FROM [Cux].[AiQuerySoOverViewV] WITH(NOLOCK) WHERE [OrderNum] = 782
```

1. 视图：`Cux.AiQuerySoOverViewV`
2. 筛选条件：`OrderNum = 782`
3. 查询字段：`OrderNum`、`LineDesc`、`OrderQty`、`CurrencyCode`、`DocLineAmount`、`LineAmount`
4. 其他关键字内容：空

## 15.9 查询销售订单782的发货数量和开票数量

```sql
SELECT ISNULL([OrderNum], 0) AS [OrderNum], ISNULL([ShipQty], 0) AS [ShipQty], ISNULL([InvoiceQty], 0) AS [InvoiceQty] FROM [Cux].[AiQuerySoOverViewV] WITH(NOLOCK) WHERE [OrderNum] = 782
```

1. 视图：`Cux.AiQuerySoOverViewV`
2. 筛选条件：`OrderNum = 782`
3. 查询字段：`OrderNum`、`ShipQty`、`InvoiceQty`
4. 其他关键字内容：空

## 15.10 查询销售订单782的客户采购订单号、需求日期和货币代码

```sql
SELECT ISNULL([OrderNum], 0) AS [OrderNum], ISNULL([PONum], 0) AS [PONum], [NeedByDate] AS [NeedByDate], LTRIM(RTRIM([CurrencyCode])) AS [CurrencyCode] FROM [Cux].[AiQuerySoOverViewV] WITH(NOLOCK) WHERE [OrderNum] = 782
```

1. 视图：`Cux.AiQuerySoOverViewV`
2. 筛选条件：`OrderNum = 782`
3. 查询字段：`OrderNum`、`PONum`、`NeedByDate`、`CurrencyCode`
4. 其他关键字内容：空

## 16.1 查询项目26M001-C-W的客户名称

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([CustName])) AS [CustName] FROM [Cux].[AiQueryProjectV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'26M001-C-W'
```

1. 视图：`Cux.AiQueryProjectV`
2. 筛选条件：`ProjectID = '26M001-C-W'`
3. 查询字段：`ProjectID`、`CustName`
4. 其他关键字内容：空

## 16.2 查询项目26M001-C-W的项目机型

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([MachineType])) AS [MachineType] FROM [Cux].[AiQueryProjectV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'26M001-C-W'
```

1. 视图：`Cux.AiQueryProjectV`
2. 筛选条件：`ProjectID = '26M001-C-W'`
3. 查询字段：`ProjectID`、`MachineType`
4. 其他关键字内容：空

## 16.3 查询项目26M001-C-W的项目状态

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([ProjectStatus])) AS [ProjectStatus] FROM [Cux].[AiQueryProjectV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'26M001-C-W'
```

1. 视图：`Cux.AiQueryProjectV`
2. 筛选条件：`ProjectID = '26M001-C-W'`
3. 查询字段：`ProjectID`、`ProjectStatus`
4. 其他关键字内容：空

## 16.4 查询项目26M001-C-W的发货日期和验收日期

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], [Dlvdate] AS [Dlvdate], [Checkdate] AS [Checkdate] FROM [Cux].[AiQueryProjectV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'26M001-C-W'
```

1. 视图：`Cux.AiQueryProjectV`
2. 筛选条件：`ProjectID = '26M001-C-W'`
3. 查询字段：`ProjectID`、`Dlvdate`、`Checkdate`
4. 其他关键字内容：空

## 16.5 查询项目26M001-I-1-W的客户名称和项目机型

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([CustName])) AS [CustName], LTRIM(RTRIM([MachineType])) AS [MachineType] FROM [Cux].[AiQueryProjectV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'26M001-I-1-W'
```

1. 视图：`Cux.AiQueryProjectV`
2. 筛选条件：`ProjectID = '26M001-I-1-W'`
3. 查询字段：`ProjectID`、`CustName`、`MachineType`
4. 其他关键字内容：空

## 16.6 查询项目26M001-I-1-W的项目状态

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([ProjectStatus])) AS [ProjectStatus] FROM [Cux].[AiQueryProjectV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'26M001-I-1-W'
```

1. 视图：`Cux.AiQueryProjectV`
2. 筛选条件：`ProjectID = '26M001-I-1-W'`
3. 查询字段：`ProjectID`、`ProjectStatus`
4. 其他关键字内容：空

## 16.7 查询项目26M001-I-1-W的发货日期

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], [Dlvdate] AS [Dlvdate] FROM [Cux].[AiQueryProjectV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'26M001-I-1-W'
```

1. 视图：`Cux.AiQueryProjectV`
2. 筛选条件：`ProjectID = '26M001-I-1-W'`
3. 查询字段：`ProjectID`、`Dlvdate`
4. 其他关键字内容：空

## 16.8 查询26M001-C-W当前状态和客户

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([ProjectStatus])) AS [ProjectStatus], LTRIM(RTRIM([CustName])) AS [CustName] FROM [Cux].[AiQueryProjectV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'26M001-C-W'
```

1. 视图：`Cux.AiQueryProjectV`
2. 筛选条件：`ProjectID = '26M001-C-W'`
3. 查询字段：`ProjectID`、`ProjectStatus`、`CustName`
4. 其他关键字内容：空

## 16.9 查询26M001-I-1-W是否已验收

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], [Checkdate] AS [Checkdate], CASE WHEN [Checkdate] IS NULL THEN N'否' ELSE N'是' END AS [IsAccepted] FROM [Cux].[AiQueryProjectV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'26M001-I-1-W'
```

1. 视图：`Cux.AiQueryProjectV`
2. 筛选条件：`ProjectID = '26M001-I-1-W'`
3. 查询字段：`ProjectID`、`Checkdate`
4. 其他关键字内容：`CASE WHEN Checkdate IS NULL THEN '否' ELSE '是' END`

## 16.10 查询项目26M001-C-W和26M001-I-1-W的发货日期

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], [Dlvdate] AS [Dlvdate] FROM [Cux].[AiQueryProjectV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) IN (N'26M001-C-W', N'26M001-I-1-W')
```

1. 视图：`Cux.AiQueryProjectV`
2. 筛选条件：`ProjectID IN ('26M001-C-W', '26M001-I-1-W')`
3. 查询字段：`ProjectID`、`Dlvdate`
4. 其他关键字内容：空

## 17.1 查询工单24M007-I-14的完工数量

```sql
SELECT LTRIM(RTRIM([JobNum])) AS [JobNum], LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([JobOprCompQty], 0) AS [JobOprCompQty] FROM [Cux].[AiQueryJobTrackingV] WITH(NOLOCK) WHERE LTRIM(RTRIM([JobNum])) = N'24M007-I-14'
```

1. 视图：`Cux.AiQueryJobTrackingV`
2. 筛选条件：`JobNum = '24M007-I-14'`
3. 查询字段：`JobNum`、`PartNum`、`PartDescription`、`JobOprCompQty`
4. 其他关键字内容：空

## 17.2 查询工单WO019594的完工数量

```sql
SELECT LTRIM(RTRIM([JobNum])) AS [JobNum], LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([JobOprCompQty], 0) AS [JobOprCompQty] FROM [Cux].[AiQueryJobTrackingV] WITH(NOLOCK) WHERE LTRIM(RTRIM([JobNum])) = N'WO019594'
```

1. 视图：`Cux.AiQueryJobTrackingV`
2. 筛选条件：`JobNum = 'WO019594'`
3. 查询字段：`JobNum`、`PartNum`、`PartDescription`、`JobOprCompQty`
4. 其他关键字内容：空

## 17.3 查询24M007-I-14目前完成了多少

```sql
SELECT LTRIM(RTRIM([JobNum])) AS [JobNum], LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([JobOprCompQty], 0) AS [JobOprCompQty] FROM [Cux].[AiQueryJobTrackingV] WITH(NOLOCK) WHERE LTRIM(RTRIM([JobNum])) = N'24M007-I-14'
```

1. 视图：`Cux.AiQueryJobTrackingV`
2. 筛选条件：`JobNum = '24M007-I-14'`
3. 查询字段：`JobNum`、`PartNum`、`PartDescription`、`JobOprCompQty`
4. 其他关键字内容：空

## 17.4 查询WO019594目前完成了多少

```sql
SELECT LTRIM(RTRIM([JobNum])) AS [JobNum], LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([JobOprCompQty], 0) AS [JobOprCompQty] FROM [Cux].[AiQueryJobTrackingV] WITH(NOLOCK) WHERE LTRIM(RTRIM([JobNum])) = N'WO019594'
```

1. 视图：`Cux.AiQueryJobTrackingV`
2. 筛选条件：`JobNum = 'WO019594'`
3. 查询字段：`JobNum`、`PartNum`、`PartDescription`、`JobOprCompQty`
4. 其他关键字内容：空

## 17.5 查询24M007-I-14的工单数量和完工数量

```sql
SELECT LTRIM(RTRIM([JobNum])) AS [JobNum], LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([JobQty], 0) AS [JobQty], ISNULL([JobOprCompQty], 0) AS [JobOprCompQty] FROM [Cux].[AiQueryJobTrackingV] WITH(NOLOCK) WHERE LTRIM(RTRIM([JobNum])) = N'24M007-I-14'
```

1. 视图：`Cux.AiQueryJobTrackingV`
2. 筛选条件：`JobNum = '24M007-I-14'`
3. 查询字段：`JobNum`、`PartNum`、`PartDescription`、`JobQty`、`JobOprCompQty`
4. 其他关键字内容：空

## 17.6 查询WO019594的工单数量和完工数量

```sql
SELECT LTRIM(RTRIM([JobNum])) AS [JobNum], LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([JobQty], 0) AS [JobQty], ISNULL([JobOprCompQty], 0) AS [JobOprCompQty] FROM [Cux].[AiQueryJobTrackingV] WITH(NOLOCK) WHERE LTRIM(RTRIM([JobNum])) = N'WO019594'
```

1. 视图：`Cux.AiQueryJobTrackingV`
2. 筛选条件：`JobNum = 'WO019594'`
3. 查询字段：`JobNum`、`PartNum`、`PartDescription`、`JobQty`、`JobOprCompQty`
4. 其他关键字内容：空

## 17.7 查询24M007-I-14是否已经完工

```sql
SELECT LTRIM(RTRIM([JobNum])) AS [JobNum], ISNULL([JobQty], 0) AS [JobQty], ISNULL([JobOprCompQty], 0) AS [JobOprCompQty], CASE WHEN ISNULL([JobOprCompQty], 0) >= ISNULL([JobQty], 0) AND ISNULL([JobQty], 0) > 0 THEN N'是' ELSE N'否' END AS [IsCompleted] FROM [Cux].[AiQueryJobTrackingV] WITH(NOLOCK) WHERE LTRIM(RTRIM([JobNum])) = N'24M007-I-14'
```

1. 视图：`Cux.AiQueryJobTrackingV`
2. 筛选条件：`JobNum = '24M007-I-14'`
3. 查询字段：`JobNum`、`JobQty`、`JobOprCompQty`
4. 其他关键字内容：`CASE WHEN ISNULL(JobOprCompQty, 0) >= ISNULL(JobQty, 0) AND ISNULL(JobQty, 0) > 0 THEN '是' ELSE '否' END`

## 17.8 查询WO019594是否已经完工

```sql
SELECT LTRIM(RTRIM([JobNum])) AS [JobNum], ISNULL([JobQty], 0) AS [JobQty], ISNULL([JobOprCompQty], 0) AS [JobOprCompQty], CASE WHEN ISNULL([JobOprCompQty], 0) >= ISNULL([JobQty], 0) AND ISNULL([JobQty], 0) > 0 THEN N'是' ELSE N'否' END AS [IsCompleted] FROM [Cux].[AiQueryJobTrackingV] WITH(NOLOCK) WHERE LTRIM(RTRIM([JobNum])) = N'WO019594'
```

1. 视图：`Cux.AiQueryJobTrackingV`
2. 筛选条件：`JobNum = 'WO019594'`
3. 查询字段：`JobNum`、`JobQty`、`JobOprCompQty`
4. 其他关键字内容：`CASE WHEN ISNULL(JobOprCompQty, 0) >= ISNULL(JobQty, 0) AND ISNULL(JobQty, 0) > 0 THEN '是' ELSE '否' END`

## 17.9 查询工单24M007-I-14对应部件的完工数量

```sql
SELECT LTRIM(RTRIM([JobNum])) AS [JobNum], LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([JobOprCompQty], 0) AS [JobOprCompQty] FROM [Cux].[AiQueryJobTrackingV] WITH(NOLOCK) WHERE LTRIM(RTRIM([JobNum])) = N'24M007-I-14'
```

1. 视图：`Cux.AiQueryJobTrackingV`
2. 筛选条件：`JobNum = '24M007-I-14'`
3. 查询字段：`JobNum`、`PartNum`、`PartDescription`、`JobOprCompQty`
4. 其他关键字内容：空

## 17.10 查询工单WO019594对应部件的完工数量

```sql
SELECT LTRIM(RTRIM([JobNum])) AS [JobNum], LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], ISNULL([JobOprCompQty], 0) AS [JobOprCompQty] FROM [Cux].[AiQueryJobTrackingV] WITH(NOLOCK) WHERE LTRIM(RTRIM([JobNum])) = N'WO019594'
```

1. 视图：`Cux.AiQueryJobTrackingV`
2. 筛选条件：`JobNum = 'WO019594'`
3. 查询字段：`JobNum`、`PartNum`、`PartDescription`、`JobOprCompQty`
4. 其他关键字内容：空

## 18.1 查询图号211.181L-01-01-003-A的库存计量单位和采购计量单位

```sql
SELECT DISTINCT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], LTRIM(RTRIM([IUM])) AS [IUM], LTRIM(RTRIM([PUM])) AS [PUM] FROM [Cux].[AiQueryPartTimeTrackingV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'211.181L-01-01-003-A'
```

1. 视图：`Cux.AiQueryPartTimeTrackingV`
2. 筛选条件：`PartNum = '211.181L-01-01-003-A'`
3. 查询字段：`PartNum`、`PartDescription`、`IUM`、`PUM`
4. 其他关键字内容：`DISTINCT`

## 18.2 查询物料181L-01-01-003-A_扇形盖板_发黑的库存计量单位和采购计量单位

```sql
SELECT DISTINCT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([PartDescription])) AS [PartDescription], LTRIM(RTRIM([IUM])) AS [IUM], LTRIM(RTRIM([PUM])) AS [PUM] FROM [Cux].[AiQueryPartTimeTrackingV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartDescription])) = N'181L-01-01-003-A_扇形盖板_发黑'
```

1. 视图：`Cux.AiQueryPartTimeTrackingV`
2. 筛选条件：`PartDescription = '181L-01-01-003-A_扇形盖板_发黑'`
3. 查询字段：`PartNum`、`PartDescription`、`IUM`、`PUM`
4. 其他关键字内容：`DISTINCT`

## 18.3 查询211.181L-01-01-003-A的时间轴明细

```sql
SELECT [DueDate] AS [DueDate], ISNULL([ReceiptQty], 0) AS [ReceiptQty], ISNULL([RequiredQty], 0) AS [RequiredQty], ISNULL([BalanceQty], 0) AS [BalanceQty], LTRIM(RTRIM([SourceName])) AS [SourceName] FROM [Cux].[AiQueryPartTimeTrackingV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'211.181L-01-01-003-A'
```

1. 视图：`Cux.AiQueryPartTimeTrackingV`
2. 筛选条件：`PartNum = '211.181L-01-01-003-A'`
3. 查询字段：`DueDate`、`ReceiptQty`、`RequiredQty`、`BalanceQty`、`SourceName`
4. 其他关键字内容：空

## 18.4 查询211.181L-01-01-003-A的到货数量和需求数量

```sql
SELECT [DueDate] AS [DueDate], ISNULL([ReceiptQty], 0) AS [ReceiptQty], ISNULL([RequiredQty], 0) AS [RequiredQty] FROM [Cux].[AiQueryPartTimeTrackingV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'211.181L-01-01-003-A'
```

1. 视图：`Cux.AiQueryPartTimeTrackingV`
2. 筛选条件：`PartNum = '211.181L-01-01-003-A'`
3. 查询字段：`DueDate`、`ReceiptQty`、`RequiredQty`
4. 其他关键字内容：空

## 18.5 查询211.181L-01-01-003-A当前余额数量

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], ISNULL([BalanceQty], 0) AS [CurrentBalanceQty] FROM [Cux].[AiQueryPartTimeTrackingV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'211.181L-01-01-003-A' AND LTRIM(RTRIM([SourceName])) = N'现存量'
```

1. 视图：`Cux.AiQueryPartTimeTrackingV`
2. 筛选条件：`PartNum = '211.181L-01-01-003-A' AND SourceName = '现存量'`
3. 查询字段：`PartNum`、`BalanceQty`
4. 其他关键字内容：空

## 18.6 查询扇形盖板_发黑的来源说明

```sql
SELECT [DueDate] AS [DueDate], LTRIM(RTRIM([SourceName])) AS [SourceName] FROM [Cux].[AiQueryPartTimeTrackingV] WITH(NOLOCK) WHERE [PartDescription] LIKE N'%扇形盖板[_]发黑%'
```

1. 视图：`Cux.AiQueryPartTimeTrackingV`
2. 筛选条件：`PartDescription LIKE '%扇形盖板[_]发黑%'`
3. 查询字段：`DueDate`、`SourceName`
4. 其他关键字内容：空

## 18.7 查询3010000978在2024年9月23日的需求数量和余额

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], [DueDate] AS [DueDate], ISNULL([RequiredQty], 0) AS [RequiredQty], ISNULL([BalanceQty], 0) AS [BalanceQty] FROM [Cux].[AiQueryPartTimeTrackingV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'3010000978' AND [DueDate] >= '2024-09-23' AND [DueDate] < '2024-09-24'
```

1. 视图：`Cux.AiQueryPartTimeTrackingV`
2. 筛选条件：`PartNum = '3010000978' AND DueDate >= '2024-09-23' AND DueDate < '2024-09-24'`
3. 查询字段：`PartNum`、`DueDate`、`RequiredQty`、`BalanceQty`
4. 其他关键字内容：空

## 18.8 查询图号211.181L-01-01-003-A的现存量

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], ISNULL([BalanceQty], 0) AS [CurrentBalanceQty] FROM [Cux].[AiQueryPartTimeTrackingV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'211.181L-01-01-003-A' AND LTRIM(RTRIM([SourceName])) = N'现存量'
```

1. 视图：`Cux.AiQueryPartTimeTrackingV`
2. 筛选条件：`PartNum = '211.181L-01-01-003-A' AND SourceName = '现存量'`
3. 查询字段：`PartNum`、`BalanceQty`
4. 其他关键字内容：空

## 18.9 查询物料211.181L-01-01-003-A后续供需变化

```sql
SELECT [DueDate] AS [DueDate], ISNULL([ReceiptQty], 0) AS [ReceiptQty], ISNULL([RequiredQty], 0) AS [RequiredQty], ISNULL([BalanceQty], 0) AS [BalanceQty], LTRIM(RTRIM([SourceName])) AS [SourceName] FROM [Cux].[AiQueryPartTimeTrackingV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'211.181L-01-01-003-A' AND [DueDate] IS NOT NULL
```

1. 视图：`Cux.AiQueryPartTimeTrackingV`
2. 筛选条件：`PartNum = '211.181L-01-01-003-A' AND DueDate IS NOT NULL`
3. 查询字段：`DueDate`、`ReceiptQty`、`RequiredQty`、`BalanceQty`、`SourceName`
4. 其他关键字内容：空

## 18.10 查询211.181L-01-01-003-A的库存单位、采购单位和余额数量

```sql
SELECT LTRIM(RTRIM([PartNum])) AS [PartNum], LTRIM(RTRIM([IUM])) AS [IUM], LTRIM(RTRIM([PUM])) AS [PUM], ISNULL([BalanceQty], 0) AS [CurrentBalanceQty] FROM [Cux].[AiQueryPartTimeTrackingV] WITH(NOLOCK) WHERE LTRIM(RTRIM([PartNum])) = N'211.181L-01-01-003-A' AND LTRIM(RTRIM([SourceName])) = N'现存量'
```

1. 视图：`Cux.AiQueryPartTimeTrackingV`
2. 筛选条件：`PartNum = '211.181L-01-01-003-A' AND SourceName = '现存量'`
3. 查询字段：`PartNum`、`IUM`、`PUM`、`BalanceQty`
4. 其他关键字内容：空

## 19.1 查询项目22149-2的发生成本

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([ProjectDesc])) AS [ProjectDesc], LTRIM(RTRIM([CustDesc])) AS [CustDesc], ISNULL([ProjOccurCst], 0) AS [ProjOccurCst] FROM [Cux].[AiQueryProjRevCstV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'22149-2'
```

1. 视图：`Cux.AiQueryProjRevCstV`
2. 筛选条件：`ProjectID = '22149-2'`
3. 查询字段：`ProjectID`、`ProjectDesc`、`CustDesc`、`ProjOccurCst`
4. 其他关键字内容：空

## 19.2 查询项目22149-2的已确认收入

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([ProjectDesc])) AS [ProjectDesc], LTRIM(RTRIM([CustDesc])) AS [CustDesc], ISNULL([ProjConfirmRev], 0) AS [ProjConfirmRev] FROM [Cux].[AiQueryProjRevCstV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'22149-2'
```

1. 视图：`Cux.AiQueryProjRevCstV`
2. 筛选条件：`ProjectID = '22149-2'`
3. 查询字段：`ProjectID`、`ProjectDesc`、`CustDesc`、`ProjConfirmRev`
4. 其他关键字内容：空

## 19.3 查询项目22149-2的已结转成本和未结转成本

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([ProjectDesc])) AS [ProjectDesc], LTRIM(RTRIM([CustDesc])) AS [CustDesc], ISNULL([ProjJzCst], 0) AS [ProjJzCst], ISNULL([ProjUnJzCst], 0) AS [ProjUnJzCst] FROM [Cux].[AiQueryProjRevCstV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'22149-2'
```

1. 视图：`Cux.AiQueryProjRevCstV`
2. 筛选条件：`ProjectID = '22149-2'`
3. 查询字段：`ProjectID`、`ProjectDesc`、`CustDesc`、`ProjJzCst`、`ProjUnJzCst`
4. 其他关键字内容：空

## 19.4 查询项目22213的发生成本和已确认收入

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([ProjectDesc])) AS [ProjectDesc], LTRIM(RTRIM([CustDesc])) AS [CustDesc], ISNULL([ProjOccurCst], 0) AS [ProjOccurCst], ISNULL([ProjConfirmRev], 0) AS [ProjConfirmRev] FROM [Cux].[AiQueryProjRevCstV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'22213'
```

1. 视图：`Cux.AiQueryProjRevCstV`
2. 筛选条件：`ProjectID = '22213'`
3. 查询字段：`ProjectID`、`ProjectDesc`、`CustDesc`、`ProjOccurCst`、`ProjConfirmRev`
4. 其他关键字内容：空

## 19.5 查询项目22213的已结转成本

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([ProjectDesc])) AS [ProjectDesc], LTRIM(RTRIM([CustDesc])) AS [CustDesc], ISNULL([ProjJzCst], 0) AS [ProjJzCst] FROM [Cux].[AiQueryProjRevCstV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'22213'
```

1. 视图：`Cux.AiQueryProjRevCstV`
2. 筛选条件：`ProjectID = '22213'`
3. 查询字段：`ProjectID`、`ProjectDesc`、`CustDesc`、`ProjJzCst`
4. 其他关键字内容：空

## 19.6 查询项目22213的未结转成本

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([ProjectDesc])) AS [ProjectDesc], LTRIM(RTRIM([CustDesc])) AS [CustDesc], ISNULL([ProjUnJzCst], 0) AS [ProjUnJzCst] FROM [Cux].[AiQueryProjRevCstV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'22213'
```

1. 视图：`Cux.AiQueryProjRevCstV`
2. 筛选条件：`ProjectID = '22213'`
3. 查询字段：`ProjectID`、`ProjectDesc`、`CustDesc`、`ProjUnJzCst`
4. 其他关键字内容：空

## 19.7 查询客户宁波金田铜管有限公司的项目成本和确认收入

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([ProjectDesc])) AS [ProjectDesc], ISNULL([ProjOccurCst], 0) AS [ProjOccurCst], ISNULL([ProjConfirmRev], 0) AS [ProjConfirmRev] FROM [Cux].[AiQueryProjRevCstV] WITH(NOLOCK) WHERE LTRIM(RTRIM([CustDesc])) = N'宁波金田铜管有限公司'
```

1. 视图：`Cux.AiQueryProjRevCstV`
2. 筛选条件：`CustDesc = '宁波金田铜管有限公司'`
3. 查询字段：`ProjectID`、`ProjectDesc`、`ProjOccurCst`、`ProjConfirmRev`
4. 其他关键字内容：空

## 19.8 查询客户烟台孚信达双金属股份有限公司的项目收入成本情况

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([ProjectDesc])) AS [ProjectDesc], ISNULL([ProjOccurCst], 0) AS [ProjOccurCst], ISNULL([ProjJzCst], 0) AS [ProjJzCst], ISNULL([ProjConfirmRev], 0) AS [ProjConfirmRev], ISNULL([ProjUnJzCst], 0) AS [ProjUnJzCst] FROM [Cux].[AiQueryProjRevCstV] WITH(NOLOCK) WHERE LTRIM(RTRIM([CustDesc])) = N'烟台孚信达双金属股份有限公司'
```

1. 视图：`Cux.AiQueryProjRevCstV`
2. 筛选条件：`CustDesc = '烟台孚信达双金属股份有限公司'`
3. 查询字段：`ProjectID`、`ProjectDesc`、`ProjOccurCst`、`ProjJzCst`、`ProjConfirmRev`、`ProjUnJzCst`
4. 其他关键字内容：空

## 19.9 查询项目22149-2的收入成本结转情况

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([ProjectDesc])) AS [ProjectDesc], LTRIM(RTRIM([CustDesc])) AS [CustDesc], ISNULL([ProjOccurCst], 0) AS [ProjOccurCst], ISNULL([ProjJzCst], 0) AS [ProjJzCst], ISNULL([ProjConfirmRev], 0) AS [ProjConfirmRev], ISNULL([ProjUnJzCst], 0) AS [ProjUnJzCst] FROM [Cux].[AiQueryProjRevCstV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'22149-2'
```

1. 视图：`Cux.AiQueryProjRevCstV`
2. 筛选条件：`ProjectID = '22149-2'`
3. 查询字段：`ProjectID`、`ProjectDesc`、`CustDesc`、`ProjOccurCst`、`ProjJzCst`、`ProjConfirmRev`、`ProjUnJzCst`
4. 其他关键字内容：空

## 19.10 查询项目22213的收入确认情况

```sql
SELECT LTRIM(RTRIM([ProjectID])) AS [ProjectID], LTRIM(RTRIM([ProjectDesc])) AS [ProjectDesc], LTRIM(RTRIM([CustDesc])) AS [CustDesc], ISNULL([ProjConfirmRev], 0) AS [ProjConfirmRev] FROM [Cux].[AiQueryProjRevCstV] WITH(NOLOCK) WHERE LTRIM(RTRIM([ProjectID])) = N'22213'
```

1. 视图：`Cux.AiQueryProjRevCstV`
2. 筛选条件：`ProjectID = '22213'`
3. 查询字段：`ProjectID`、`ProjectDesc`、`CustDesc`、`ProjConfirmRev`
4. 其他关键字内容：空

## 20.1 查询供应商上海影旗传动机械有限公司的本币余额

```sql
SELECT LTRIM(RTRIM([VendorName])) AS [VendorName], LTRIM(RTRIM([CurrCode])) AS [CurrCode], ISNULL([BeqRemainAmount], 0) AS [BeqRemainAmount] FROM [Cux].[AiQueryPayablesV] WITH(NOLOCK) WHERE LTRIM(RTRIM([VendorName])) = N'上海影旗传动机械有限公司'
```

1. 视图：`Cux.AiQueryPayablesV`
2. 筛选条件：`VendorName = '上海影旗传动机械有限公司'`
3. 查询字段：`VendorName`、`CurrCode`、`BeqRemainAmount`
4. 其他关键字内容：空

## 20.2 查询供应商上海影旗传动机械有限公司的原币余额

```sql
SELECT LTRIM(RTRIM([VendorName])) AS [VendorName], LTRIM(RTRIM([CurrCode])) AS [CurrCode], ISNULL([RemainAmount], 0) AS [RemainAmount] FROM [Cux].[AiQueryPayablesV] WITH(NOLOCK) WHERE LTRIM(RTRIM([VendorName])) = N'上海影旗传动机械有限公司'
```

1. 视图：`Cux.AiQueryPayablesV`
2. 筛选条件：`VendorName = '上海影旗传动机械有限公司'`
3. 查询字段：`VendorName`、`CurrCode`、`RemainAmount`
4. 其他关键字内容：空

## 20.3 查询供应商上海影旗传动机械有限公司的累计金额

```sql
SELECT LTRIM(RTRIM([VendorName])) AS [VendorName], LTRIM(RTRIM([CurrCode])) AS [CurrCode], ISNULL([Amount], 0) AS [Amount], ISNULL([BeqAmount], 0) AS [BeqAmount] FROM [Cux].[AiQueryPayablesV] WITH(NOLOCK) WHERE LTRIM(RTRIM([VendorName])) = N'上海影旗传动机械有限公司'
```

1. 视图：`Cux.AiQueryPayablesV`
2. 筛选条件：`VendorName = '上海影旗传动机械有限公司'`
3. 查询字段：`VendorName`、`CurrCode`、`Amount`、`BeqAmount`
4. 其他关键字内容：空

## 20.4 查询供应商上海洪瀚流体控制设备有限公司的本币余额

```sql
SELECT LTRIM(RTRIM([VendorName])) AS [VendorName], LTRIM(RTRIM([CurrCode])) AS [CurrCode], ISNULL([BeqRemainAmount], 0) AS [BeqRemainAmount] FROM [Cux].[AiQueryPayablesV] WITH(NOLOCK) WHERE LTRIM(RTRIM([VendorName])) = N'上海洪瀚流体控制设备有限公司'
```

1. 视图：`Cux.AiQueryPayablesV`
2. 筛选条件：`VendorName = '上海洪瀚流体控制设备有限公司'`
3. 查询字段：`VendorName`、`CurrCode`、`BeqRemainAmount`
4. 其他关键字内容：空

## 20.5 查询供应商上海洪瀚流体控制设备有限公司的原币余额

```sql
SELECT LTRIM(RTRIM([VendorName])) AS [VendorName], LTRIM(RTRIM([CurrCode])) AS [CurrCode], ISNULL([RemainAmount], 0) AS [RemainAmount] FROM [Cux].[AiQueryPayablesV] WITH(NOLOCK) WHERE LTRIM(RTRIM([VendorName])) = N'上海洪瀚流体控制设备有限公司'
```

1. 视图：`Cux.AiQueryPayablesV`
2. 筛选条件：`VendorName = '上海洪瀚流体控制设备有限公司'`
3. 查询字段：`VendorName`、`CurrCode`、`RemainAmount`
4. 其他关键字内容：空

## 20.6 查询供应商上海洪瀚流体控制设备有限公司的累计金额

```sql
SELECT LTRIM(RTRIM([VendorName])) AS [VendorName], LTRIM(RTRIM([CurrCode])) AS [CurrCode], ISNULL([Amount], 0) AS [Amount], ISNULL([BeqAmount], 0) AS [BeqAmount] FROM [Cux].[AiQueryPayablesV] WITH(NOLOCK) WHERE LTRIM(RTRIM([VendorName])) = N'上海洪瀚流体控制设备有限公司'
```

1. 视图：`Cux.AiQueryPayablesV`
2. 筛选条件：`VendorName = '上海洪瀚流体控制设备有限公司'`
3. 查询字段：`VendorName`、`CurrCode`、`Amount`、`BeqAmount`
4. 其他关键字内容：空

## 20.7 查询上海洪瀚流体控制设备有限公司的本币余额和原币余额

```sql
SELECT LTRIM(RTRIM([VendorName])) AS [VendorName], LTRIM(RTRIM([CurrCode])) AS [CurrCode], ISNULL([RemainAmount], 0) AS [RemainAmount], ISNULL([BeqRemainAmount], 0) AS [BeqRemainAmount] FROM [Cux].[AiQueryPayablesV] WITH(NOLOCK) WHERE LTRIM(RTRIM([VendorName])) = N'上海洪瀚流体控制设备有限公司'
```

1. 视图：`Cux.AiQueryPayablesV`
2. 筛选条件：`VendorName = '上海洪瀚流体控制设备有限公司'`
3. 查询字段：`VendorName`、`CurrCode`、`RemainAmount`、`BeqRemainAmount`
4. 其他关键字内容：空

## 20.8 查询上海影旗传动机械有限公司的应付余额

```sql
SELECT LTRIM(RTRIM([VendorName])) AS [VendorName], LTRIM(RTRIM([CurrCode])) AS [CurrCode], ISNULL([RemainAmount], 0) AS [RemainAmount], ISNULL([BeqRemainAmount], 0) AS [BeqRemainAmount] FROM [Cux].[AiQueryPayablesV] WITH(NOLOCK) WHERE LTRIM(RTRIM([VendorName])) = N'上海影旗传动机械有限公司'
```

1. 视图：`Cux.AiQueryPayablesV`
2. 筛选条件：`VendorName = '上海影旗传动机械有限公司'`
3. 查询字段：`VendorName`、`CurrCode`、`RemainAmount`、`BeqRemainAmount`
4. 其他关键字内容：空

## 20.9 查询供应商上海洪瀚流体控制设备有限公司的剩余应付金额

```sql
SELECT LTRIM(RTRIM([VendorName])) AS [VendorName], LTRIM(RTRIM([CurrCode])) AS [CurrCode], ISNULL([RemainAmount], 0) AS [RemainAmount], ISNULL([BeqRemainAmount], 0) AS [BeqRemainAmount] FROM [Cux].[AiQueryPayablesV] WITH(NOLOCK) WHERE LTRIM(RTRIM([VendorName])) = N'上海洪瀚流体控制设备有限公司'
```

1. 视图：`Cux.AiQueryPayablesV`
2. 筛选条件：`VendorName = '上海洪瀚流体控制设备有限公司'`
3. 查询字段：`VendorName`、`CurrCode`、`RemainAmount`、`BeqRemainAmount`
4. 其他关键字内容：空

## 20.10 查询上海影旗传动机械有限公司的累计金额和余额

```sql
SELECT LTRIM(RTRIM([VendorName])) AS [VendorName], LTRIM(RTRIM([CurrCode])) AS [CurrCode], ISNULL([Amount], 0) AS [Amount], ISNULL([BeqAmount], 0) AS [BeqAmount], ISNULL([RemainAmount], 0) AS [RemainAmount], ISNULL([BeqRemainAmount], 0) AS [BeqRemainAmount] FROM [Cux].[AiQueryPayablesV] WITH(NOLOCK) WHERE LTRIM(RTRIM([VendorName])) = N'上海影旗传动机械有限公司'
```

1. 视图：`Cux.AiQueryPayablesV`
2. 筛选条件：`VendorName = '上海影旗传动机械有限公司'`
3. 查询字段：`VendorName`、`CurrCode`、`Amount`、`BeqAmount`、`RemainAmount`、`BeqRemainAmount`
4. 其他关键字内容：空

## 21.1 查询客户江西江铜龙昌精密铜管有限公司的本币余额

```sql
SELECT LTRIM(RTRIM([CustName])) AS [CustName], LTRIM(RTRIM([CueeCode])) AS [CueeCode], ISNULL([BeqRemainAmount], 0) AS [BeqRemainAmount] FROM [Cux].[AiQueryReceivablesV] WITH(NOLOCK) WHERE LTRIM(RTRIM([CustName])) = N'江西江铜龙昌精密铜管有限公司'
```

1. 视图：`Cux.AiQueryReceivablesV`
2. 筛选条件：`CustName = '江西江铜龙昌精密铜管有限公司'`
3. 查询字段：`CustName`、`CueeCode`、`BeqRemainAmount`
4. 其他关键字内容：空

## 21.2 查询客户江西江铜龙昌精密铜管有限公司的原币余额

```sql
SELECT LTRIM(RTRIM([CustName])) AS [CustName], LTRIM(RTRIM([CueeCode])) AS [CueeCode], ISNULL([RemainAmount], 0) AS [RemainAmount] FROM [Cux].[AiQueryReceivablesV] WITH(NOLOCK) WHERE LTRIM(RTRIM([CustName])) = N'江西江铜龙昌精密铜管有限公司'
```

1. 视图：`Cux.AiQueryReceivablesV`
2. 筛选条件：`CustName = '江西江铜龙昌精密铜管有限公司'`
3. 查询字段：`CustName`、`CueeCode`、`RemainAmount`
4. 其他关键字内容：空

## 21.3 查询客户江西江铜龙昌精密铜管有限公司的累计金额

```sql
SELECT LTRIM(RTRIM([CustName])) AS [CustName], LTRIM(RTRIM([CueeCode])) AS [CueeCode], ISNULL([Amount], 0) AS [Amount], ISNULL([BeqAmount], 0) AS [BeqAmount] FROM [Cux].[AiQueryReceivablesV] WITH(NOLOCK) WHERE LTRIM(RTRIM([CustName])) = N'江西江铜龙昌精密铜管有限公司'
```

1. 视图：`Cux.AiQueryReceivablesV`
2. 筛选条件：`CustName = '江西江铜龙昌精密铜管有限公司'`
3. 查询字段：`CustName`、`CueeCode`、`Amount`、`BeqAmount`
4. 其他关键字内容：空

## 21.4 查询客户金龙精密铜管集团股份有限公司的本币余额

```sql
SELECT LTRIM(RTRIM([CustName])) AS [CustName], LTRIM(RTRIM([CueeCode])) AS [CueeCode], ISNULL([BeqRemainAmount], 0) AS [BeqRemainAmount] FROM [Cux].[AiQueryReceivablesV] WITH(NOLOCK) WHERE LTRIM(RTRIM([CustName])) = N'金龙精密铜管集团股份有限公司'
```

1. 视图：`Cux.AiQueryReceivablesV`
2. 筛选条件：`CustName = '金龙精密铜管集团股份有限公司'`
3. 查询字段：`CustName`、`CueeCode`、`BeqRemainAmount`
4. 其他关键字内容：空

## 21.5 查询客户金龙精密铜管集团股份有限公司的原币余额

```sql
SELECT LTRIM(RTRIM([CustName])) AS [CustName], LTRIM(RTRIM([CueeCode])) AS [CueeCode], ISNULL([RemainAmount], 0) AS [RemainAmount] FROM [Cux].[AiQueryReceivablesV] WITH(NOLOCK) WHERE LTRIM(RTRIM([CustName])) = N'金龙精密铜管集团股份有限公司'
```

1. 视图：`Cux.AiQueryReceivablesV`
2. 筛选条件：`CustName = '金龙精密铜管集团股份有限公司'`
3. 查询字段：`CustName`、`CueeCode`、`RemainAmount`
4. 其他关键字内容：空

## 21.6 查询客户金龙精密铜管集团股份有限公司的累计金额

```sql
SELECT LTRIM(RTRIM([CustName])) AS [CustName], LTRIM(RTRIM([CueeCode])) AS [CueeCode], ISNULL([Amount], 0) AS [Amount], ISNULL([BeqAmount], 0) AS [BeqAmount] FROM [Cux].[AiQueryReceivablesV] WITH(NOLOCK) WHERE LTRIM(RTRIM([CustName])) = N'金龙精密铜管集团股份有限公司'
```

1. 视图：`Cux.AiQueryReceivablesV`
2. 筛选条件：`CustName = '金龙精密铜管集团股份有限公司'`
3. 查询字段：`CustName`、`CueeCode`、`Amount`、`BeqAmount`
4. 其他关键字内容：空

## 21.7 查询江西江铜龙昌精密铜管有限公司的应收余额

```sql
SELECT LTRIM(RTRIM([CustName])) AS [CustName], LTRIM(RTRIM([CueeCode])) AS [CueeCode], ISNULL([RemainAmount], 0) AS [RemainAmount], ISNULL([BeqRemainAmount], 0) AS [BeqRemainAmount] FROM [Cux].[AiQueryReceivablesV] WITH(NOLOCK) WHERE LTRIM(RTRIM([CustName])) = N'江西江铜龙昌精密铜管有限公司'
```

1. 视图：`Cux.AiQueryReceivablesV`
2. 筛选条件：`CustName = '江西江铜龙昌精密铜管有限公司'`
3. 查询字段：`CustName`、`CueeCode`、`RemainAmount`、`BeqRemainAmount`
4. 其他关键字内容：空

## 21.8 查询金龙精密铜管集团股份有限公司的应收余额

```sql
SELECT LTRIM(RTRIM([CustName])) AS [CustName], LTRIM(RTRIM([CueeCode])) AS [CueeCode], ISNULL([RemainAmount], 0) AS [RemainAmount], ISNULL([BeqRemainAmount], 0) AS [BeqRemainAmount] FROM [Cux].[AiQueryReceivablesV] WITH(NOLOCK) WHERE LTRIM(RTRIM([CustName])) = N'金龙精密铜管集团股份有限公司'
```

1. 视图：`Cux.AiQueryReceivablesV`
2. 筛选条件：`CustName = '金龙精密铜管集团股份有限公司'`
3. 查询字段：`CustName`、`CueeCode`、`RemainAmount`、`BeqRemainAmount`
4. 其他关键字内容：空

## 21.9 查询江西江铜龙昌精密铜管有限公司的本币余额和原币余额

```sql
SELECT LTRIM(RTRIM([CustName])) AS [CustName], LTRIM(RTRIM([CueeCode])) AS [CueeCode], ISNULL([RemainAmount], 0) AS [RemainAmount], ISNULL([BeqRemainAmount], 0) AS [BeqRemainAmount] FROM [Cux].[AiQueryReceivablesV] WITH(NOLOCK) WHERE LTRIM(RTRIM([CustName])) = N'江西江铜龙昌精密铜管有限公司'
```

1. 视图：`Cux.AiQueryReceivablesV`
2. 筛选条件：`CustName = '江西江铜龙昌精密铜管有限公司'`
3. 查询字段：`CustName`、`CueeCode`、`RemainAmount`、`BeqRemainAmount`
4. 其他关键字内容：空

## 21.10 查询金龙精密铜管集团股份有限公司的累计金额和余额

```sql
SELECT LTRIM(RTRIM([CustName])) AS [CustName], LTRIM(RTRIM([CueeCode])) AS [CueeCode], ISNULL([Amount], 0) AS [Amount], ISNULL([BeqAmount], 0) AS [BeqAmount], ISNULL([RemainAmount], 0) AS [RemainAmount], ISNULL([BeqRemainAmount], 0) AS [BeqRemainAmount] FROM [Cux].[AiQueryReceivablesV] WITH(NOLOCK) WHERE LTRIM(RTRIM([CustName])) = N'金龙精密铜管集团股份有限公司'
```

1. 视图：`Cux.AiQueryReceivablesV`
2. 筛选条件：`CustName = '金龙精密铜管集团股份有限公司'`
3. 查询字段：`CustName`、`CueeCode`、`Amount`、`BeqAmount`、`RemainAmount`、`BeqRemainAmount`
4. 其他关键字内容：空
