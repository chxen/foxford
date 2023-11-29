import requests
from dotenv import dotenv_values

config = dotenv_values("../.env")

r = requests.get(f'https://api.telegram.org/bot{config["TOKEN"]}/setWebhook?url=https://{config["WHOOK"]}/')
print(r.json())
