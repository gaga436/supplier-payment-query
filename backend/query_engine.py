"""
AI 自然语言查询引擎
────────────────
将用户的中文/英文自然语言查询转换为 SQL，执行后返回结构化和自然语言结果。

支持 DeepSeek、OpenAI 兼容 API。
"""

import json
import logging
import os
import re
from typing import Any
try:
    from openai import OpenAI
    _HAVE_OPENAI = True
except ImportError:
    OpenAI = None
    _HAVE_OPENAI = False
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ── 数据库 Schema 描述（喂给 LLM 用） ──
TABLE_SCHEMA = """
表名: payments (供应商付款表)
字段:
  - 付款编号 (TEXT, 主键, 格式: PAY-2025xxxx)
  - 供应商编号 (TEXT, 如 SUP001)
  - 供应商名称 (TEXT, 供应商全称)
  - 供应商简称 (TEXT, 如 华为, 腾讯云)
  - 供应商类别 (TEXT, 如 IT设备, 云服务, 软件服务, 通信服务, 物流服务, 广告营销, 差旅服务, 工程建设)
  - 费用类型 (TEXT, 如 硬件采购, 软件许可, 云服务费, 咨询服务费, 维护保养费, 物流运输费, 广告推广费, 差旅费用, 工程项目款)
  - 付款金额 (REAL, 单位: 元)
  - 币种 (TEXT, 默认 CNY)
  - 付款状态 (TEXT, 可选值: 已付款, 审批中, 待审批, 已驳回, 处理中, 已逾期)
  - 发票号码 (TEXT)
  - 开票日期 (DATE, 格式: YYYY-MM-DD)
  - 付款到期日 (DATE, 格式: YYYY-MM-DD)
  - 实际付款日期 (DATE, 可为空)
  - 收款银行 (TEXT)
  - 收款账户尾号 (TEXT)
  - 申请部门 (TEXT)
  - 申请人 (TEXT)
  - 审批状态 (TEXT, 可选值: 已通过, 待审批, 已驳回)
  - 备注 (TEXT)

通用规则:
  - 日期筛选用 BETWEEN 或 >= <=
  - 金额单位永远是元 (CNY)
  - 模糊查询用 LIKE
  - 聚合函数: COUNT, SUM, AVG, MAX, MIN
  - 结果按 付款到期日 或 开票日期 倒序, 除非另有指定
  - 限制最多返回 50 条
"""

SYSTEM_PROMPT = f"""你是一个专业的财务数据分析助手。你的任务是将用户的自然语言查询转换为 SQLite SQL 查询。

数据库 Schema:
{TABLE_SCHEMA}

要求:
1. 只返回 JSON，不要返回任何其他文字或代码块标记
2. JSON 格式: {{"sql": "SQL查询语句", "explanation": "简短中文说明你要查什么"}}
3. SQL 使用 SQLite 兼容语法
4. 如果用户查询涉及日期范围，合理推断（如"本月"=当月1号到今天，"上个月"=上个月1号到月底）
5. 金额查询请用 ROUND(SUM(付款金额), 2) 避免浮点精度问题
6. 如果用户问的是统计类问题（总数、总额、平均），请用聚合函数
7. 不要生成 INSERT/UPDATE/DELETE，只允许 SELECT
8. 如果查询不明确或无法执行，返回 {{"error": "描述为什么无法查询"}}
"""


