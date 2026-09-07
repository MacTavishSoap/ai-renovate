"""生成路由 — 创建任务 / 列表 / 详情

使用 FastAPI BackgroundTasks 执行异步生成流程。
"""

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import Generation, get_db
from ..models.schemas import (
    GenerationCreateRequest,
    GenerationListResponse,
    GenerationResponse,
)

router = APIRouter(prefix="/api/generations", tags=["生成"])


async def _run_pipeline(job_id: str, params: dict):
    """后台生成流程

    1. 意图解析（Pydantic AI Agent）
    2. 图像生成（gpt-image-2 或 SD+ControlNet，待确认）
    3. 后处理（超分、切片，待确认）
    4. 更新数据库状态

    TODO: 逐步实现，当前是骨架
    """
    print(f"[{job_id}] 生成任务开始: {params}")
    # TODO: 调 agent.parse_intent → image_service.generate_image → ...
    print(f"[{job_id}] 生成任务完成（占位）")


@router.post("", response_model=GenerationResponse)
async def create_generation(
    req: GenerationCreateRequest,
    bg: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """提交生成任务，异步执行"""
    # TODO: 从 token 获取 user_id，临时用 1
    user_id = 1

    job = Generation(
        user_id=user_id,
        type=req.type,
        status="pending",
        input_image_url=req.input_image_url,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # 异步执行
    job_id = str(job.id)
    bg.add_task(_run_pipeline, job_id, req.model_dump())

    return job


@router.get("", response_model=GenerationListResponse)
async def list_generations(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """生成历史列表"""
    # TODO: 按 user_id 过滤
    query = db.query(Generation)
    total = query.count()
    items = query.order_by(Generation.id.desc()).offset(skip).limit(limit).all()
    return GenerationListResponse(total=total, items=items)


@router.get("/{generation_id}", response_model=GenerationResponse)
async def get_generation(generation_id: int, db: Session = Depends(get_db)):
    """获取单条生成详情"""
    item = db.query(Generation).filter(Generation.id == generation_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="未找到")
    return item
