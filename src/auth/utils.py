"""
Утилиты для авторизации
"""
#импортируем библиотеки
import jwt
import bcrypt 
import datetime
import smtplib
import secrets
import uuid
from db import new_session
from sqlalchemy import select, delete
from fastapi import HTTPException
from typing import Optional
from auth.models import User
from email.mime.text import MIMEText
from celery_app import celery_app
import os
from dotenv import load_dotenv

#загружаем переменные окружения
load_dotenv()

salt = bcrypt.gensalt()

JWT_ALGHORITM = os.getenv('JWT_ALGHORITM')

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

SMTP_HOST = os.getenv('SMTP_HOST_ENV')     # или smtp.yandex.ru, smtp.mail.ru
SMTP_PORT = int(os.getenv('SMTP_PORT_ENV'))  # для TLS
SMTP_USER = os.getenv('SMTP_USER_ENV')      # твоя почта
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD_ENV')

def send_email_sync(to_email: str, subject: str, message: str):
    """
    Синхронная функция отправки email
    
    Args:
        to_email: Email получателя
        subject: Тема письма
        message: Текст письма
    """
    
    msg = MIMEText(message, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_email

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Email send failed: {e}")
        raise

@celery_app.task(name='send_email', bind=True, max_retries=3)
def send_email_task(self, to_email: str, subject: str, message: str):
        """
        Celery задача для отправки email
        """
        try:
            send_email_sync(to_email, subject, message)
        except Exception as e:
            print(f"Email send failed: {e}")
            raise self.retry(exc=e)

async def create_access_token(login:str):
    """
    Создает JWT-токен

    Args: Какой либо логин в формате str

    Returns: JWT-токен
    """
    try:
      payload = {
        'login': login,
        'exp': ((datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)).timestamp())
        }
      # JWT требует строку или bytes, проверяем тип
      key = JWT_SECRET_KEY if isinstance(JWT_SECRET_KEY, (str, bytes)) else JWT_SECRET_KEY.decode('utf-8') if isinstance(JWT_SECRET_KEY, bytes) else str(JWT_SECRET_KEY)
      token = jwt.encode(payload=payload, key=key, algorithm=JWT_ALGHORITM)
      return {'token': token}
    except:
      raise HTTPException(status_code=500)

async def decode(token:str)->dict['login':str, 'exp':float]:
   """
    Получает значения JWT-токена

    Args: JWT-токен в формате str

    Returns: dict['login': str, 'exp': float]

    Exceptions: Invalid token error
    """
   key = JWT_SECRET_KEY if isinstance(JWT_SECRET_KEY, (str, bytes)) else JWT_SECRET_KEY.decode('utf-8') if isinstance(JWT_SECRET_KEY, bytes) else str(JWT_SECRET_KEY)
   decoded_token = jwt.decode(token=token, key=key, algorithms=[JWT_ALGHORITM])
   times = decoded_token['exp']
   time = datetime.datetime.fromtimestamp(times, tz=datetime.timezone.utc)
   if time <= datetime.datetime.now(datetime.timezone.utc):
     raise HTTPException(status_code=401, detail="Invalid JWT")
   return decoded_token

async def get_user_by_email(email: str) -> Optional[User]:
    """
    Получает пользователя по email
    
    Args:
        email: Email пользователя
    
    Returns:
        User | None: Пользователь или None, если не найден
    """
    async with new_session() as session:
        result = await session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

async def generate_verification_code() -> str:
    """
    Генерирует 6-значный код верификации
    
    Returns:
        str: Код верификации
    """
    return ''.join([str(secrets.randbelow(10)) for _ in range(6)])

async def send_verification_email(email: str, code: str):
    """
    Отправляет код верификации на email
    
    Args:
        email: Email пользователя
        code: Код верификации
    """
    subject = "Код верификации FastTube"
    message = f"Ваш код верификации: {code}\n\nВведите этот код для подтверждения email."
    send_email_task.delay(email, subject, message)

async def create_account(name:str, email:str, password:str):
  async with new_session() as session:
     # Проверяем существование пользователя в той же сессии
     result = await session.execute(select(User).where(User.email == email))
     existing_user = result.scalar_one_or_none()
     if existing_user:
      raise HTTPException(status_code=401, detail="This email is taken!")
     
     # Генерируем соль для каждого пароля
     salt = bcrypt.gensalt()
     hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
     
     # Генерируем код верификации
     verification_code = await generate_verification_code()
     
     new_user = User(
         id=uuid.uuid4(), 
         name=name, 
         email=email, 
         password=hashed_password,
         is_verified=False,
         verification_code=verification_code
     )
     session.add(new_user)
     await session.commit()
     await session.refresh(new_user)
     
     # Отправляем код верификации
     await send_verification_email(email, verification_code)
     
     return new_user

async def verify_email(email: str, code: str) -> bool:
    """
    Проверяет код верификации и подтверждает email
    
    Args:
        email: Email пользователя
        code: Код верификации
    
    Returns:
        bool: True если код верный, False иначе
    
    Raises:
        INVALID_VERIF_CODE: Если код неверный
    """
    async with new_session() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=401, detail='Invalid login or password!')
        
        if user.verification_code != code:
            raise HTTPException(status_code=401, detail='Invalid verification code')
        
        user.is_verified = True
        user.verification_code = None
        await session.commit()
        return True

async def authentification(email:str, password:str):
  user = await get_user_by_email(email)
  if not user:
    raise HTTPException(status_code=401, detail='Invalid login or password!')
  
  # Проверяем, верифицирован ли email
  if not user.is_verified:
    raise HTTPException(status_code=403, detail="Email not verified! Please verify your email first.")
  
  if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
    token_data = await create_access_token(email)
    return token_data
  else:
    raise HTTPException(status_code=401, detail='Invalid login or password!')
  
async def resend_verification_code(email: str):
    """
    Повторно отправляет код верификации
    
    Args:
        email: Email пользователя
    """
    async with new_session() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=401, detail='Invalid login or password!')
        
        if user.is_verified:
            raise HTTPException(status_code=400, detail="Email already verified!")
        
        # Генерируем новый код
        verification_code = await generate_verification_code()
        user.verification_code = verification_code
        await session.commit()
        
        # Отправляем код
        await send_verification_email(email, verification_code)

async def deleting(token:str, password:str):
  async with new_session() as session:
   decoded = await decode(token=token)
   result = await session.execute(select(User).where(User.email == decoded['login']))
   user = result.scalar_one_or_none()
   
   if not user:
     raise HTTPException(status_code=401, detail='Invalid login or password!')

   if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
     await session.execute(delete(User).where(User.id == user.id))
     await session.commit()
     return {'message': 'Successful deleting of account!'}
   else:
     raise HTTPException(status_code=401, detail='Invalid password!')