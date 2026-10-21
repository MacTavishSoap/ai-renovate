"""生图服务 — 调用图像生成 API

当前：复用 demo 的 gpt-image-2 API（smile-ai 中转）
待确认：是否切换为 SD + ControlNet（结构一致性）
"""

import base64

import httpx

from ..config import settings


class ImageService:
    """图像生成服务"""

    def __init__(self):
        self.base_url = settings.image_api_base_url
        self.api_key = settings.image_api_key
        self.model = settings.image_model
        self.default_quality = settings.image_default_quality
        self.default_size = settings.image_default_size

    async def generate(
        self,
        prompt: str,
        size: str | None = None,
        quality: str | None = None,
        reference_image: str | None = None,
    ) -> bytes:
        """调用图像生成 API

        Args:
            prompt: 生成提示词
            size: 图像尺寸，默认 1024x1024
            quality: 质量 auto/high/medium/low
            reference_image: 参考图（URL 或 base64）

        Returns:
            图片二进制数据
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload: dict = {
            "model": self.model,
            "prompt": prompt,
            "size": size or self.default_size,
            "quality": quality or self.default_quality,
            "n": 1,
        }

        if reference_image:
            # TODO: 支持 URL 下载后转 base64
            # 当前假设传入的是 base64
            payload["image"] = reference_image

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.base_url}/images/generations",
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

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.base_url}/models")
                return resp.status_code == 200
        except Exception:
            return False
