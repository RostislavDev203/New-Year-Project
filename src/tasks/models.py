"""
Модели для задач
"""
#импортируем библиотеки
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from uuid import UUID
from db import Model
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from auth.models import User

class Task(Model):
    __tablename__ = 'task'
    id:Mapped[UUID] = mapped_column(primary_key=True, nullable=False)
    name:Mapped[str] = mapped_column(nullable=False)
    description:Mapped[Optional[str]] = mapped_column(default=None)
    is_complete:Mapped[bool] = mapped_column(default=False)
    #модель "много"
    user_id:Mapped[UUID] = mapped_column(ForeignKey('user.id'))
    author:Mapped["User"] = relationship(back_populates="tasks", uselist=False)
