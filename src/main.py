"""
Главный файл, инициализирующий всё
"""
#импортируем библиотеки
from fastapi import FastAPI
from db import init_db

#создаем приложение
app = FastAPI(
    title="New Year assistant API",
    description="Your New Year assistant with which you can create, update, delete tasks",
    version="1.0.0"
    )

@app.get('/')
async def root():
    """
    Корневой эндпоинт

    Returns: dict приветствие
    """
    return {
        'message': 'Welcome to your New Year assistant API!',
        'docs': '/docs',
        'version': '1.0.0'
    }

@app.get("/ping")
async def pong():
    """
    Эндпоинт для проверки статуса сервера

    Returns: dict
    """
    return {'ping!': 'pong!'}

@app.on_event('startup')
async def startup():
    """
    Эндпоинт, для инициализации сервисов 
    """
    init_db()