class QueryEngine:
    """将自然语言转换为 SQL 并执行查询"""

    def __init__(self, db_session):
        self.db = db_session
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.client = None
        self._init_client()

    def _init_client(self):
        if not self.api_key or self.api_key == "sk-your-key-here":
            logger.warning("DEEPSEEK_API_KEY 未配置，将使用基于规则的简单查询")
            return
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base,
            timeout=15,  # 15s timeout for API calls
            max_retries=1,
        )

    def ask(self, question: str) -> dict:
        """
        入口方法：接收自然语言问题，返回查询结果
        返回: {"query": 原问题, "sql": 执行的SQL, "explanation": 说明, "data": [...], "summary": "自然语言总结"}
        """
        result = {
            "query": question,
            "sql": None,
            "explanation": None,
            "data": [],
            "summary": None,
            "error": None,
        }

        # 1. 自然语言 → SQL
        sql_result = self._nl_to_sql(question)
        if "error" in sql_result:
            result["error"] = sql_result["error"]
            return result

        result["sql"] = sql_result["sql"]
        result["explanation"] = sql_result.get("explanation", "")

        # 2. 执行 SQL
        try:
            rows = self._execute_sql(sql_result["sql"])
        except Exception as e:
            result["error"] = f"SQL 执行失败: {e}"
            return result

        result["data"] = rows

        # 3. 生成自然语言总结
        summary = self._generate_summary(question, rows, sql_result["sql"])
        result["summary"] = summary

        return result

    def _nl_to_sql(self, question: str) -> dict:
        """自然语言转 SQL（优先 AI，降级规则匹配）"""
        if self.client:
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"请将以下查询转换为 SQL：\n\n{question}"},
                    ],
                    temperature=0.1,
                    max_tokens=500,
                    timeout=10,
                )
                content = resp.choices[0].message.content.strip()
                # 清理可能的 markdown 代码块
                content = re.sub(r'^```(?:json)?\s*', '', content)
                content = re.sub(r'\s*```$', '', content)
                parsed = json.loads(content)
                if "sql" in parsed:
                    # 验证 SQL 安全
                    sql = parsed["sql"].strip().upper()
                    if not sql.startswith("SELECT"):
                        return {"error": "仅支持 SELECT 查询"}
                    return parsed
                return {"error": parsed.get("error", "无法解析该查询")}
            except Exception as e:
                logger.warning(f"AI SQL 生成失败: {e}，降级到规则匹配")
                return self._rule_based_sql(question)
        return self._rule_based_sql(question)

    def _rule_based_sql(self, question: str) -> dict:
        """基于规则的简单查询匹配（AI 不可用时降级）"""
        q = question.lower()

        # ── 统计类 ──
        if any(kw in q for kw in ["总共有多少", "一共多少", "有几笔", "多少笔", "总数", "count"]):
            return self._build_sql("SELECT COUNT(*) AS 总笔数 FROM payments", "统计总付款笔数")

        if any(kw in q for kw in ["总金额", "总额", "总共付了", "一共付"]):
            return self._build_sql("SELECT ROUND(SUM(付款金额), 2) AS 总金额 FROM payments", "统计付款总金额")

        # ── 按状态 ──
        for status in ["已付款", "审批中", "待审批", "已驳回", "已逾期", "处理中"]:
            if status in q:
                return self._build_sql(
                    f"SELECT * FROM payments WHERE 付款状态 = '{status}' ORDER BY 付款到期日 DESC",
                    f"查询状态为「{status}」的付款记录",
                )

        # ── 按供应商 ──
        sup_names = ["华为", "腾讯云", "阿里云", "金蝶", "用友", "顺丰", "百度", "海康", "中兴", "联想"]
        for name in sup_names:
            if name in q:
                return self._build_sql(
                    f"SELECT * FROM payments WHERE 供应商简称 LIKE '%{name}%' ORDER BY 付款到期日 DESC",
                    f"查询供应商「{name}」的付款记录",
                )

        # ── 按金额范围 ──
        amount_match = re.search(r'(\d+万?)\s*(?:以[上下]|到|至|-|~)\s*(\d+万?)', q)
        if amount_match:
            lo, hi = amount_match.group(1), amount_match.group(2)
            lo_val = float(lo.replace('万', '')) * 10000 if '万' in lo else float(lo)
            hi_val = float(hi.replace('万', '')) * 10000 if '万' in hi else float(hi)
            return self._build_sql(
                f"SELECT * FROM payments WHERE 付款金额 BETWEEN {lo_val} AND {hi_val} ORDER BY 付款金额 DESC",
                f"查询金额在 {lo_val:.0f}~{hi_val:.0f} 元的付款记录",
            )

        # ── 本月/上月/本季度 ──
        from datetime import datetime
        now = datetime.now()
        if "本月" in q:
            first_day = now.replace(day=1).strftime("%Y-%m-%d")
            today = now.strftime("%Y-%m-%d")
            return self._build_sql(
                f"SELECT * FROM payments WHERE 付款到期日 BETWEEN '{first_day}' AND '{today}' ORDER BY 付款到期日",
                f"查询本月（{first_day} ~ {today}）到期的付款",
            )
        if "上月" in q or "上个月" in q:
            from datetime import timedelta
            first = now.replace(day=1) - timedelta(days=1)
            last_month_start = first.replace(day=1).strftime("%Y-%m-%d")
            last_month_end = first.strftime("%Y-%m-%d")
            return self._build_sql(
                f"SELECT * FROM payments WHERE 付款到期日 BETWEEN '{last_month_start}' AND '{last_month_end}' ORDER BY 付款到期日",
                f"查询上月（{last_month_start} ~ {last_month_end}）到期的付款",
            )
        if "季度" in q or "季" in q:
            qnum = (now.month - 1) // 3 + 1
            return self._build_sql(
                f"SELECT * FROM payments WHERE 备注 LIKE '%Q{qnum}%' OR 备注 LIKE '%第{qnum}期%' ORDER BY 付款到期日",
                f"查询第{qnum}季度的付款记录",
            )

        # ── 默认 ──
        return self._build_sql(
            "SELECT * FROM payments ORDER BY 付款到期日 DESC LIMIT 20",
            "查询最近付款记录（近20条）",
        )

    def _build_sql(self, sql: str, explanation: str) -> dict:
        return {"sql": sql, "explanation": explanation}

    def _execute_sql(self, sql: str) -> list[dict]:
        """执行 SQL 并返回字典列表"""
        from sqlalchemy import text
        result = self.db.execute(text(sql))
        rows = result.fetchall()
        columns = result.keys()
        return [dict(zip(columns, row)) for row in rows]

    def _generate_summary(self, question: str, rows: list[dict], sql: str) -> str:
        """为查询结果生成自然语言总结"""
        if not rows:
            return "未找到符合条件的付款记录。"

        count = len(rows)

        # 尝试提取金额字段
        has_amount = any(k in (rows[0].keys()) for k in ["付款金额", "总金额", "总笔数"])
        total = None
        if has_amount:
            if "总金额" in rows[0]:
                total = rows[0]["总金额"]
            elif "SUM" in sql.upper():
                total = rows[0].get(list(rows[0].keys())[0])

        # 转换为浮点数防止 SQLite 返回字符串导致格式化报错
        def _to_float(v):
            if v is None: return 0.0
            try: return float(v)
            except: return 0.0

        # 聚合查询
        if count == 1 and total is not None:
            return f"查询结果：共 {_to_float(total):,.2f} 元"

        # 普通列表查询
        if "COUNT" in sql.upper() and "总笔数" in rows[0]:
            total_count = rows[0]["总笔数"]
            return f"共查询到 {total_count} 条付款记录。"

        if "SUM" in sql.upper() or any("金额" in k or "总额" in k for k in rows[0]):
            # 找第一个金额相关的字段
            amount_key = next((k for k in rows[0] if "金额" in k or "总额" in k), list(rows[0].keys())[0])
            amount = rows[0].get(amount_key, 0)
            return f"查询结果：总金额为 {_to_float(amount):,.2f} 元"

        if count <= 50:
            statuses = set(r.get("付款状态", "") for r in rows if "付款状态" in r)
            status_info = f"（包含状态: {', '.join(sorted(statuses))}）" if statuses else ""
            return f"共查询到 {count} 条付款记录{status_info}。如需明细请查看下方数据。"

        return f"共查询到 {count} 条记录，建议缩小查询范围。"
