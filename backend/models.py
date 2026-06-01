"""
供应商付款数据模型
"""

from sqlalchemy import Column, Integer, String, Float, Date, Text
from backend.database import Base


class Payment(Base):
    """供应商付款记录"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    付款编号 = Column(String(32), unique=True, nullable=False, index=True, comment="付款唯一编号")
    供应商编号 = Column(String(16), nullable=False, index=True, comment="供应商编码")
    供应商名称 = Column(String(128), nullable=False, comment="供应商全称")
    供应商简称 = Column(String(32), nullable=True, comment="供应商简称")
    供应商类别 = Column(String(32), nullable=True, comment="供应商分类")
    费用类型 = Column(String(32), nullable=False, comment="费用/采购类型")
    付款金额 = Column(Float, nullable=False, comment="付款金额（元）")
    币种 = Column(String(8), default="CNY", comment="币种")
    付款状态 = Column(String(16), nullable=False, index=True, comment="付款状态")
    发票号码 = Column(String(32), nullable=True, comment="关联发票号")
    开票日期 = Column(Date, nullable=True, comment="发票日期")
    付款到期日 = Column(Date, nullable=True, comment="付款截止日")
    实际付款日期 = Column(Date, nullable=True, comment="实际付款日期")
    收款银行 = Column(String(64), nullable=True, comment="收款银行")
    收款账户尾号 = Column(String(16), nullable=True, comment="收款账户尾号")
    申请部门 = Column(String(32), nullable=True, comment="申请部门")
    申请人 = Column(String(16), nullable=True, comment="申请人")
    审批状态 = Column(String(16), nullable=True, comment="审批状态")
    备注 = Column(Text, nullable=True, comment="备注说明")

    def to_dict(self):
        return {
            "id": self.id,
            "付款编号": self.付款编号,
            "供应商编号": self.供应商编号,
            "供应商名称": self.供应商名称,
            "供应商简称": self.供应商简称,
            "供应商类别": self.供应商类别,
            "费用类型": self.费用类型,
            "付款金额": self.付款金额,
            "币种": self.币种,
            "付款状态": self.付款状态,
            "发票号码": self.发票号码,
            "开票日期": str(self.开票日期) if self.开票日期 else None,
            "付款到期日": str(self.付款到期日) if self.付款到期日 else None,
            "实际付款日期": str(self.实际付款日期) if self.实际付款日期 else None,
            "收款银行": self.收款银行,
            "收款账户尾号": self.收款账户尾号,
            "申请部门": self.申请部门,
            "申请人": self.申请人,
            "审批状态": self.审批状态,
            "备注": self.备注,
        }

    def __repr__(self):
        return f"<Payment {self.付款编号} | {self.供应商简称} | ¥{self.付款金额:.2f} | {self.付款状态}>"
