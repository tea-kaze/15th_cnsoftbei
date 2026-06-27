# 🏯 灵山胜境 · AI 智能导游

> **第十五届中国软件杯大赛 A 组赛题 A5 — 景区导览服务 AI 数字人**
>
> 出题企业：锐捷网络（苏州）有限公司

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue-3.5-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org/)
[![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek--chat-536DFE)](https://platform.deepseek.com/)
[![License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-blue)](./LICENSE)

---

## 📖 项目简介

**灵小导** 是一个面向智慧景区的 AI 数字人智能导游系统，以无锡 **灵山胜境** 为示范景区，利用大语言模型（LLM）、检索增强生成（RAG）、语音交互和数字人技术，为游客提供 7×24 小时在线智能导览服务，同时为景区管理者提供数据大屏与游客洞察。

> 🎙️ 游客用语音或文字向 AI 数字人导游提问，系统基于景区知识库实时生成专业、亲切的回答，并驱动数字人以语音和表情进行互动回应——所有服务全天候在线，无需预约。

---

## ✨ 核心功能

### 🎙️ 游客端

| 功能 | 说明 |
|------|------|
| **智能问答** | 基于灵山胜境知识库（37 个知识块），回答景点、历史、文化、路线等问题 |
| **流式打字机** | AI 回答逐字实时显示，SSE 推送，延迟感知极低 |
| **语音输入** | 浏览器 Web Speech API 中文语音识别，说出问题即可 |
| **语音合成** | edge-tts 自然语音播放，5 种中文发音人可选 |
| **路线推荐** | 历史文化 / 自然风光 / 亲子家庭三条路线，附带景点时间线与实用贴士 |
| **多轮对话** | 支持上下文理解与代词消解（"它有多高？"→ 自动关联灵山大佛） |
| **CSS 2D 数字人** | 曼荼罗光环 + 8 瓣金莲 + 浮动粒子，5 种表情 + 14 种关键帧动画 + CSS 变量主题，零外部依赖 |
| **VTube Studio** | 可选接入 Live2D/VRM 3D 模型，WebSocket 实时控制口型与表情 |

### 📊 管理后台

| 功能 | 说明 |
|------|------|
| **数据大屏** | 6 统计卡片 + ECharts 趋势图 + 热门问题 + 时段热力图，30s 自动刷新 |
| **知识库管理** | 拖拽上传文档（txt/pdf/docx），自动解析、分块、建立索引 |
| **交互记录** | 分页查看全部问答，支持关键词搜索、日期筛选、详情弹窗 |
| **游客报告** | 关注点分析 + 情感趋势 + 热门问题 Top 10 + 改进建议 |
| **数字人配置** | VTube Studio 连接 + 状态监控 + 表情/动作测试 + 角色名称/欢迎语/发音人设置 |

---

## 🏗️ 技术架构

```
游客浏览器                    管理员浏览器
    │                              │
    │  Vue 3 SPA                   │  Vue 3 SPA
    │  语音 / 文字输入               │  数据大屏 / 知识库管理
    │                              │
    └──────────┬───────────────────┘
               │  HTTP REST + SSE (流式)
               ▼
┌──────────────────────────────────────────┐
│          Python FastAPI :8000             │
│                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │  /chat   │ │  /admin  │ │   /tts   │ │
│  │ RAG+LLM  │ │  仪表盘   │ │ edge-tts │ │
│  │ SSE 流式  │ │  报告    │ │          │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ │
│       │             │             │      │
│  ┌────┴─────────────┴─────────────┴────┐ │
│  │            服务层                    │ │
│  │  rag.py / llm.py / tts_service.py   │ │
│  │  vts_service.py / logging_service   │ │
│  │  recommend_service.py               │ │
│  └────────────────┬────────────────────┘ │
│                   │                      │
│  ┌────────────────┴────────────────────┐ │
│  │            数据层                    │ │
│  │  knowledge_index.json (37 chunks)   │ │
│  │  analytics.db (SQLite)              │ │
│  │  uploads/ + tts_cache/              │ │
│  └─────────────────────────────────────┘ │
└──────────────────────────────────────────┘
          │                      │
          ▼                      ▼
    DeepSeek API           VTube Studio
    (LLM 问答)            (3D 数字人·可选)
```

### 技术选型

| 层面 | 技术 | 选型理由 |
|------|------|---------|
| 前端 | Vue 3 + Vite + Element Plus | 轻量、中文生态好、响应式 |
| 图表 | ECharts 5 | 国产、文档完善、大屏标配 |
| 语音识别 | Web Speech API | 浏览器内置、零成本、中文识别率高 |
| 语音合成 | edge-tts | 免费、中文质量极高、40+ 发音人 |
| 大语言模型 | DeepSeek-chat | 性价比高、中文能力强、支持流式 |
| 向量检索 | sklearn TF-IDF (char ngram 1-3) | 离线可用、无需 GPU、无网络依赖 |
| 数字人 | CSS 2D（曼荼罗/莲花/粒子/5 表情/14 动画）+ VTube Studio | CSS 零依赖保底，VTS 3D 增强，PC/移动端双布局 |
| 数据库 | SQLite | Python 内置、零配置、竞赛场景足够 |

---

## 🚀 快速开始

### 环境要求

- **Python** 3.10+
- **Node.js** 18+
- **DeepSeek API Key** — 从 [platform.deepseek.com](https://platform.deepseek.com) 获取
- **Chrome / Edge** 浏览器（语音识别支持最佳）

### 三步启动

```bash
# 1️⃣ 启动后端
cd backend
pip install -r requirements.txt
cp .env.example .env          # 编辑 .env 填入 DEEPSEEK_API_KEY
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# 2️⃣ 启动前端（新终端）
cd frontend
npm install
npx vite

# 3️⃣ 浏览器访问
# 游客端   → http://localhost:5173/visitor
# 管理后台 → http://localhost:5173/admin
```

> 📖 详细部署说明、VTube Studio 集成、故障排除请参阅 [产品部署和使用手册](text/产品部署和使用手册.md)

---

## 📁 项目结构

```
A5/
├── backend/                          # Python FastAPI 后端
│   ├── main.py                       # 应用入口，路由注册，CORS
│   ├── .env.example                  # 环境变量模板
│   ├── requirements.txt              # Python 依赖清单
│   ├── knowledge_index.json          # TF-IDF 检索索引 (37 chunks)
│   ├── routes_config.json            # 路线配置数据
│   ├── routes/                       # API 路由层
│   │   ├── chat.py                   #   问答 + SSE 流式
│   │   ├── knowledge.py              #   知识库 CRUD
│   │   ├── tts.py                    #   语音合成
│   │   ├── vts.py                    #   VTube Studio 控制
│   │   ├── admin.py                  #   管理后台统计
│   │   └── recommend.py              #   路线推荐
│   └── services/                     # 服务逻辑层
│       ├── rag.py                    #   TF-IDF 检索 + 文档解析
│       ├── llm.py                    #   DeepSeek 调用 + 流式生成
│       ├── tts_service.py            #   edge-tts 封装
│       ├── vts_service.py            #   VTS WebSocket 客户端
│       ├── logging_service.py        #   SQLite 日志 + 统计
│       ├── recommend_service.py      #   推荐引擎
│       ├── analytics_service.py      #   游客行为数据分析
│       └── middleware.py             #   API 安全中间件
├── frontend/                         # Vue 3 前端
│   └── src/
│       ├── views/                    # 页面（游客端 / 管理后台）
│       ├── components/
│       │   ├── visitor/              #   聊天、数字人、推荐面板等
│       │   └── admin/                #   仪表盘、知识库、报告等
│       ├── api/                      # API 封装
│       └── router/                   # 路由配置
├── text/                             # 📖 项目文档
```

---

## 🔌 API 概览

### 游客端接口

| 方法 | 端点 | 说明 |
|------|------|------|
| `POST` | `/api/chat/ask` | 非流式问答 |
| `POST` | `/api/chat/ask/stream` | SSE 流式问答（打字机效果） |
| `GET` | `/api/tts/voices` | 获取可用语音列表 |
| `POST` | `/api/tts/synthesize` | 文本转语音 |
| `POST` | `/api/recommend` | 个性化路线推荐 |

### 管理端接口

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/api/admin/dashboard` | 仪表盘统计数据 |
| `GET` | `/api/admin/interactions` | 分页交互记录 |
| `GET` | `/api/admin/trend` | 每日交互趋势 |
| `GET` | `/api/admin/popular` | 热门问题 Top-N |
| `GET` | `/api/admin/hourly` | 时段热力图数据 |
| `GET` | `/api/admin/report` | 游客感受度报告 |

### 知识库接口

| 方法 | 端点 | 说明 |
|------|------|------|
| `POST` | `/api/knowledge/upload` | 上传文档（txt/pdf/docx） |
| `GET` | `/api/knowledge/list` | 文档列表 |
| `DELETE` | `/api/knowledge/{filename}` | 删除文档 |

### 数字人接口（可选）

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/api/vts/status` | VTube Studio 连接状态 |
| `POST` | `/api/vts/expression` | 设置数字人表情 |
| `POST` | `/api/vts/speak` | 触发口型同步 |
| `POST` | `/api/vts/greet` | 欢迎流程 |

---

## 🌟 创新亮点

| 维度 | 创新点 | 说明 |
|------|--------|------|
| **交互体验** | 流式打字机 + TTS 全链路 | SSE 逐 token 推送 → 异步渲染 → edge-tts 播放 |
| **数字人** | 双轨方案 | CSS 2D 保底 + VTube Studio 3D 增强 |
| **双布局** | PC/移动端一键切换 | CSS Grid 35%/65% 分栏，localStorage 持久化 |
| **情绪联动** | LLM → 表情映射 | 自动检测回答情绪，驱动数字人表情同步 |
| **语音链路** | 全免费方案 | 浏览器 ASR + edge-tts TTS，零语音 API 成本 |
| **离线可用** | TF-IDF 替代向量数据库 | 解决 HuggingFace 不可达问题，纯离线运行 |
| **完整闭环** | 游客端 + 管理端 | 从服务到分析的全链路覆盖 |

---

## 📚 文档导航

- [项目介绍文档](text/项目介绍文档.md) — 完整的项目背景、功能说明、数据流与创新要点
- [产品总体设计文档](text/产品总体设计文档.md) — 系统架构、模块设计、数据库与算法说明
- [产品部署和使用手册](text/产品部署和使用手册.md) — 环境配置、部署步骤、使用指南与故障排除

---

## 📊 项目规模

| 指标 | 数据 |
|------|------|
| 后端 API 端点 | 23 个 |
| 知识库文档 | 2 份（37 个知识块） |
| 预设游览路线 | 3 条 |
| TTS 发音人 | 5 种 |
| 前端页面 | 2 个（游客端 + 管理后台）+ 10 个组件 |
| 代码行数 | 后端 ~1800 行 / 前端 ~3750 行 |

---

## 🏆 致谢

本项目为 **第十五届中国软件杯大赛** A 组参赛作品，赛题由 **锐捷网络（苏州）有限公司** 出题。

- 大语言模型：[DeepSeek](https://www.deepseek.com/)
- 景区资料：无锡灵山胜境
- 语音合成：[edge-tts](https://github.com/rany2/edge-tts)

---

<p align="center">
  <sub>Built with ❤️ for the 15th China Software Cup</sub>
</p>
