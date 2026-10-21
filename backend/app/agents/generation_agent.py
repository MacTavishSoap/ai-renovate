"""Generation Agent — 意图解析 + 质量检查

两个 LLM 决策点：
1. 意图解析：用户文字 → 结构化生成参数
2. 质量检查：生成图 → 是否合格

其他流程是纯函数，不走 Agent。
"""

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from ..config import settings
from .providers import LLMProvider, ProviderConfig, ProviderType, create_provider


# ===== 结构化输出模型 =====
class GenerationIntent(BaseModel):
    """意图解析结果"""
    room_type: str = Field(description="房间类型：客厅/卧室/厨房/卫生间...")
    style: str = Field(description="装修风格：北欧/日式/现代简约...")
    work_type: str | None = Field(default=None, description="施工类型：整装/软装/局部改造")
    prompt: str = Field(description="给图像模型的完整英文 prompt")


class QualityCheckResult(BaseModel):
    """质量检查结果"""
    passed: bool = Field(description="是否通过")
    score: int = Field(ge=0, le=100, description="质量评分 0-100")
    issues: list[str] = Field(default_factory=list, description="不合格原因")


# ===== Agent 实例 =====
def _create_llm_provider() -> LLMProvider:
    """从 settings 创建 LLM Provider"""
    config = ProviderConfig(
        provider_type=ProviderType.LLM,
        provider=settings.llm_model.split("/")[-1] if "/" in settings.llm_model else settings.llm_model,
        base_url=settings.llm_api_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
    )
    return create_provider(config)


def create_intent_agent() -> Agent:
    """创建意图解析 Agent"""
    return Agent(
        model=settings.llm_model,
        result_retries=3,
        output_type=GenerationIntent,
        system_prompt=(
            "你是家装设计助手。用户会用自然语言描述想要的装修效果，"
            "你需要提取出：房间类型、装修风格、施工类型，并生成一段"
            "专业的英文 prompt 供图像生成模型使用。"
        ),
    )


def create_quality_agent() -> Agent:
    """创建质量检查 Agent"""
    return Agent(
        model=settings.llm_model,
        result_retries=2,
        output_type=QualityCheckResult,
        system_prompt=(
            "你是家装效果图质检员。请评估这张装修效果图的质量：\n"
            "1. 结构一致性：家具、门窗位置是否合理\n"
            "2. 风格一致性：是否符合指定风格\n"
            "3. 图像质量：清晰度、色彩、光照\n"
            "返回是否合格及评分(0-100)"
        ),
    )


# ===== Agent 调用接口 =====
async def parse_intent(user_input: str) -> GenerationIntent:
    """意图解析：用户文字 → 结构化参数"""
    agent = create_intent_agent()
    result = await agent.run(user_input)
    return result.output


async def check_quality(image_url: str, requirements: str) -> QualityCheckResult:
    """质量检查：图像 URL + 要求 → 是否合格
    
    注意：实际需要传图片给多模态模型，当前是占位
    """
    agent = create_quality_agent()
    # TODO: 传图片 URL 给多模态模型
    result = await agent.run(
        f"请检查这张效果图：{image_url}\n要求：{requirements}"
    )
    return result.output
