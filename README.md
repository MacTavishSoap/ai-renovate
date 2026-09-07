# AI 家装项目 · ai-renovate

正式项目仓库。AI 驱动的家装效果图生成与全景浏览平台，支持户型图上传、风格化生成、图像超分、全景图浏览与对比。

## 技术选型

| 层 | 选型 | 说明 |
|---|---|---|
| 后端框架 | FastAPI | 异步 Web 框架，自带 OpenAPI 文档 |
| AI 编排 | Pydantic AI | 类型安全的 Agent 编排框架 |
| 数据库 | SQLite + SQLAlchemy | 轻量级，零运维 |
| 前端框架 | Vue 3 + Vite | SPA 单页应用 |
| UI 组件库 | Vant 4 | 移动端优先的组件库 |
| 状态管理 | Pinia | Vue 3 官方推荐 |
| 全景浏览 | Photo Sphere Viewer | 360° 全景图查看 |
| 部署 | Docker 多服务 | backend + frontend + nginx 编排 |
| 反向代理 | Nginx | 静态托管 + API 转发 |
| CI/CD | GitHub Actions | 自动测试 + Docker 构建 |

## 目录结构

```
ai-renovate/
├── docker-compose.yml          # 多服务编排（backend / frontend / nginx）
├── .env.example                # 环境变量模板
├── .gitignore
├── README.md                   # 本文件
│
├── scripts/
│   └── setup_dev.py            # 一键搭建开发环境
│
├── .github/workflows/          # CI/CD
│   ├── ci.yml                  # PR/Push 时跑测试
│   └── cd-build.yml            # Push 到 main 时构建 Docker 镜像
│
├── backend/                    # FastAPI 后端 + Pydantic AI Agent
│   ├── Dockerfile
│   ├── pyproject.toml          # Python 依赖声明
│   ├── requirements.lock       # 🔒 锁定的依赖版本（保证环境一致）
│   ├── .python-version         # 固定 Python 3.12.7
│   ├── app/
│   │   ├── main.py             # FastAPI 入口
│   │   ├── config.py           # 配置加载（环境变量）
│   │   ├── database.py         # SQLite 连接
│   │   ├── models/             # Pydantic / SQLAlchemy 模型
│   │   ├── routers/            # API 路由
│   │   ├── agents/             # Pydantic AI Agent
│   │   └── services/           # 业务逻辑（生图、超分、切片等）
│   └── tests/
│
└── frontend/                   # Vue 3 + Vite 前端
    ├── Dockerfile              # 多阶段构建（node build → nginx 托管）
    ├── nginx.conf              # Nginx 配置（静态 + API 反代）
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.js
        ├── App.vue
        ├── router/             # Vue Router 路由
        ├── stores/             # Pinia 状态管理
        ├── api/                # Axios 封装的 HTTP 客户端
        ├── views/              # 页面组件
        │   ├── GenerateView    # 效果图生成
        │   ├── PanoView        # 全景图浏览
        │   ├── CompareView     # 方案对比
        │   ├── HistoryView     # 历史记录
        │   └── LoginView       # 登录
        └── assets/
```

## 待定（推荐但未确认，不进代码）

| 项 | 推荐 | 说明 |
|---|---|---|
| 图像生成 | SD + ControlNet | 结构一致性最佳方案，但需 GPU、部署重 |
| 结构提取 | Depth Anything + M-LSD | ControlNet 配套，CPU 可跑 |
| 图像超分 | 阿里云超分 API | 零运维，¥0.06/张 |
| 图片存储 | 腾讯云 COS + CDN | 不存本地 |

> 以上推荐项确认后，逐步加入对应 service 模块和 Dockerfile。

## 快速开始

### 首次拉取项目（一键搭建环境）

```powershell
git clone https://github.com/MacTavishSoap/ai-renovate.git
cd ai-renovate
python scripts/setup_dev.py
```

> 脚本会自动：创建虚拟环境 → 安装锁定依赖 → 创建 .env → 运行测试验证

### 后端开发

