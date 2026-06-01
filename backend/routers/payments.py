"""
供应商付款查询 API 路由
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.models import Payment
from backend.query_engine import QueryEngine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["付款查询"])


# ── 请求/响应模型 ──

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500, description="自然语言查询问题")
    top_k: Optional[int] = Field(50, ge=1, le=200, description="最多返回条数")


class PaymentResponse(BaseModel):
    付款编号: str
    供应商名称: str
    供应商简称: Optional[str]
    供应商类别: Optional[str]
    费用类型: str
    付款金额: float
    币种: str
    付款状态: str
    付款到期日: Optional[str]
    实际付款日期: Optional[str]
    申请部门: Optional[str]
    申请人: Optional[str]
    审批状态: Optional[str]


class QueryResponse(BaseModel):
    query: str
    sql: Optional[str] = None
    explanation: Optional[str] = None
    summary: Optional[str] = None
    data: list[dict] = []
    error: Optional[str] = None


# ── API 端点 ──

@router.post("/query", response_model=QueryResponse)
async def natural_query(req: QueryRequest, db: Session = Depends(get_db)):
    """
    自然语言查询供应商付款
    ---
    示例问题:
    - "华为的付款有哪些？"
    - "本月到期的付款有多少笔？"
    - "已逾期的付款总额是多少？"
    - "金额大于10万的待审批付款"
    - "腾讯云今年已付了多少钱？"
    - "采购部申请的付款记录"
    """
    engine = QueryEngine(db)
    result = engine.ask(req.question)

    if result.get("error"):
        return QueryResponse(
            query=req.question,
            error=result["error"],
            data=[],
        )

    return QueryResponse(
        query=result["query"],
        sql=result["sql"],
        explanation=result["explanation"],
        summary=result["summary"],
        data=result["data"],
    )


@router.get("/payments", response_model=list[PaymentResponse])
async def list_payments(
    status: Optional[str] = None,
    supplier: Optional[str] = None,
    department: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """
    通过参数筛选查询付款记录（非 AI 方式）
    """
    q = db.query(Payment)
    if status:
        q = q.filter(Payment.付款状态 == status)
    if supplier:
        q = q.filter(Payment.供应商简称.like(f"%{supplier}%"))
    if department:
        q = q.filter(Payment.申请部门 == department)
    payments = q.order_by(Payment.付款到期日.desc()).offset(skip).limit(limit).all()
    return [p.to_dict() for p in payments]


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: str, db: Session = Depends(get_db)):
    """通过付款编号查询单条记录"""
    p = db.query(Payment).filter(Payment.付款编号 == payment_id).first()
    if not p:
        raise HTTPException(status_code=404, detail=f"付款记录 {payment_id} 未找到")
    return p.to_dict()


# ── 飞书机器人 Webhook ──

class FeishuWebhookRequest(BaseModel):
    """飞书自定义机器人/事件回调请求"""
    challenge: Optional[str] = None
    encrypt: Optional[str] = None
    token: Optional[str] = None
    type: Optional[str] = None
    event: Optional[dict] = None
    # 直接消息模式
    msg_type: Optional[str] = None
    content: Optional[dict] = None
    # 简化模式
    text: Optional[str] = None
    question: Optional[str] = None


class FeishuCardElement(BaseModel):
    tag: str
    text: Optional[dict] = None
    content: Optional[str] = None


@router.post("/feishu-webhook")
async def feishu_webhook(req: FeishuWebhookRequest, db: Session = Depends(get_db)):
    """
    飞书机器人 Webhook 回调接口
    ──────────────────────────────
    支持双模式:
    1. URL Challenge 验证（飞书事件订阅首次校验）
    2. 消息查询（用户发消息给飞书机器人，自动查询付款信息）
    """
    # ── URL Challenge ──
    if req.challenge:
        return {"challenge": req.challenge}

    # ── 提取用户问题 ──
    question = None
    if req.question:
        question = req.question
    elif req.text:
        question = req.text
    elif req.content and isinstance(req.content, dict):
        question = req.content.get("text", "")
    elif req.event and isinstance(req.event, dict):
        msg = req.event.get("message", {})
        content_raw = msg.get("content", "{}")
        import json
        try:
            content_obj = json.loads(content_raw) if isinstance(content_raw, str) else content_raw
            question = content_obj.get("text", "")
        except (json.JSONDecodeError, TypeError):
            pass

    if not question:
        return {"msg_type": "text", "content": {"text": "请发送付款查询问题，例如：本月付款总额是多少？"}}

    # ── 执行查询 ──
    engine = QueryEngine(db)
    result = engine.ask(question)

    # ── 构造返回消息 ──
    if result.get("error"):
        return {
            "msg_type": "text",
            "content": {"text": f"❌ 查询失败：{result['error']}"},
        }

    # 摘要 + 数据详情
    lines = [f"🔍 *{result.get('explanation', '查询结果')}*"]
    if result.get("summary"):
        lines.append(f"\n📊 {result['summary']}")

    data = result.get("data", [])
    if data and len(data) <= 10:
        lines.append("\n━━━━━━━━━━━━━━━")
        for i, row in enumerate(data[:5], 1):
            name = row.get("供应商简称") or row.get("供应商名称", "")
            amount = row.get("付款金额", "")
            status = row.get("付款状态", "")
            dept = row.get("申请部门", "")
            if amount:
                lines.append(f"{i}. {name} | ¥{amount:,.0f} | {status} | {dept}")
            else:
                lines.append(f"{i}. {name} | {status}")
        if len(data) > 5:
            lines.append(f"\n... 还有 {len(data)-5} 条记录")

    return {
        "msg_type": "text",
        "content": {"text": "\n".join(lines)},
    }


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """付款统计概览"""
    from sqlalchemy import func, text

    total_count = db.query(func.count(Payment.id)).scalar()
    total_amount = db.query(func.round(func.sum(Payment.付款金额), 2)).scalar() or 0
    paid_count = db.query(func.count(Payment.id)).filter(Payment.付款状态 == "已付款").scalar()
    pending_count = db.query(func.count(Payment.id)).filter(
        Payment.付款状态.in_(["待审批", "审批中"])
    ).scalar()
    overdue_count = db.query(func.count(Payment.id)).filter(Payment.付款状态 == "已逾期").scalar()

    return {
        "总笔数": total_count,
        "总金额": round(total_amount, 2),
        "已付款笔数": paid_count,
        "待处理笔数": pending_count,
        "已逾期笔数": overdue_count,
    }
