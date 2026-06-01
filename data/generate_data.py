"""
供应商付款样本数据生成器
生成 50+ 条逼真的供应商付款记录用于演示和测试
"""

import csv
import os
import random
from datetime import datetime, timedelta

# ── 供应商数据 ──
SUPPLIERS = [
    {"id": "SUP001", "name": "华为技术有限公司", "short": "华为", "category": "IT设备"},
    {"id": "SUP002", "name": "深圳市腾讯计算机系统有限公司", "short": "腾讯云", "category": "云服务"},
    {"id": "SUP003", "name": "阿里巴巴集团控股有限公司", "short": "阿里云", "category": "云服务"},
    {"id": "SUP004", "name": "金蝶国际软件集团有限公司", "short": "金蝶", "category": "软件服务"},
    {"id": "SUP005", "name": "用友网络科技股份有限公司", "short": "用友", "category": "软件服务"},
    {"id": "SUP006", "name": "中国电信股份有限公司", "short": "中国电信", "category": "通信服务"},
    {"id": "SUP007", "name": "顺丰速运有限公司", "short": "顺丰", "category": "物流服务"},
    {"id": "SUP008", "name": "北京百度网讯科技有限公司", "short": "百度", "category": "广告营销"},
    {"id": "SUP009", "name": "上海携程商务有限公司", "short": "携程商旅", "category": "差旅服务"},
    {"id": "SUP010", "name": "中国建筑第三工程局", "short": "中建三局", "category": "工程建设"},
    {"id": "SUP011", "name": "联想（北京）有限公司", "short": "联想", "category": "IT设备"},
    {"id": "SUP012", "name": "上海海康威视数字技术有限公司", "short": "海康威视", "category": "安防设备"},
    {"id": "SUP013", "name": "中兴通讯股份有限公司", "short": "中兴", "category": "通信设备"},
    {"id": "SUP014", "name": "北京字节跳动科技有限公司", "short": "字节跳动", "category": "广告营销"},
    {"id": "SUP015", "name": "上海电气集团股份有限公司", "short": "上海电气", "category": "工业设备"},
]

# ── 银行信息 ──
BANKS = ["中国银行", "工商银行", "建设银行", "农业银行", "招商银行", "浦发银行"]
TAIL_NUMS = [list(range(1000 + i * 100, 1000 + (i + 1) * 100)) for i in range(6)]

# ── 付款状态 ──
STATUSES = [
    ("已付款", 0.55),
    ("审批中", 0.15),
    ("待审批", 0.12),
    ("已驳回", 0.05),
    ("处理中", 0.08),
    ("已逾期", 0.05),
]

# ── 费用类型 ──
EXPENSE_TYPES = [
    ("硬件采购", 0.20),
    ("软件许可", 0.12),
    ("云服务费", 0.10),
    ("咨询服务费", 0.08),
    ("维护保养费", 0.10),
    ("物流运输费", 0.07),
    ("广告推广费", 0.08),
    ("差旅费用", 0.05),
    ("工程项目款", 0.10),
    ("办公用品", 0.05),
    ("通信费用", 0.03),
    ("培训服务费", 0.02),
]

# ── 发票号码前缀 ──
INV_PREFIXES = ["INV", "FP", "ZZFP"]


def pick_weighted(options):
    items, weights = zip(*options)
    return random.choices(items, weights=weights, k=1)[0]


def random_amount(category: str) -> float:
    ranges = {
        "IT设备": (5000, 500000),
        "云服务": (2000, 200000),
        "软件服务": (10000, 300000),
        "通信服务": (1000, 50000),
        "物流服务": (500, 80000),
        "广告营销": (30000, 800000),
        "差旅服务": (1000, 100000),
        "工程建设": (100000, 2000000),
        "安防设备": (10000, 200000),
        "通信设备": (5000, 300000),
        "工业设备": (50000, 500000),
    }
    lo, hi = ranges.get(category, (1000, 100000))
    amount = round(random.uniform(lo, hi), 2)
    # Make some amounts look more "real"
    if random.random() < 0.3:
        amount = round(amount / 10000, 0) * 10000
    return amount


def random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def generate_dataset(num_records=60):
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2026, 6, 1)

    records = []
    used_invoices = set()

    for i in range(num_records):
        supplier = random.choice(SUPPLIERS)
        status = pick_weighted(STATUSES)
        expense = pick_weighted(EXPENSE_TYPES)
        amount = random_amount(supplier["category"])

        inv = f"{random.choice(INV_PREFIXES)}-2025{random.randint(10000, 99999)}"
        while inv in used_invoices:
            inv = f"{random.choice(INV_PREFIXES)}-2025{random.randint(10000, 99999)}"
        used_invoices.add(inv)

        invoice_date = random_date(start_date, end_date - timedelta(days=30))
        due_date = invoice_date + timedelta(days=random.choice([30, 45, 60, 90]))
        actual_pay_date = None
        if status == "已付款":
            actual_pay_date = random_date(invoice_date + timedelta(days=5), due_date)

        bank = random.choice(BANKS)
        bank_tail = random.choice(TAIL_NUMS[BANKS.index(bank)])
        remark_options = [
            f"Q{i // 3 + 1}季度设备采购",
            f"{i % 12 + 1}月份服务费",
            f"合同#{25000 + i}尾款",
            f"项目#{3000 + i}进度款",
            "年度框架协议结算",
            f"第{i + 1}期付款",
            "紧急采购一次性付款",
            "半年服务费预付",
            "",
            "",
            "",
        ]
        remark = random.choice(remark_options)

        record = {
            "付款编号": f"PAY-{20250000 + i + 1}",
            "供应商编号": supplier["id"],
            "供应商名称": supplier["name"],
            "供应商简称": supplier["short"],
            "供应商类别": supplier["category"],
            "费用类型": expense,
            "付款金额": amount,
            "币种": "CNY",
            "付款状态": status,
            "发票号码": inv,
            "开票日期": invoice_date.strftime("%Y-%m-%d"),
            "付款到期日": due_date.strftime("%Y-%m-%d"),
            "实际付款日期": actual_pay_date.strftime("%Y-%m-%d") if actual_pay_date else "",
            "收款银行": bank,
            "收款账户尾号": str(bank_tail),
            "申请部门": random.choice(["财务部", "IT部", "行政部", "市场部", "工程部", "采购部"]),
            "申请人": random.choice(["张伟", "李娜", "王强", "刘洋", "陈静", "杨帆", "赵磊", "黄丽"]),
            "审批状态": "已通过" if status in ["已付款", "处理中"] else ("待审批" if status in ["待审批", "审批中"] else "已驳回"),
            "备注": remark,
        }
        records.append(record)

    return records


def main():
    os.makedirs("data", exist_ok=True)
    records = generate_dataset(60)

    # CSV 输出
    csv_path = "data/payments.csv"
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        if records:
            writer = csv.DictWriter(f, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)
    print(f"✅ 已生成 {len(records)} 条付款记录 → {csv_path}")

    # SQL 插入语句输出
    sql_path = "data/seed.sql"
    with open(sql_path, "w", encoding="utf-8") as f:
        f.write("-- 供应商付款样本数据\n")
        f.write("-- 生成时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
        for r in records:
            cols = ", ".join(r.keys())
            vals = ", ".join(
                f"'{v}'" if isinstance(v, str) else str(v) for v in r.values()
            )
            f.write(f"INSERT INTO payments ({cols}) VALUES ({vals});\n")
    print(f"✅ SQL 脚本已生成 → {sql_path}")

    return records


if __name__ == "__main__":
    main()
