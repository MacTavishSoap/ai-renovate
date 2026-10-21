"""SQLAlchemy ORM 模型"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, relationship


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
    structure_state_url = Column(Text)
    output_image_url = Column(Text)
    pano_url = Column(Text)
    status = Column(String(20), default="pending")
    cost = Column(Integer)  # 单位：分
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="generations")
