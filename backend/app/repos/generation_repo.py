"""生成任务仓库"""

from sqlalchemy.orm import Session

from ..models.models import Generation
from .base import BaseRepo


class GenerationRepo(BaseRepo[Generation]):
    model = Generation

    def list_by_user(self, user_id: int, skip: int = 0, limit: int = 20) -> tuple[list[Generation], int]:
        """返回 (列表, 总数)"""
        query = self.db.query(Generation).filter(Generation.user_id == user_id)
        total = query.count()
        items = query.order_by(Generation.id.desc()).offset(skip).limit(limit).all()
        return items, total
