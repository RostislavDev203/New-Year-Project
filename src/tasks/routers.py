"""
Роутер для задач
"""
#импортируем библиотеки
from fastapi import APIRouter, Depends
from typing import Annotated
from .schemas import Create_Task

#Создаем роутер tasks
tasks = APIRouter(prefix='/tasks', tags=["Tasks"])

@tasks.post('/create_task')
async def create_taks(data:Annotated[Create_Task, Depends()]):
    return None