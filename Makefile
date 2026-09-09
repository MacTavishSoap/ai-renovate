# ================================================================
# AI 家装 (ai-renovate) — 统一构建 / 发布 / 开发工具集
#
# 三个模块可独立维护:
#   make backend-*    后端 (FastAPI)
#   make frontend-*   前端 (Vue 3 + Vite)
#   make ci-*         CI/CD 工作流
#
# 完整上线流程:
#   1. 本机:  make release      (构建+打标签+推送到镜像仓库)
#   2. 服务器: make server-update (SSH 登录服务器拉取+重启)
#
# 常用命令:
#   make dev          一键启动开发环境 (后端+前端)
#   make build        构建所有 Docker 镜像
#   make release      发布所有镜像到仓库 (构建+打标签+推送)
#   make help         查看全部命令
# ================================================================

# ---- 镜像仓库配置 ----
REGISTRY    := ccr.ccs.tencentyun.com
NAMESPACE   := ai-renovate

# ---- 版本号 (独立维护) ----
BACKEND_VERSION  := v0.1.0
FRONTEND_VERSION := v0.1.0

# ---- 镜像地址 ----
BACKEND_IMAGE  := $(REGISTRY)/$(NAMESPACE)/backend
FRONTEND_IMAGE := $(REGISTRY)/$(NAMESPACE)/frontend

# ---- 端口 ----
BACKEND_PORT  := 8000
FRONTEND_PORT := 8080

# ---- 服务器 SSH (发布后手动登录拉取) ----
SERVER_USER := root
SERVER_HOST := your-server-ip
SERVER_PATH := /opt/ai-renovate

