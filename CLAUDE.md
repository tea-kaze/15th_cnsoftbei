# A5 项目：AI数字人智能导游（软件杯赛题）

## 当前进度
- [x] 阶段一：后端 + RAG知识库 + LLM问答
- [x] 阶段二：游客端聊天界面 + 语音交互 + CSS 2D 数字人
- [x] 阶段三：管理后台（数据大屏、交互记录、知识库管理、游客报告、数字人配置）
- [x] 阶段四：个性化路线推荐 + VTube Studio 集成 + 联调

## 技术栈
- 后端：Python FastAPI (端口 8000)
- 前端：Vue 3 + Vite + Element Plus + ECharts 5 (端口 5173)
- 向量检索：sklearn TF-IDF (char ngram 1-3, max_features=2000)
- LLM：DeepSeek API (deepseek-chat, temperature=0.7, max_tokens=500)
- 语音识别：浏览器 Web Speech API
- 语音合成：edge-tts (5 种中文发音人)
- 数字人：CSS 2D 古风头像 + VTube Studio (Live2D/VRM, 可选)
- 数据库：SQLite (analytics.db) + JSON (knowledge_index.json)
- 景区资料：灵山胜境（2 个 docx 文档，37 chunks）
- Python 路径：/d/DevelopTool/Python3.13/python (Python 3.13)

## 启动命令
```bash
# 后端
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# 前端（新终端）
cd frontend
npx vite
```

浏览器访问：
- 游客端 → http://localhost:5173/visitor
- 管理后台 → http://localhost:5173/admin

## API 接口 (23 个)

### 核心问答
- GET  /api/health                    健康检查
- POST /api/chat/ask                  非流式问答 {"question":"...", "history":[...]}
- POST /api/chat/ask/stream           SSE 流式问答（打字机效果）

### 知识库
- POST /api/knowledge/upload          上传文档（txt/pdf/docx）
- GET  /api/knowledge/list            文档列表 + 知识块数量
- DELETE /api/knowledge/{filename}     删除文档

### 语音合成
- GET  /api/tts/voices                获取可用语音列表
- POST /api/tts/synthesize            文本转语音 {"text":"..."}
- GET  /api/tts/audio/{filename}      获取缓存音频

### 管理后台
- GET  /api/admin/dashboard           仪表盘统计（今日/本周/累计）
- GET  /api/admin/interactions        分页交互记录（支持搜索、日期筛选）
- GET  /api/admin/trend               每日交互趋势（默认 30 天）
- GET  /api/admin/popular             热门问题 Top-N
- GET  /api/admin/hourly              时段热力图数据
- GET  /api/admin/report              游客感受度报告

### 路线推荐
- POST /api/recommend                 个性化路线推荐 {"interest":"..."}

### VTube Studio 数字人（可选）
- GET  /api/vts/status                连接状态
- POST /api/vts/connect               手动连接
- POST /api/vts/expression            表情控制（happy/sad/surprised/angry/neutral）
- POST /api/vts/speak                 口型同步
- POST /api/vts/stop                  停止口型同步
- POST /api/vts/hotkey                触发热键动作
- POST /api/vts/move                  移动/旋转/缩放模型
- POST /api/vts/greet                 欢迎流程

## 文件结构
```
A5/
├── README.md                          # 项目首页
├── .gitignore
├── CLAUDE.md                          # 本文件
├── text/                              # 项目文档
│   ├── 项目介绍文档.md
│   ├── 产品总体设计文档.md
│   └── 产品部署和使用手册.md
├── backend/
│   ├── main.py                        # FastAPI 入口，路由注册，CORS
│   ├── .env                           # DeepSeek API Key（不提交）
│   ├── .env.example                   # 环境变量模板
│   ├── requirements.txt               # Python 依赖
│   ├── knowledge_index.json           # TF-IDF 检索索引 (37 chunks)
│   ├── analytics.db                   # SQLite 交互日志（运行时生成）
│   ├── routes/
│   │   ├── chat.py                    # 问答 API + SSE 流式
│   │   ├── knowledge.py               # 知识库 CRUD
│   │   ├── tts.py                     # 语音合成
│   │   ├── vts.py                     # VTube Studio 控制
│   │   ├── admin.py                   # 管理后台统计
│   │   └── recommend.py               # 路线推荐
│   ├── services/
│   │   ├── rag.py                     # TF-IDF 检索 + 文档解析（txt/pdf/docx）
│   │   ├── llm.py                     # DeepSeek 调用（流式 + 非流式）
│   │   ├── tts_service.py             # edge-tts 封装 + 缓存
│   │   ├── vts_service.py             # VTS WebSocket 客户端（单例）
│   │   ├── logging_service.py         # SQLite 日志 + 统计查询
│   │   └── recommend_service.py       # 推荐引擎（3 条预设路线）
│   ├── uploads/                       # 上传文档存储
│   └── tts_cache/                     # TTS 音频缓存（运行时生成）
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js                 # API 代理到 :8000
│   └── src/
│       ├── main.js                    # Vue 3 入口
│       ├── App.vue
│       ├── views/
│       │   ├── VisitorView.vue        # 游客端主视图
│       │   └── AdminView.vue          # 管理后台布局
│       ├── components/
│       │   ├── visitor/
│       │   │   ├── ChatBubble.vue     # 聊天气泡（Markdown）
│       │   │   ├── ChatInput.vue      # 输入栏（文字 + 语音）
│       │   │   ├── DigitalHuman.vue   # CSS 2D 数字人（古风汉服）
│       │   │   ├── RecommendPanel.vue # 路线推荐面板
│       │   │   └── VirtualCamView.vue # OBS Virtual Cam 嵌入
│       │   └── admin/
│       │       ├── DashboardPanel.vue     # 数据大屏（ECharts）
│       │       ├── InteractionsPanel.vue  # 交互记录表格
│       │       ├── KnowledgePanel.vue     # 知识库管理（拖拽上传）
│       │       ├── ReportPanel.vue        # 游客报告
│       │       └── DigitalHumanConfig.vue # 数字人配置
│       ├── api/
│       │   ├── chat.js                # 游客端 API 封装
│       │   └── admin.js               # 管理端 API 封装
│       └── router/
│           └── index.js               # Vue Router 配置
└── 示范景区公开资料包/                 # 灵山胜境原始资料（可选保留）
    ├── 灵山胜境 景点结构化数据集.docx
    └── 灵山胜境：历史、文化、景点特色与个性化游览指南.docx
```

## 注意事项
- Windows CMD 下 curl JSON 引号会出问题，测试用 Python 或 PowerShell
- 中国网络无法访问 HuggingFace，所以用 sklearn TF-IDF 替代 ChromaDB
- 前端 Vite 已配置 `/api` 代理到 `http://localhost:8000`，无需手动设置 CORS
- `.env` 文件不要提交到版本控制（已在 .gitignore 中）
- VTube Studio 为可选组件，不启动也不影响核心功能
