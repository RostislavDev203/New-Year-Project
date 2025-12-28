"""
Схемы для авторизации
"""
#импортируем библиотеки
from pydantic import BaseModel, EmailStr, Field

class Base(BaseModel):
    pass

class Create_Account(Base):
    name:str = Field(..., min_length=1, max_length=100, description="Имя пользователя")
    email:EmailStr = Field(..., description="Email адрес")
    password:str = Field(..., min_length=6, description="Пароль (минимум 6 символов)")

class LogIn(Base):
    email:EmailStr = Field(..., description="Email адрес")
    password:str = Field(..., description="Пароль")

class Verify_Email(Base):
    email:EmailStr = Field(..., description="Email адрес")
    code:str = Field(..., min_length=6, max_length=6, description="6-значный код верификации")

class Resend_Code(Base):
    email:EmailStr = Field(..., description="Email адрес")

class DeleteAccount(Base):
    token:str
    password:str = Field(..., description="Пароль")