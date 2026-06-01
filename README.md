# 🏭 供应商付款查询系统 — 博西家电定制版

> **AI 驱动的财务智能助手** — 基于博西家电（BSH Hausgeräte）真实采购数据
> 支持自然语言查询供应商付款信息，部署于腾讯云，接入飞书机器人

---

## 📋 项目简介

本项目是**博西家电（BSH）财务智能化**的核心工具，实现了供应商付款场景的端到端智能查询：

- **真实数据** — 27条博西家电真实供应商付款记录（加西贝拉、宝钢、巴斯夫、SAP等），总计 **¥2.79亿**
- **自然语言查询** — 基于 DeepSeek 大模型，中文提问自动转 SQL
- **飞书集成** — 支持通过飞书机器人直接查询付款信息
- **总裁展示页** — 精美大屏展示页面，适合高管演示

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 🤖 **AI 自然语言查询** | 输入中文即可查询："加西贝拉付了多少钱？" |
| 🎯 **博西家电真实数据** | 27条供应商付款记录，涵盖IT、采购、物流、市场等6大部门 |
| 📊 **统计概览** | 总笔数、总金额、各付款状态一目了然 |
| 🔍 **多维度筛选** | 按供应商、部门、付款状态、金额范围精准查询 |
| 💻 **Web UI 聊天界面** | 响应式设计，手机/电脑均可流畅使用 |
| 🌐 **RESTful API** | 方便集成到飞书、企业微信等系统 |
| 🚀 **DeepSeek AI 引擎** | 智能 NL2SQL，规则降级保证可靠性 |

## 🏗️ 技术架构

```
飞书机器人 ─┐
微信/WeChat ─┼──→ Web UI ──→ FastAPI ──→ QueryEngine ──→ DeepSeek API
             │                   │                      └→ 规则降级
             │                   ↓
             └── Hermes Gateway  SQLite → 27条BSH真实付款记录
```

- **后端**: Python 3.12+, FastAPI, SQLAlchemy, SQLite
- **AI 引擎**: DeepSeek Chat API（NL2SQL 智能查询）
- **前端**: 纯 HTML + CSS + JavaScript（无框架依赖，移动端适配）
- **消息平台**: 飞书机器人 / 微信 / Web 端三端覆盖
- **部署**: 腾讯云新加坡节点 + Uvicorn ASGI

## 🚀 线上地址

| 入口 | 地址 |
|------|------|
| 🌐 Web 首页 | http://43.156.67.190:18000 |
| 📊 总裁展示页 | http://43.156.67.190:18000/presentation.html |
| 🔌 API 文档 | http://43.156.67.190:18000/docs |

## 🎯 博西家电数据概览

| 指标 | 数值 |
|------|------|
| 📋 供应商总数 | 27家 |
| 💰 总付款金额 | **¥279,350,000** (约2.79亿) |
| ✅ 已付款 | 13笔 |
| ⏳ 待处理 | 9笔 |
| ⚠️ 已逾期 | 5笔 |
| 🏢 覆盖部门 | 6个（采购部、IT部、生产部、市场部、物流部、研发部） |

### 主要供应商

| 供应商 | 金额 | 费用类型 |
|--------|------|---------|
| 🔩 **加西贝拉** | ¥2,560万 | 压缩机框架采购 |
| 🏗️ **宝钢** | ¥5,230万 | 彩涂板年度合同 |
| 🧪 **巴斯夫** | ¥1,280万 | 保温泡沫材料 |
| 🛒 **京东** | ¥350万 | 渠道返利 |
| 💻 **SAP** | ¥680万 | ERP年度许可 |
| 🚢 **德迅** | ¥960万 | 欧洲出口海运 |
| ⚡ **英飞凌** | ¥1,250万 | 智能家电芯片 |
| 🔩 **威灵电机** | ¥1,520万 | BLDC电机采购 |

## 🧪 使用示例

在 Web UI 或飞书中直接提问：

| 问题类型 | 示例 |
|---------|------|
| 📋 **查供应商** | "加西贝拉的付款记录有哪些？" |
| 💸 **查状态** | "所有已逾期的付款" |
| 📊 **查统计** | "付款总额是多少？" |
| 🔍 **组合查询** | "采购部的已逾期付款" |
| 🏢 **按部门** | "IT部门的付款情况" |

## 🔌 API 接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/query` | 自然语言查询付款（AI 智能转 SQL） |
| GET  | `/api/v1/payments` | 参数筛选付款记录 |
| GET  | `/api/v1/payments/:id` | 查询单条记录 |
| GET  | `/api/v1/stats` | 统计概览 |
| POST | `/api/v1/feishu-webhook` | 飞书机器人 Webhook 入口 |

## 📁 项目结构

```
supplier-payment-query/
├── backend/
│   ├── main.py              # FastAPI 主入口
│   ├── database.py          # SQLite 数据库引擎
│   ├── models.py            # 数据模型
│   ├── query_engine.py      # AI 自然语言 → SQL 查询引擎
│   └── routers/
│       └── payments.py      # RESTful API + 飞书 Webhook 路由
├── frontend/
│   ├── index.html           # 聊天式 Web UI
│   └── presentation.html    # 总裁级展示页面
├── data/
│   ├── generate_real_data.py # BSH 真实数据生成器
│   ├── payments_real.csv    # 真实数据 CSV
│   └── payments.db          # SQLite 数据库
├── scripts/
│   └── init_db.py           # 数据库初始化脚本
└── .env                     # 环境变量配置
```

## 🛠️ 本地部署

```bash
# 1. 克隆
git clone https://github.com/gaga436/supplier-payment-query.git
cd supplier-payment-query

# 2. 安装依赖
python3 -m venv venv && source venv/bin/activate
pip install fastapi uvicorn sqlalchemy openai python-dotenv

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY

# 4. 初始化数据库
python scripts/init_db.py

# 5. 启动
./venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 18000
```

---

**博西家用电器（BSH Hausgeräte GmbH）** — 欧洲领先的家电制造商，旗下品牌包括博世（Bosch）、西门子（Siemens）、嘉格纳（Gaggenau）等。
