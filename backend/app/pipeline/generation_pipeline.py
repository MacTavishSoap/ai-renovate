"""Generation Pipeline — 核心生成流程编排

流程：
  1. 意图解析（Agent）
  2. 结构状态提取（待实现）
  3. 图像生成（API）
  4. 质量验收（Agent）
  5. 后处理（超分/切片/上传）
  6. 更新任务状态

每个步骤都是独立函数，Agent 只在步骤 1 和 4 起作用。
"""

import asyncio
import logging
from dataclasses import dataclass
from enum import Enum

from ..agents import generation_agent
from ..config import settings
from ..services import ImageService

logger = logging.getLogger(__name__)


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


@dataclass
class PipelineContext:
    """Pipeline 执行上下文"""
    job_id: int
    user_id: int
    type: str              # 'effect' | 'pano'
    input_image_url: str | None
    style: str
    room_type: str
    work_type: str | None
    extra_prompt: str | None

    # 中间产物
    intent: dict | None = None
    structure_state: dict | None = None
    generated_image: bytes | None = None
    output_url: str | None = None
    quality_passed: bool | None = None
    quality_score: int | None = None

    # 状态
    current_step: str = ""
    steps: dict[str, StepStatus] = None

    def __post_init__(self):
        if self.steps is None:
            self.steps = {
                "intent_parse": StepStatus.PENDING,
                "structure_extract": StepStatus.PENDING,
                "image_generate": StepStatus.PENDING,
                "quality_check": StepStatus.PENDING,
                "post_process": StepStatus.PENDING,
            }


class GenerationPipeline:
    """生成 Pipeline"""

    def __init__(self, ctx: PipelineContext):
        self.ctx = ctx
        self.image_service = ImageService()

    async def run(self) -> dict:
        """执行完整 Pipeline"""
        logger.info(f"[{self.ctx.job_id}] Pipeline 开始")

        try:
            # 1. 意图解析
            await self._step_intent_parse()
            
            # 2. 结构提取（占位，后续接 Depth Anything + M-LSD）
            await self._step_structure_extract()
            
            # 3. 图像生成
            await self._step_image_generate()
            
            # 4. 质量验收
            await self._step_quality_check()
            
            # 5. 后处理（占位：超分/切片/上传）
            await self._step_post_process()

            logger.info(f"[{self.ctx.job_id}] Pipeline 完成")
            return {"status": "done", "output_url": self.ctx.output_url}

        except Exception as e:
            logger.error(f"[{self.ctx.job_id}] Pipeline 失败: {e}")
            self.ctx.steps[self.ctx.current_step] = StepStatus.FAILED
            raise

    async def _update_step(self, step: str, status: StepStatus):
        self.ctx.steps[step] = status
        self.ctx.current_step = step
        logger.info(f"[{self.ctx.job_id}] Step '{step}' -> {status.value}")

    async def _step_intent_parse(self):
        """步骤 1：意图解析"""
        await self._update_step("intent_parse", StepStatus.RUNNING)
        
        # 如果用户已经选了风格/房间类型，可能不需要再解析
        # 这里演示完整流程：先拼装用户输入，再让 Agent 优化
        user_input = f"风格：{self.ctx.style}，房间：{self.ctx.room_type}"
        if self.ctx.extra_prompt:
            user_input += f"，要求：{self.ctx.extra_prompt}"

        intent = await generation_agent.parse_intent(user_input)
        self.ctx.intent = intent.model_dump()
        await self._update_step("intent_parse", StepStatus.DONE)

    async def _step_structure_extract(self):
        """步骤 2：结构状态提取（占位）"""
        await self._update_step("structure_extract", StepStatus.RUNNING)
        
        # TODO: 接 Depth Anything V2 + M-LSD
        # 1. 下载 input_image_url
        # 2. 跑 depth estimation
        # 3. 跑 line detection
        # 4. 存 COS，返回 state dict
        
        self.ctx.structure_state = {
            "status": "placeholder",
            "message": "结构提取待实现"
        }
        await self._update_step("structure_extract", StepStatus.DONE)

    async def _step_image_generate(self):
        """步骤 3：图像生成"""
        await self._update_step("image_generate", StepStatus.RUNNING)

        # 使用 Agent 生成的 prompt（或用户原始输入）
        prompt = self.ctx.intent.get("prompt", "") if self.ctx.intent else self.ctx.style
        
        image_bytes = await self.image_service.generate(
            prompt=prompt,
            reference_image=self.ctx.input_image_url,  # 如果有参考图，传 base64
        )
        
        self.ctx.generated_image = image_bytes
        # TODO: 临时存本地/上传 COS
        
        await self._update_step("image_generate", StepStatus.DONE)

    async def _step_quality_check(self):
        """步骤 4：质量验收"""
        await self._update_step("quality_check", StepStatus.RUNNING)

        # TODO: 实际需要把图上传后拿 URL，再传给多模态模型
        # 当前占位：直接通过
        requirements = f"风格：{self.ctx.style}，房间：{self.ctx.room_type}"
        
        # 演示：模拟 Agent 调用
        # result = await generation_agent.check_quality(image_url, requirements)
        # self.ctx.quality_passed = result.passed
        # self.ctx.quality_score = result.score
        
        # 占位：直接通过，后续接 M-LSD 重合度验收
        self.ctx.quality_passed = True
        self.ctx.quality_score = 80
        
        await self._update_step("quality_check", StepStatus.DONE)

    async def _step_post_process(self):
        """步骤 5：后处理"""
        await self._update_step("post_process", StepStatus.RUNNING)

        # TODO:
        # 1. 阿里云超分
        # 2. 多分辨率切片
        # 3. 上传 COS
        # 4. 返回 CDN URL

        self.ctx.output_url = "/outputs/placeholder.jpg"  # 占位
        await self._update_step("post_process", StepStatus.DONE)
