from fastapi import FastAPI, Depends, Request, HTTPException
from tortoise.contrib.fastapi import register_tortoise
from app import bot
from models import *
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth import *
from schemas import Answer
from contextlib import asynccontextmanager
from bot import dp, config
from aiogram import Dispatcher, Bot, types
from typing import List


app = FastAPI()
auth = OAuth2PasswordBearer(tokenUrl="authorization")

token = config["TOKEN"]
WEBHOOK_PATH = f"/bot/{token}"
WEBHOOK_URL = "https://f18a-77-37-157-209.ngrok-free.app" + WEBHOOK_PATH

TORTOISE_ORM = {
    "connections": {"default": "postgres://postgres:0000@localhost:5432/loginuser"},
    "apps": {
        "models": {
            "models": ["models"],
            "default_connection": "default",
        },
    }
}

register_tortoise(
    app,
    config=TORTOISE_ORM,
    add_exception_handlers=True,
    generate_schemas=True
)


# Создание роли пользователя
@app.post('/create_role', tags=["role"])
async def create_role(roles: RoleCreate):
    lst_roles = []
    for role in roles.title:
        lst_role = await Role.create(title=role)
        lst_roles.append(lst_role)
    return lst_roles


# Регистрация пользователя
@app.post('/registration', tags=["user"])
async def registration(data: UserCreate):
    new_user = await User.create(
        username=data.username,
        email=data.email,
        password=hashPassword(data.password))
    for one_role in data.role:
        role = await Role.get(title=one_role)
        await new_user.role.add(role)
    return new_user


# Авторизация через jwt
@app.post('/authorization', tags=["user"])
async def authorization(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = await User.get(username=form_data.username)
    if verify_password(form_data.password, db_user.password):
        token = encodeJWT(data={"sub": db_user.username})
        return {'access_token':token}
    else:
        return {"Error": f"This user is not registered or wrong email/password."}


# Проверка токена
@app.get('/check_auth', tags=["user"])
async def check_auth(token: str = Depends(auth)):
    return {"token": token}


# telegram bot
@asynccontextmanager
async def lifespan(app: FastAPI):
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL
        )

@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await dp.process_update(telegram_update)


@app.get("/tickets/", response_model=List[TicketResponse])
async def get_tickets(status: str = None, employee_id: int = None, sort_by: str = "created_at"):
    filters = {}
    if status:
        filters["status"] = status
    if employee_id:
        filters["employee_id"] = employee_id

    tickets = await Ticket.filter(**filters).order_by(sort_by).all()
    return tickets


@app.put("/tickets/{ticket_id}/", response_model=Ticket)
async def update_ticket(ticket_id: int, ticket_update: TicketUpdate):
    ticket = await Ticket.get_or_none(id=ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket.status = ticket_update.status
    await ticket.save()
    
    return ticket


@app.post("/tickets/{ticket_id}/messages/", response_model=TicketMessage)
async def create_ticket_message(ticket_id: int, message_create: TicketMessageCreate):
    ticket = await Ticket.get_or_none(id=ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    message = await TicketMessage.create(
        ticket=ticket,
        sender=message_create.sender,
        message=message_create.message
    )

    return message


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)