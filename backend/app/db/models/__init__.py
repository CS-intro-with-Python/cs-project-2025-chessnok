"""
Импорт всех моделей для автоматического обнаружения Alembic.
Все новые модели должны быть импортированы здесь.
"""


from app.db.base import Base
from .teacher import Teacher
__all__ = ["Base", "Teacher"]
