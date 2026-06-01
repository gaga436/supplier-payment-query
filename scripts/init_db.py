"""
数据库初始化脚本
从 CSV 导入样本数据到 SQLite 数据库
"""

import csv
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db, SessionLocal
from backend.models import Payment


def load_csv(csv_path: str):
    """从 CSV 加载数据到数据库"""
    if not os.path.exists(csv_path):
        print(f"❌ 文件不存在: {csv_path}")
        return False

    db = SessionLocal()
    try:
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                # 日期字段处理
                for date_field in ["开票日期", "付款到期日", "实际付款日期"]:
                    val = row.get(date_field, "").strip()
                    if val:
                        try:
                            row[date_field] = datetime.strptime(val, "%Y-%m-%d").date()
                        except ValueError:
                            row[date_field] = None
                    else:
                        row[date_field] = None

                payment = Payment(**row)
                db.add(payment)
                count += 1

            db.commit()
            print(f"✅ 成功导入 {count} 条付款记录")
            return True
    except Exception as e:
        db.rollback()
        print(f"❌ 导入失败: {e}")
        return False
    finally:
        db.close()


def generate_and_load():
    """生成样本数据并导入"""
    from data.generate_data import generate_dataset, main as gen_main
    gen_main()

    csv_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "payments.csv"
    )
    return load_csv(csv_path)


if __name__ == "__main__":
    print("=" * 50)
    print("供应商付款查询系统 — 数据库初始化")
    print("=" * 50)

    init_db()
    print("✅ 数据库表结构已创建")

    success = generate_and_load()
    if success:
        print("\n🎉 初始化完成！可以使用以下命令启动服务：")
        print("   python -m backend.main")
    else:
        print("\n❌ 初始化失败，请检查错误信息")
        sys.exit(1)
