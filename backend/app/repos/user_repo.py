"""用户仓库"""

from sqlalchemy.orm import Session

from ..models.models import User
from .base import BaseRepo


class UserRepo(BaseRepo[User]):
    model = User

    def get_by_phone(self, phone: str) -> User | None:
        return self.db.query(User).filter(User.phone == phone).first()
