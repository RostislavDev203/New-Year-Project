"""
Главный файл управления БД
"""
#импортируем библиотеки
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv

#загружаем переменные окружения
load_dotenv()

class Model(DeclarativeBase):
    pass

#загружаем url
url=os.getenv('URL')

#создаем движок
engine = create_async_engine(url=url)

#создаем сессию
new_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    """
    Инициализирует БД
    """
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)
