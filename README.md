# AI 家装项目 · ai-renovate

正式项目仓库，与 demo（`renovate-demo/`、`pano-demo/`）平级。

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
└── frontend/                   # 前端（Gradio 生成界面 / 静态页面）
    └── Dockerfile
```

## 已确定的技术选型

| 层 | 选型 | 状态 |
|---|---|---|
| 后端框架 | FastAPI | ✅ 确定 |
| AI 编排 | Pydantic AI | ✅ 确定 |
| 数据库 | SQLite | ✅ 确定 |
| 部署 | Docker 多服务 | ✅ 确定 |
| 反向代理 | Nginx | ✅ 确定 |

## 待定（推荐但未确认，不进代码）

| 项 | 推荐 | 说明 |
|---|---|---|
| 图像生成 | SD + ControlNet | 结构一致性最佳方案，但需 GPU、部署重 |
| 结构提取 | Depth Anything + M-LSD | ControlNet 配套，CPU 可跑 |
| 图像超分 | 阿里云超分 API | 零运维，¥0.06/张 |
| 图片存储 | 腾讯云 COS + CDN | 不存本地 |
| 全景浏览 | Pannellum | 开源 MIT |

> 以上推荐项确认后，逐步加入对应 service 模块和 Dockerfile。

## 快速开始

### 首次拉取项目（一键搭建环境）

```powershell
git clone https://github.com/MacTavishSoap/ai-renovate.git
cd ai-renovate
python scripts/setup_dev.py
```

> 脚本会自动：创建虚拟环境 → 安装锁定依赖 → 创建 .env → 运行测试验证

### 本地开发（不用 Docker）

```powershell
cd ai-renovate\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.lock
pip install -e . --no-deps
uvicorn app.main:app --reload --port 8000
```

> ⚠️ 使用 `requirements.lock` 而非 `pyproject.toml` 安装，确保版本完全一致

### Docker 开发

```powershell
cd ai-renovate
docker compose up -d
# backend → http://localhost:8000
# frontend → http://localhost:7860
```

## 协作流程

### 邀请协作者

仓库 Owner 在 GitHub 页面操作：
1. 打开 https://github.com/MacTavishSoap/ai-renovate/settings/access
2. 点击 **Add people** → 输入对方 GitHub 用户名
3. 权限选 **Write** → 发送邀请
4. 对方邮箱收到邀请，接受后即可推送代码

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

### 环境更新（依赖变化时）

当 `pyproject.toml` 增删依赖后，重新生成锁定文件：

```powershell
cd backend
venv\Scripts\activate
pip install -e ".[dev]"          # 安装新依赖
pip freeze > requirements.lock   # 重新锁定
git add requirements.lock
git commit -m "chore: 更新依赖锁定"
```

## 设计原则

1. **每个服务一个 Dockerfile** — 可以单独 build、单独更新
2. **版本迭代** — 改了 backend 就 `docker compose build backend && up -d backend`，不动 frontend
3. **配置走环境变量** — `.env` 文件管理所有密钥/配置，不硬编码
4. **未确认的不落代码** — 推荐方案写在文档里，确认后才写 service + Dockerfile
