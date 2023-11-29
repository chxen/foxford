from pydantic import BaseModel, Field


class FromF(BaseModel):
    chat_id: int = Field(alias='id')
    is_bot: bool
    first_name: str
    username: str
    language_code: str


class Chat(BaseModel):
    chat_id: int = Field(alias='id')
    first_name: str
    username: str
    type: str


class Message(BaseModel):
    message_id: int
    from_f: FromF = Field(alias='from')
    chat: Chat
    date: int
    text: str


class Answer(BaseModel):
    update_id: int
    message: Message
