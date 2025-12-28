"""
Файл celery
"""
#импортируем библиотеки 
from celery import Celery
import os
from dotenv import load_dotenv

#загружаем переменные окружения
load_dotenv

#создаем приложение celery
celery_app = Celery('New Year assistant', broker=os.getenv('CELERY_URL'), backend=os.getenv('CELERY_URL'))