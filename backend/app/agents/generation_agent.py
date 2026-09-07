"""Pydantic AI Agent — 意图解析 / 质量检查 / 一致性判断

三个 LLM 决策点：
1. 意图解析：用户文字 → 结构化生成参数
2. 质量检查：生成图 → 是否合格（待图像生成方案确认后启用）
3. 一致性判断：两张图是否同一房间结构（待结构状态方案确认后启用）
"""

from pydantic import BaseModel
from pydantic_ai import Agent

from ..config import settings


# ===== 结构化输出模型 =====
class GenerationIntent(BaseModel):
    """意图解析结果 — 从用户输入提取结构化参数"""
    room_type: str          # 客厅/卧室/厨房...
    style: str              # 北欧/日式/工业...
    work_type: str | None   # 整装/软装/局部改造
    prompt: str             # 给图像模型的完整 prompt


class QualityCheck(BaseModel):
    """质量检查结果"""
    passed: bool
    issues: list[str]       # 不合格原因
    score: int              # 0-100


# ===== Agent 定义 =====
# 使用 OpenAI 兼容 API（smile-ai 中转），模型名走配置

intent_agent = Agent(
    model=settings.llm_model,
    output_type=GenerationIntent,
    system_prompt=(
        "你是家装设计助手。用户会用自然语言描述想要的装修效果，"
        "你需要提取出：房间类型、装修风格、施工类型，并生成一段"
        "专业的英文 prompt 供图像生成模型使用。"
    ),
)


async def parse_intent(user_input: str) -> GenerationIntent:
    """意图解析：用户文字 → 结构化参数"""
    result = await intent_agent.run(user_input)
    return result.output