```powershell
cd ai-renovate\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.lock
pip install -e . --no-deps
uvicorn app.main:app --reload --port 8000
```

> ⚠️ 使用 `requirements.lock` 而非 `pyproject.toml` 安装，确保版本完全一致
>
> API 文档：http://127.0.0.1:8000/docs

### 前端开发

```powershell
cd ai-renovate\frontend
npm install
npm run dev
```

> 前端开发服务器：http://localhost:5173
>
> 前端会通过 Vite 代理将 `/api` 请求转发到后端 `localhost:8000`

### Docker 一键启动（全部服务）

```powershell
cd ai-renovate
docker compose up -d --build
# backend  → http://localhost:8000
# frontend → http://localhost:80（Nginx 托管）
```

单独重建某个服务：

```powershell
docker compose build backend && docker compose up -d backend
docker compose build frontend && docker compose up -d frontend
```

## 协作流程

### 邀请协作者

仓库 Owner 在 GitHub 页面操作：
1. 打开 https://github.com/MacTavishSoap/ai-renovate/settings/access
2. 点击 **Add people** → 输入对方 GitHub 用户名
3. 权限选 **Write** → 发送邀请
4. 对方邮箱收到邀请，接受后即可推送代码

或用命令行快速邀请：

```powershell
gh api repos/MacTavishSoap/ai-renovate/collaborators/<对方用户名> -X PUT -f permission=push
```

### 日常开发（通过 Pull Request）

```powershell
# 1. 开工前拉取最新代码
git pull

# 2. 创建功能分支（不要直接改 main）
git checkout -b feature/你的功能名

# 3. 写代码...
git add -A
git commit -m "描述你改了什么"
git push -u origin feature/你的功能名

# 4. 去 GitHub 创建 Pull Request
# 5. 至少1人 review 通过后合并 → CI/CD 自动跑
```

> **分支保护规则**：`main` 分支受保护，普通协作者不能直接 push，必须走 PR + 1人审批。Owner 可以 bypass 但建议也走 PR 流程。

### 环境统一

虚拟环境（venv / node_modules）**不提交到仓库**，通过以下文件保证所有协作者环境一致：

| 文件 | 作用 |
|------|------|
| `backend/.python-version` | 固定 Python 3.12.7 |
| `backend/requirements.lock` | 🔒 锁定所有 Python 依赖精确版本（100+ 包） |
| `frontend/package-lock.json` | 🔒 锁定所有前端依赖精确版本 |
| `scripts/setup_dev.py` | 一键搭建脚本 |

朋友拉下来后只需：

```powershell
python scripts/setup_dev.py   # 后端环境一键搞定
cd frontend && npm install     # 前端环境
```

### 环境更新（依赖变化时）

后端加了新依赖：

```powershell
cd backend
venv\Scripts\activate
pip install -e ".[dev]"          # 安装新依赖
pip freeze > requirements.lock   # 重新锁定
git add requirements.lock pyproject.toml
git commit -m "chore: 更新后端依赖锁定"
```

前端加了新依赖：

```powershell
cd frontend
npm install 新包名
git add package.json package-lock.json
git commit -m "chore: 更新前端依赖"
```

## CI/CD

| Workflow | 触发条件 | 作用 |
|----------|---------|------|
| `ci.yml` | push/PR 到 main | 编译检查 + pytest 测试 |
| `cd-build.yml` | push 到 main / 打 tag | 构建 backend + frontend Docker 镜像 |

CI 必须通过才能合并 PR。CD 会自动构建 Docker 镜像，后续如需推送到镜像仓库（Docker Hub / 阿里云 ACR），在仓库 Settings → Secrets 配置凭据后取消注释 `cd-build.yml` 中的推送步骤即可。

## 设计原则

1. **每个服务一个 Dockerfile** — 可以单独 build、单独更新
2. **版本迭代** — 改了 backend 就 `docker compose build backend && up -d backend`，不动 frontend
3. **配置走环境变量** — `.env` 文件管理所有密钥/配置，不硬编码
4. **未确认的不落代码** — 推荐方案写在文档里，确认后才写 service + Dockerfile
