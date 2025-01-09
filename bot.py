import os
import time
from pyrogram import Client, filters ,types
from config import Config

API_ID = Config.apiid
API_HASH = Config.apihash
BOT_TOKEN = Config.tk

# Initialize the Pyrogram Client
plugins = dict(root="plugins")
bot = Client(name="RVX_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH, plugins=plugins)


# Run the bot
if __name__ == '__main__':
    bot.run()
