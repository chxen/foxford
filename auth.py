import jwt
from passlib.context import CryptContext
from dotenv import dotenv_values

'''Aутентификация  через jwt токен'''

config_credentials = dotenv_values("../.env")
password_new = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Хэширует пароль
def hashPassword(password):
    return password_new.hash(password)

# Функция проверяет совпадают ли пароли
def verify_password(password, hashPassword):
    return password_new.verify(password, hashPassword)

# Функция, используемая для шифрования строки JWT
def encodeJWT(data: dict):
    return jwt.encode(data, config_credentials["SECRET"], algorithm=config_credentials["JWT_ALGORITM"])

# Функция, используемая для расшифрования строки JWT
def decodeJWT(token: str):
    return jwt.decode(token, config_credentials["SECRET"], algorithms=config_credentials["JWT_ALGORITM"])
