"""通用 CRUD 仓库基类"""

from typing import Any, Generic, TypeVar

from sqlalchemy.orm import Session

from ..models.models import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepo(Generic[ModelT]):
    """通用 CRUD 模板，子类只需声明 model 和 id 字段"""

    model: type[ModelT]

    def __init__(self, db: Session):
        self.db = db

    def get(self, id: int) -> ModelT | None:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_or_raise(self, id: int) -> ModelT:
        """查不到抛异常"""
        obj = self.get(id)
        if not obj:
            from ..core.exceptions import NotFoundError
            raise NotFoundError(self.model.__name__)
        return obj

    def create(self, **kwargs) -> ModelT:
        obj = self.model(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: ModelT, **kwargs) -> ModelT:
        for k, v in kwargs.items():
            if v is not None:
                setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: ModelT) -> None:
        self.db.delete(obj)
        self.db.commit()

    def list(self, skip: int = 0, limit: int = 20, **filters) -> list[ModelT]:
        query = self.db.query(self.model)
        for k, v in filters.items():
            if v is not None and hasattr(self.model, k):
                query = query.filter(getattr(self.model, k) == v)
        return query.order_by(self.model.id.desc()).offset(skip).limit(limit).all()

    def count(self, **filters) -> int:
        query = self.db.query(self.model)
        for k, v in filters.items():
            if v is not None and hasattr(self.model, k):
                query = query.filter(getattr(self.model, k) == v)
        return query.count()
