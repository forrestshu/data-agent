"""查询结果字段的中文本地化。"""

from __future__ import annotations

COLUMN_LABELS_ZH = {
    "Company": "公司代码", "CompanyName": "公司名称", "ComName": "公司名称",
    "Plant": "工厂", "PartNum": "物料编码", "PartDescription": "物料描述",
    "ECOMtl_MtlPartNum": "子物料编码", "MtlPartDescription": "子物料描述",
    "JobNum": "工单号", "JobHead_JobNum": "工单号",
    "JobHead_PartNum": "工单物料编码", "JobHead_PartDescription": "工单物料描述",
    "JobQty": "工单数量", "JobHead_ProdQty": "生产数量", "LaborQty": "报工数量",
    "JobOprCompQty": "末道工序完成数量", "CompleteQty": "完工入库数量",
    "ProjectID": "项目号", "ProjectDesc": "项目描述",
    "Project_Description": "项目描述", "ReqDueDate": "要求交期",
    "BinNum": "库位编码", "BinName": "库位名称", "Qty": "现有量",
    "IUM": "库存计量单位", "PUM": "采购计量单位", "DueDate": "需求日期",
    "ReceiptQty": "收货数量", "RequiredQty": "需求数量", "BalanceQty": "结余数量",
    "SourceName": "来源", "VendorID": "供应商代码", "VendorNum": "供应商编号",
    "VendorName": "供应商名称", "Vendor_Name": "供应商名称",
    "NewVendorName": "最新供应商名称", "CurrCode": "币种",
    "Amount": "原币金额", "BeqAmount": "本币金额", "RemainAmount": "原币余额",
    "BeqRemainAmount": "本币余额", "PONum": "采购订单号",
    "NewPONum": "最新采购订单号", "OrderDate": "订单日期",
    "LineDesc": "物料行描述", "OrderQty": "订单数量",
    "ReceivedQty": "收货数量", "InspectionQty": "在检数量",
    "NetReceivedQty": "收货净值", "InvoiceQty": "开票数量",
    "RemainQty": "剩余数量", "ApproveStatus_c": "审批状态",
    "LeadTime": "采购提前期", "NewPrice": "最新采购价", "AvgPrice": "平均采购价",
    "CustID": "客户代码", "CustNum": "客户编号", "CustName": "客户名称",
    "CustDesc": "客户名称", "Customer_Name": "客户名称", "CueeCode": "币种",
    "MachineType": "项目机型", "ProjectStatus": "项目状态",
    "Dlvdate": "发货日期", "Checkdate": "验收日期",
    "ProjOccurCst": "项目发生成本", "ProjJzCst": "项目结转成本",
    "ProjConfirmRev": "项目确认收入", "ProjUnJzCst": "项目未结转成本",
    "OrderNum": "销售订单号", "CurrencyCode": "币种",
    "NeedByDate": "需求日期", "ShipQty": "发货数量",
    "ReturnQty": "退货数量", "RedQty": "红票数量",
    "DocLineAmount": "原币行金额", "LineAmount": "本币行金额",
    "DocOrderAmt": "原币订单金额", "OrderAmt": "本币订单金额",
    "TaxRegionCode": "税区代码",
}


def column_label(column: str) -> str:
    """返回字段中文名；尚未配置时保留原字段，避免伪造业务含义。"""

    return COLUMN_LABELS_ZH.get(column, column)
