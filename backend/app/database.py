"""SQLite 数据库连接

注意：ORM 模型已迁移到 models/models.py
"""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import settings

# 引擎 — 确保数据库目录存在，避免 SQLite "unable to open database file"
_db_url = settings.database_url
if _db_url.startswith("sqlite:///") and not _db_url.startswith("sqlite:////"):
    _db_path = Path(_db_url.replace("sqlite:///", "", 1))
    if not _db_path.is_absolute():
        _db_path = Path(__file__).resolve().parent.parent / _db_path
    _db_path.parent.mkdir(parents=True, exist_ok=True)
    _db_url = f"sqlite:///{_db_path.as_posix()}"

engine = create_engine(
    _db_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db():
    """启动时建表"""
    from .models.models import Base
    Base.metadata.create_all(engine)


# 为向后兼容保留旧导入路径
from .models.models import Base, Generation, User
from .api.deps import get_db

__all__ = ["engine", "SessionLocal", "init_db", "get_db", "Base", "User", "Generation"]
