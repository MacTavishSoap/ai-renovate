"""用户路由 — 登录 / 验证码 / 积分"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.schemas import LoginRequest, LoginResponse, SendCodeRequest

router = APIRouter(prefix="/api", tags=["用户"])

# 临时存储验证码（生产换阿里云短信）
_code_store: dict[str, str] = {}


@router.post("/send-code")
async def send_code(req: SendCodeRequest):
    """发送验证码（当前 mock，返回固定码）"""
    # TODO: 接阿里云短信
    code = "123456"
    _code_store[req.phone] = code
    return {"message": "验证码已发送", "dev_code": code}  # 开发期返回，上线删


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    """手机号 + 验证码登录"""
    stored = _code_store.get(req.phone)
    if not stored or stored != req.code:
        raise HTTPException(status_code=400, detail="验证码错误或已过期")

    _code_store.pop(req.phone, None)

    # 查或建用户
    from ..database import User
    user = db.query(User).filter(User.phone == req.phone).first()
    if not user:
        user = User(phone=req.phone, credits=3)
        db.add(user)
        db.commit()
        db.refresh(user)

    # TODO: 签发 JWT
    token = f"mock-token-{user.id}"

    return LoginResponse(token=token, user_id=user.id, credits=user.credits)
