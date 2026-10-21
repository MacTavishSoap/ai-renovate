"""生成服务 — 任务生命周期管理"""

from sqlalchemy.orm import Session

from ..core import GenerationCreateRequest
from ..pipeline import GenerationPipeline, PipelineContext
from ..repos import GenerationRepo


class GenerationService:
    """生成任务服务"""

    def __init__(self, db: Session):
        self.db = db
        self.repo = GenerationRepo(db)

    def create(self, user_id: int, req: GenerationCreateRequest) -> dict:
        """创建生成任务，返回任务信息"""
        job = self.repo.create(
            user_id=user_id,
            type=req.type,
            status="pending",
            input_image_url=req.input_image_url,
            style=req.style,
            room_type=req.room_type,
            work_type=req.work_type,
            extra_prompt=req.extra_prompt,
        )
        return self._to_dict(job)

    def list(self, user_id: int, skip: int = 0, limit: int = 20) -> tuple[list[dict], int]:
        """用户任务列表"""
        items, total = self.repo.list_by_user(user_id, skip, limit)
        return [self._to_dict(i) for i in items], total

    def get(self, generation_id: int) -> dict:
        """获取单个任务"""
        job = self.repo.get_or_raise(generation_id)
        return self._to_dict(job)

    def update_status(self, generation_id: int, status: str, **kwargs) -> dict:
        """更新任务状态"""
        job = self.repo.get_or_raise(generation_id)
        job = self.repo.update(job, status=status, **kwargs)
        return self._to_dict(job)

    def _to_dict(self, job) -> dict:
        return {
            "id": job.id,
            "user_id": job.user_id,
            "type": job.type,
            "status": job.status,
            "input_image_url": job.input_image_url,
            "output_image_url": job.output_image_url,
            "pano_url": job.pano_url,
            "cost": job.cost,
            "created_at": job.created_at,
        }


async def run_generation_pipeline(job_id: int, req: GenerationCreateRequest) -> dict:
    """异步执行生成 Pipeline"""
    ctx = PipelineContext(
        job_id=job_id,
        user_id=1,  # TODO: 从 token 解析
        type=req.type,
        input_image_url=req.input_image_url,
        style=req.style,
        room_type=req.room_type,
        work_type=req.work_type,
        extra_prompt=req.extra_prompt,
    )
    pipeline = GenerationPipeline(ctx)
    return await pipeline.run()
