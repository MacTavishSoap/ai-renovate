"""生成路由 — 只做请求分发"""

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from ..api.deps import get_db
from ..core import GenerationCreateRequest, GenerationListResponse, GenerationResponse
from ..services import GenerationService, run_generation_pipeline

router = APIRouter(prefix="/api/generations", tags=["生成"])


@router.post("", response_model=GenerationResponse)
async def create_generation(
    req: GenerationCreateRequest,
    bg: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """提交生成任务，异步执行 Pipeline"""
    # TODO: 从 token 获取 user_id
    user_id = 1
    svc = GenerationService(db)
    job = svc.create(user_id, req)

    # 后台执行 Pipeline
    bg.add_task(run_generation_pipeline, job["id"], req)
    return job


@router.get("", response_model=GenerationListResponse)
async def list_generations(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """生成历史列表"""
    user_id = 1  # TODO: 从 token 获取
    svc = GenerationService(db)
    items, total = svc.list(user_id, skip, limit)
    return GenerationListResponse(total=total, items=items)


@router.get("/{generation_id}", response_model=GenerationResponse)
async def get_generation(generation_id: int, db: Session = Depends(get_db)):
    """获取单条生成详情"""
    svc = GenerationService(db)
    return svc.get(generation_id)
