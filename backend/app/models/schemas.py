"""Pydantic 请求/响应模型"""

from datetime import datetime

from pydantic import BaseModel


# ===== 用户相关 =====
class SendCodeRequest(BaseModel):
    phone: str


class LoginRequest(BaseModel):
    phone: str
    code: str


class LoginResponse(BaseModel):
    token: str
    user_id: int
    credits: int


# ===== 生成相关 =====
class GenerationCreateRequest(BaseModel):
    """用户提交生成任务"""
    type: str  # 'effect' | 'pano'
    input_image_url: str | None = None
    style: str
    room_type: str
    work_type: str | None = None
    extra_prompt: str | None = None


class GenerationResponse(BaseModel):
    id: int
    type: str
    status: str
    input_image_url: str | None
    output_image_url: str | None
    pano_url: str | None
    cost: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class GenerationListResponse(BaseModel):
    total: int
    items: list[GenerationResponse]
