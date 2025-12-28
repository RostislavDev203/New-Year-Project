"""
Схемы для задач
"""
#импортируем библиотеки
from pydantic import BaseModel, Field

class Base(BaseModel):
    pass

class Create_Task(Base):
    token:str
    name:str = Field(..., min_length=1, max_length=50, description="Название задачи")
    description:str = Field(..., min_length=1, max_length=200, description="Описание")

