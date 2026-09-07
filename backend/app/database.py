"""SQLite 数据库连接 + SQLAlchemy 模型

两张表：users + generations（按 TECH_SPEC.md 设计）
"""

import os
from datetime import datetime
from pathlib import Path

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker

from .config import settings


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    phone = Column(String(20), unique=True, nullable=False)
    credits = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)

    generations = relationship("Generation", back_populates="user")


class Generation(Base):
    __tablename__ = "generations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String(20), nullable=False)  # 'effect' | 'pano'
    input_image_url = Column(Text)
    structure_state_url = Column(Text)  # 结构状态（深度图+直线图），待确认方案
    output_image_url = Column(Text)
    pano_url = Column(Text)
    status = Column(String(20), default="pending")
    cost = Column(Integer)  # 单位：分
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="generations")


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
    Base.metadata.create_all(engine)


def get_db():
    """FastAPI 依赖注入：获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
