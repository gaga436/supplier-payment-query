# 供应商付款查询系统 💰

> **AI 驱动的财务智能助手** — 支持自然语言查询供应商付款信息  
> 财务AI助手实习项目 · 供应商付款查询场景端到端实现

---

## 📋 项目简介

本项目是**财务AI助手实习项目**的核心交付物之一，实现了"供应商付款查询"场景的端到端设计：

- **知识梳理** — 整理供应商付款业务的数据库 Schema 和查询逻辑
- **对话逻辑构建** — 基于 DeepSeek 大语言模型，将自然语言自动转换为 SQL 查询
- **用户验收测试** — 提供完整的 Web UI，支持用户直接用中文提问
- **成效追踪** — 内置统计接口，可监控自助查询率等核心指标

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 🤖 **AI 自然语言查询** | 输入中文即可查询，AI 自动转 SQL |
| 📊 **60+ 条真实样本数据** | 华为、腾讯云、阿里云等供应商付款记录 |
| 🔍 **按状态、供应商、金额、日期筛选** | 已付款、待审批、已逾期一键查询 |
| 📈 **统计概览** | 总笔数、总金额、各状态分布 |
| 💻 **Web UI 聊天界面** | 简洁美观，支持快捷提问 |
| 🌐 **RESTful API** | 方便集成到其他系统 |
| 🔌 **DeepSeek API** | AI 查询引擎，规则降级保证可用 |

## 🏗️ 技术架构

```
用户 → Web UI → FastAPI → QueryEngine → DeepSeek API / Rule-based
                ↓
            SQLite → 60条付款数据
```

- **后端**: Python 3.12+, FastAPI, SQLAlchemy, SQLite
- **AI**: DeepSeek Chat API (兼容 OpenAI SDK)
- **前端**: 纯 HTML + CSS + JavaScript (无框架依赖)
- **部署**: Uvicorn ASGI 服务器

## 🚀 快速开始

### 前置条件

- Python 3.11+
- DeepSeek API Key（[免费申请](https://platform.deepseek.com/)）

### 安装运行

```bash
# 1. 克隆仓库
git clone https://github.com/<你的用户名>/supplier-payment-query.git
cd supplier-payment-query

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt
# 或: pip install fastapi uvicorn sqlalchemy openai python-dotenv pandas

# 4. 配置 API 密钥
cp .env.example .env
# 编辑 .env，填入你的 DEEPSEEK_API_KEY

# 5. 初始化数据库（生成60条样本数据）
python scripts/init_db.py

# 6. 启动服务
python -m uvicorn backend.main:app --host 127.0.0.1 --port 15721

# 7. 打开浏览器访问
# http://127.0.0.1:15721
```

### 使用 Docker

```bash
# 构建
docker build -t supplier-payment-query .

# 运行
docker run -p 15721:15721 \
  -e DEEPSEEK_API_KEY=sk-your-key \
  supplier-payment-query
```

## 🧪 使用示例

在 Web UI 的输入框中，可以直接用中文提问：

| 问题类型 | 示例 |
|---------|------|
| 📋 **查供应商** | "华为的付款有哪些？" |
| 💸 **查状态** | "所有已逾期的付款" |
| 📊 **查统计** | "本月付款总金额是多少？" |
| 🔍 **组合查询** | "IT部门申请的金额超过10万的已逾期付款" |
| 📅 **按时间** | "上个月到期的付款" |

AI 会自动理解你的问题，生成对应的 SQL 查询并返回结果。

## 📁 项目结构

```
supplier-payment-query/
├── backend/
│   ├── main.py              # FastAPI 主入口
│   ├── database.py          # SQLite 数据库引擎
│   ├── models.py            # 数据模型（Payment 表）
│   ├── query_engine.py      # AI 自然语言 → SQL 查询引擎
│   └── routers/
│       └── payments.py      # RESTful API 路由
├── frontend/
│   └── index.html           # 聊天式 Web UI
├── data/
│   ├── generate_data.py     # 60条样本数据生成器
│   ├── payments.csv         # 样本数据（CSV）
│   └── seed.sql             # 样本数据（SQL）
├── scripts/
│   └── init_db.py           # 数据库初始化脚本
├── pyproject.toml           # 项目配置
├── .env.example             # 环境变量模板
└── .gitignore
```

## 🔌 API 文档

启动服务后访问 `http://127.0.0.1:15721/docs` 查看 Swagger 文档。

### 核心接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/query` | 自然语言查询付款 |
| GET  | `/api/v1/payments` | 参数筛选付款记录 |
| GET  | `/api/v1/payments/:id` | 查询单条记录 |
| GET  | `/api/v1/stats` | 统计概览 |

## 📈 实习项目成效

本项目可作为财务AI助手实习项目的**交付成果**，覆盖以下实习内容：

1. **战略分析与规划** — 供应商付款场景的需求分析和数据库设计
2. **解决方案设计与测试** — 端到端查询逻辑实现 + Web UI
3. **成效追踪** — 统计接口可监控自助查询率
4. **跨部门沟通** — RESTful API 便于 IT 和业务部门集成

## 📄 License

MIT
