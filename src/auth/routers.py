"""
Роутеры для авторизации
"""
#импортируем библиотеки
from fastapi import APIRouter, WebSocket, Depends
from typing import Annotated
from .schemas import Create_Account, LogIn, Verify_Email, Resend_Code, DeleteAccount
from .utils import create_account, authentification, verify_email, resend_verification_code, deleting

#Создаем роутер auth
auth = APIRouter(prefix='/auth', tags=["Authorisation"])

@auth.post('/sign_in')
async def sign_in(data:Annotated[Create_Account, Depends()]):
    return await create_account(data.name, data.email, data.password)

@auth.post('/log_in')
async def log_in(data:Annotated[LogIn, Depends()]):
    return await authentification(data.email, data.password)

@auth.post('/verify_email')
async def verify_email(data:Annotated[Verify_Email, Depends()]):
    return await verify_email(data.email, data.code)

@auth.put('/resend_code')
async def resend_code(data:Annotated[Resend_Code, Depends()]):
    await resend_verification_code(data.email)

@auth.delete('/delete_account')
async def delete_account(data:Annotated[DeleteAccount, Depends()]):
    return await deleting(data.token, data.password)