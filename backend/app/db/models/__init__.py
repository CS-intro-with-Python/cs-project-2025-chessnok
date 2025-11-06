"""
Import all models so that Base has them before being imported by Alembic.
"""

from app.db.base import Base

from .teacher import Teacher
from .user import User

__all__ = ["Base", "Teacher", "User"]
