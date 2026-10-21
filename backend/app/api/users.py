"""用户路由 — 只做请求分发"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..api.deps import get_db
from ..core import LoginRequest, LoginResponse, SendCodeRequest
from ..services import UserService

router = APIRouter(prefix="/api", tags=["用户"])


@router.post("/send-code")
async def send_code(req: SendCodeRequest, db: Session = Depends(get_db)):
    """发送验证码"""
    svc = UserService(db)
    return svc.send_code(req.phone)


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    """手机号 + 验证码登录"""
    svc = UserService(db)
    return svc.login(req.phone, req.code)
