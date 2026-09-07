"""生图服务 — 调用图像生成 API

当前：复用 demo 的 gpt-image-2 API（smile-ai 中转）
待确认：是否切换为 SD + ControlNet（结构一致性）
"""

import base64
import time

import httpx

from ..config import settings


async def generate_image(
    prompt: str,
    size: str = "1024x1024",
    quality: str = "high",
    reference_image: str | None = None,
) -> bytes:
    """调用图像生成 API

    Args:
        prompt: 生成提示词
        size: 图像尺寸
        quality: 质量 auto/high/medium/low
        reference_image: 参考图 base64（可选）

    Returns:
        图片二进制数据

    TODO: 确认是否改用 SD + ControlNet 做结构一致性
    """
    headers = {
        "Authorization": f"Bearer {settings.image_api_key}",
        "Content-Type": "application/json",
    }

    payload: dict = {
        "model": settings.image_model,
        "prompt": prompt,
        "size": size,
        "quality": quality,
        "n": 1,
    }

    if reference_image:
        payload["image"] = reference_image

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{settings.image_api_base_url}/images/generations",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()

    # OpenAI 兼容格式：data[0].b64_json 或 data[0].url
    item = data["data"][0]
    if "b64_json" in item:
        return base64.b64decode(item["b64_json"])
    elif "url" in item:
        async with httpx.AsyncClient(timeout=60) as client:
            img_resp = await client.get(item["url"])
            img_resp.raise_for_status()
            return img_resp.content
    else:
        raise ValueError("API 返回格式异常：无 b64_json 或 url")