# ---- 颜色 ----
CYAN  := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RESET := \033[0m

.PHONY: help \
        dev dev-backend dev-frontend stop-dev \
        backend-build backend-tag backend-push backend-release backend-run backend-logs \
        frontend-build frontend-tag frontend-push frontend-release frontend-run frontend-logs \
        build tag push release \
        server-ssh server-pull server-up server-update \
        ci-test ci-build ci-frontend-check \
        clean clean-all

## ================================================================
## 开发命令
## ================================================================

## 一键启动开发环境 (docker compose up)
dev:
	@echo "$(CYAN)🚀 启动开发环境...$(RESET)"
	docker compose up -d --build
	@echo ""
	@echo "$(GREEN)✅ 开发环境已启动$(RESET)"
	@echo "   后端:  http://localhost:$(BACKEND_PORT)"
	@echo "   前端:  http://localhost:$(FRONTEND_PORT)"
	@echo "   日志:  make backend-logs / make frontend-logs"

## 仅启动后端
dev-backend:
	docker compose up -d --build backend
	@echo "$(GREEN)✅ 后端已启动 → http://localhost:$(BACKEND_PORT)$(RESET)"

## 仅启动前端
dev-frontend:
	docker compose up -d --build frontend
	@echo "$(GREEN)✅ 前端已启动 → http://localhost:$(FRONTEND_PORT)$(RESET)"

## 停止开发环境
stop-dev:
	docker compose down
	@echo "$(YELLOW)⏹  开发环境已停止$(RESET)"

## ================================================================
## 后端 (独立维护)
## ================================================================

## 构建后端镜像
backend-build:
	@echo "$(CYAN)🏗️  构建后端镜像...$(RESET)"
	docker build -t ai-renovate-backend:latest ./backend

## 后端打标签
backend-tag: backend-build
	docker tag ai-renovate-backend:latest $(BACKEND_IMAGE):$(BACKEND_VERSION)
	docker tag ai-renovate-backend:latest $(BACKEND_IMAGE):latest

## 推送后端镜像到仓库
backend-push: backend-tag
	@echo "$(CYAN)📤 推送后端镜像...$(RESET)"
	docker push $(BACKEND_IMAGE):$(BACKEND_VERSION)
	docker push $(BACKEND_IMAGE):latest
	@echo "$(GREEN)✅ 后端已推送: $(BACKEND_IMAGE):$(BACKEND_VERSION)$(RESET)"

## 后端发布 (构建+打标签+推送) — 之后去服务器 make server-update
backend-release: backend-push
	@echo "$(GREEN)✅ 后端发布完成 → 下一步: 服务器上执行 docker compose pull && docker compose up -d backend$(RESET)"

## 本地运行后端 (不用 Docker)
backend-run:
	cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port $(BACKEND_PORT)

## 查看后端日志
backend-logs:
	docker compose logs -f backend

## ================================================================
## 前端 (独立维护)
## ================================================================

## 构建前端镜像
frontend-build:
	@echo "$(CYAN)🏗️  构建前端镜像...$(RESET)"
	docker build -t ai-renovate-frontend:latest ./frontend

## 前端打标签
frontend-tag: frontend-build
	docker tag ai-renovate-frontend:latest $(FRONTEND_IMAGE):$(FRONTEND_VERSION)
	docker tag ai-renovate-frontend:latest $(FRONTEND_IMAGE):latest

## 推送前端镜像到仓库
frontend-push: frontend-tag
	@echo "$(CYAN)📤 推送前端镜像...$(RESET)"
	docker push $(FRONTEND_IMAGE):$(FRONTEND_VERSION)
	docker push $(FRONTEND_IMAGE):latest
	@echo "$(GREEN)✅ 前端已推送: $(FRONTEND_IMAGE):$(FRONTEND_VERSION)$(RESET)"

## 前端发布 (构建+打标签+推送) — 之后去服务器 make server-update
frontend-release: frontend-push
	@echo "$(GREEN)✅ 前端发布完成 → 下一步: 服务器上执行 docker compose pull && docker compose up -d frontend$(RESET)"

## 本地运行前端 (不用 Docker, 需先 npm install)
frontend-run:
	cd frontend && npm run dev

## 查看前端日志
frontend-logs:
	docker compose logs -f frontend

## ================================================================
## 全局命令 (同时操作前后端)
## ================================================================

## 构建所有镜像
build: backend-build frontend-build
	@echo "$(GREEN)✅ 全部构建完成$(RESET)"

## 打所有标签
tag: backend-tag frontend-tag

## 推送所有镜像到仓库
push: backend-push frontend-push
	@echo "$(GREEN)✅ 全部推送完成$(RESET)"

## 发布所有镜像 (构建+打标签+推送) — 还需去服务器拉取
release: push
	@echo ""
	@echo "$(GREEN)✅✅ 镜像已发布到仓库!$(RESET)"
	@echo "   后端:  $(BACKEND_IMAGE):$(BACKEND_VERSION)"
	@echo "   前端:  $(FRONTEND_IMAGE):$(FRONTEND_VERSION)"
	@echo ""
	@echo "$(YELLOW)⚠️  镜像还在仓库，服务器还没更新!$(RESET)"
	@echo "   下一步: SSH 登录服务器后执行 make server-update"
	@echo "   或手动: docker compose pull && docker compose up -d"

## ================================================================
## 服务器端命令 (需先 SSH 登录服务器)
## ================================================================

## SSH 登录服务器
server-ssh:
	ssh $(SERVER_USER)@$(SERVER_HOST)

## 服务器: 拉取最新镜像
server-pull:
	cd $(SERVER_PATH) && docker compose pull

## 服务器: 重启容器
server-up:
	cd $(SERVER_PATH) && docker compose up -d

## 服务器: 一键更新 (拉取+重启) — 在服务器上执行
server-update: server-pull server-up
	@echo "$(GREEN)✅ 服务器已更新!$(RESET)"

## ================================================================
## CI/CD 工作流 (本地模拟 GitHub Actions)
## ================================================================

## 运行后端测试 (等同 CI)
ci-test:
	@echo "$(CYAN)🧪 运行后端测试...$(RESET)"
	cd backend && pip install -e ".[dev]" && python -m pytest tests/ -v --tb=short

## 前端编译检查 (CI 补充)
ci-frontend-check:
	@echo "$(CYAN)🔍 前端编译检查...$(RESET)"
	cd frontend && npm run build

## 构建 CI 镜像 (等同 CD)
ci-build: build
	@echo "$(GREEN)✅ CI 构建完成$(RESET)"

## ================================================================
## 清理
## ================================================================

## 清理悬空镜像
clean:
	docker image prune -f
	@echo "$(GREEN)✅ 已清理悬空镜像$(RESET)"

## 深度清理 (包含未使用的镜像)
clean-all:
	docker image prune -a -f
	docker compose down -v
	@echo "$(GREEN)✅ 深度清理完成$(RESET)"

## ================================================================
## 帮助
## ================================================================

help:
	@echo "$(CYAN)╔══════════════════════════════════════════════════╗$(RESET)"
	@echo "$(CYAN)║       AI 家装 — Makefile 命令手册               ║$(RESET)"
	@echo "$(CYAN)╚══════════════════════════════════════════════════╝$(RESET)"
	@echo ""
	@echo "$(YELLOW)── 开发 ──$(RESET)"
	@echo "  make dev              一键启动开发环境 (docker compose)"
	@echo "  make dev-backend      仅启动后端"
	@echo "  make dev-frontend     仅启动前端"
	@echo "  make stop-dev         停止开发环境"
	@echo ""
	@echo "$(YELLOW)── 后端 (版本 $(BACKEND_VERSION)) ──$(RESET)"
	@echo "  make backend-build    构建后端镜像"
	@echo "  make backend-release  发布后端 (构建+标签+推送) → 仓库"
	@echo "  make backend-run      本地运行后端 (不用 Docker)"
	@echo "  make backend-logs     查看后端日志"
	@echo ""
	@echo "$(YELLOW)── 前端 (版本 $(FRONTEND_VERSION)) ──$(RESET)"
	@echo "  make frontend-build   构建前端镜像"
	@echo "  make frontend-release 发布前端 (构建+标签+推送) → 仓库"
	@echo "  make frontend-run     本地运行前端 (不用 Docker)"
	@echo "  make frontend-logs    查看前端日志"
	@echo ""
	@echo "$(YELLOW)── 全局 ──$(RESET)"
	@echo "  make build            构建所有镜像"
	@echo "  make release          发布所有镜像 → 仓库"
	@echo ""
	@echo "$(YELLOW)── 服务器 (SSH 登录后在服务器执行) ──$(RESET)"
	@echo "  make server-update    拉取最新镜像 + 重启容器"
	@echo "  make server-pull      仅拉取镜像"
	@echo "  make server-up        仅重启容器"
	@echo ""
	@echo "$(YELLOW)── CI/CD ──$(RESET)"
	@echo "  make ci-test          运行后端测试"
	@echo "  make ci-frontend-check 前端编译检查"
	@echo "  make ci-build         构建 CI 镜像"
	@echo ""
	@echo "$(YELLOW)── 清理 ──$(RESET)"
	@echo "  make clean            清理悬空镜像"
	@echo "  make clean-all        深度清理 (含未使用镜像+卷)"
	@echo ""
	@echo "$(YELLOW)── 完整上线流程 ──$(RESET)"
	@echo "  1. 本机:  make release          (构建+推送到镜像仓库)"
	@echo "  2. SSH 登录服务器"
	@echo "  3. 服务器: make server-update   (拉取+重启)"
	@echo ""
	@echo "$(YELLOW)── 版本号修改 ──$(RESET)"
	@echo "  后端: 修改 Makefile 顶部 BACKEND_VERSION"
	@echo "  前端: 修改 Makefile 顶部 FRONTEND_VERSION"
	@echo "  前端 package.json 也需同步修改 version 字段"
