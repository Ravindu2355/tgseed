import os
import time
from pyrogram import Client, filters ,types
from config import Config
from tor.seed import SeedrClient
from lg import logger as l

API_ID = Config.apiid
API_HASH = Config.apihash
BOT_TOKEN = Config.tk

# Initialize the Pyrogram Client
plugins = dict(root="plugins")
bot = Client(name="RVX_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH, plugins=plugins)

#seedr client
seedr = SeedrClient(
    Config.seedr_email,
    Config.seedr_pw
)
if seedr.login():
    l.info("Successfully loged into seedr account!...")
else:
    l.info("Sorry cant log into seedr account")
# Run the bot
if __name__ == '__main__':
    l.info("bot client starting...")
    bot.run()
