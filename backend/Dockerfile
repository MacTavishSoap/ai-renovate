# AI 家装 — 后端镜像
# 支持分步更新：只改 backend 时 docker compose build backend
FROM python:3.12.7-slim

WORKDIR /app

# 系统依赖（图像处理需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 先拷依赖文件，利用 Docker 层缓存
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# 拷源码
COPY app/ ./app/

# 数据目录（SQLite）
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
