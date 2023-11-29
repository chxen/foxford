from pydantic import BaseModel, EmailStr, Field
from tortoise.models import Model
from tortoise import fields
from enum import Enum


class TicketStatusEnum(str, Enum):
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    CLOSED = 'closed'


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=100)
    email = fields.CharField(max_length=100, unique=True)
    password = fields.CharField(max_length=100)
    role = fields.ManyToManyField("models.Role", related_name="user", through="user_role")

    def __str__(self):
        return f"User: {self.username}"

    class Meta:
        table = "users"


class Role(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"Role: {self.title}"

    class Meta:
        table = "roles"


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: list


class RoleCreate(BaseModel):
    title: list


class Client(Model):
    telegram_id = fields.IntField(unique=True)
    name = fields.CharField(max_length=255)

    def __str__(self):
        return self.name


class Employee(Model):
    username = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)

    def __str__(self):
        return self.username


class Ticket(Model):
    STATUS_OPEN = 'open'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_CLOSED = 'closed'

    client = fields.ForeignKeyField('models.Client', related_name='tickets')
    employee = fields.ForeignKeyField('models.Employee', related_name='tickets', null=True)
    status = fields.CharEnumField(enum_type=TicketStatusEnum, choices=TicketStatusEnum)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return f'Ticket #{self.id} - Status: {self.status}'


class TicketMessage(Model):
    ticket = fields.ForeignKeyField('models.Ticket', related_name='messages')
    sender = fields.CharField(max_length=255)
    message = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f'Message from {self.sender} - {self.message}'


class TicketResponse(Model):
    id: int
    client_id: int
    employee_id: int
    status: str
    created_at: fields.DatetimeField(auto_now_add=True)
    updated_at: fields.DatetimeField(auto_now_add=True)

class TicketMessageCreate(Model):
    sender: str
    message: str

class TicketCreate(Model):
    client_id: int
    status: str

class TicketUpdate(Model):
    status: str