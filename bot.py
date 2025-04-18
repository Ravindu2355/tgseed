import os
import time ,json
from pyrogram import Client, filters ,types
from config import Config
from tor.seed import SeedrClient
from lg import logger as l
from plugins.func.simples import clean_dir

API_ID = Config.apiid
API_HASH = Config.apihash
BOT_TOKEN = Config.tk

clean_dir(Config.dl_dir)
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
    #l.info(f"account settings: {json.dumps(seedr.get_account_settings())}")
else:
    l.info("Sorry cant log into seedr account")
# Run the bot
#if __name__ == '__main__':
    #l.info("bot client starting...")
    #bot.run()
# Run the bot
if __name__ == '__main__':
    l.info("feeding..!")
    from plugins.torfeed import start_feed_watcher
    start_feed_watcher(bot)
    l.info("bot client starting...")
    bot.run()
