"""用户服务"""

from sqlalchemy.orm import Session

from ..models.schemas import LoginResponse, SendCodeRequest
from ..repos import UserRepo


# 临时存储验证码（生产换阿里云短信）
_code_store: dict[str, str] = {}


class UserService:
    """用户服务"""

    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepo(db)

    def send_code(self, phone: str) -> dict:
        """发送验证码"""
        # TODO: 接阿里云短信
        code = "123456"
        _code_store[phone] = code
        return {"message": "验证码已发送", "dev_code": code}

    def login(self, phone: str, code: str) -> LoginResponse:
        """登录"""
        stored = _code_store.get(phone)
        if not stored or stored != code:
            from ..core.exceptions import ValidationError
            raise ValidationError("验证码错误或已过期")
        _code_store.pop(phone, None)

        # 查或建用户
        user = self.repo.get_by_phone(phone)
        if not user:
            user = self.repo.create(phone=phone, credits=3)

        # TODO: 签发 JWT
        token = f"mock-token-{user.id}"
        return LoginResponse(token=token, user_id=user.id, credits=user.credits)
