"""
Модели для авторизации 
"""
#импортируем библиотеки
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Model
from uuid import UUID
from pydantic import EmailStr
from typing import Optional
from tasks.models import Task

class User(Model):
    __tablename__ = 'user'
    id:Mapped[UUID] = mapped_column(primary_key=True, nullable=False)
    name:Mapped[str] = mapped_column(nullable=False)
    email:Mapped[EmailStr] = mapped_column(nullable=False, unique=True)
    password:Mapped[str] = mapped_column(nullable=False)
    is_verified:Mapped[bool] = mapped_column(default=False)
    verification_code:Mapped[Optional[str]] = mapped_column(default=None)
    #модель "один"
    tasks:Mapped[list['Task']] = relationship(back_populates='user')