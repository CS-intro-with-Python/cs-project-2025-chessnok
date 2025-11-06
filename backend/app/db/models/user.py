from sqlalchemy import Boolean, Column, DateTime, String, func

from app.db import Base


class User(Base):
    __tablename__ = "users"

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(String, default="active")
