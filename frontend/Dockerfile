# AI 家装 — 前端镜像
# 当前是占位，后续接入 Gradio 生成界面或静态页面
FROM python:3.12.7-slim

WORKDIR /app

RUN pip install --no-cache-dir gradio>=4.44

COPY . .

EXPOSE 7860

# 占位启动命令，后续替换为真正的 Gradio 入口
CMD ["python", "-c", "print('frontend placeholder — TODO: 接入 Gradio 生成界面')"]
