import time
import json
import requests
import os
import hashlib
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from lg import logger as l
import asyncio
from threading import Thread

FEEDS_FILE = "feeds.json"
SENT_FILE = "sent_items.json"
interval = 5
magnet_store = {}  # In-memory store for short hash -> magnet link

# Ensure JSON files exist
if not os.path.exists(FEEDS_FILE):
    with open(FEEDS_FILE, "w") as f:
        json.dump({"feeds": [], "enabled": True}, f)

if not os.path.exists(SENT_FILE):
    with open(SENT_FILE, "w") as f:
        json.dump([], f)

def load_feeds():
    with open(FEEDS_FILE) as f:
        return json.load(f)

def save_feeds(data):
    with open(FEEDS_FILE, "w") as f:
        json.dump(data, f)

def load_sent():
    with open(SENT_FILE) as f:
        return json.load(f)

def save_sent(sent):
    with open(SENT_FILE, "w") as f:
        json.dump(sent, f)

def parse_rss(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.content, "xml")
        items = soup.find_all("item")
        return items
    except Exception as e:
        l.info(f"[RSS ERROR] {url} -> {e}")
        return []

def build_message(item):
    title = item.find("title").text.strip()
    magnet = item.find("link").text.strip()
    size_tag = item.find("contentLength")
    size = int(size_tag.text.strip()) if size_tag else 0
    size_mb = f"{size / (1024 * 1024):.2f} MB" if size else "N/A"
    pub = item.find("pubDate").text.strip()

    # Shorten magnet using hash
    key = hashlib.md5(magnet.encode()).hexdigest()[:10]
    magnet_store[key] = magnet

    text = f"**🧲 New Torrent Found!**\n\n" \
           f"**📦 Title:** `{title}`\n" \
           f"**📅 Published:** {pub}\n" \
           f"**📁 Size:** {size_mb}" \
           f"\n**Link:** `{magnet}`"

    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Magnet", callback_data=f"mgt_{key}")]
    ])
    return text, button, key

async def batch_sender(bot: Client, messages: list):
    batch = messages[:25]
    for text, button in batch:
        try:
            await bot.send_message(Config.OWNER, text, reply_markup=button)
        except Exception as e:
            l.info(f"[SEND ERROR] {e}")
        await asyncio.sleep(1)  # Slight delay to avoid flood
    await asyncio.sleep(30)  # Wait before next batch

async def send_new_items(bot: Client):
    l.info("starting listen to feeds...!")
    while True:
        feeds = load_feeds()
        if not feeds.get("enabled", True):
            await asyncio.sleep(60)
            continue

        sent_ids = load_sent()
        to_send = []

        for feed_url in feeds["feeds"]:
            items = parse_rss(feed_url)
            l.info("doing...!")
            for item in items:
                guid = item.find("guid").text.strip()
                if guid in sent_ids:
                    continue

                msg, btn, key = build_message(item)
                to_send.append((msg, btn))
                sent_ids.append(guid)

        if to_send:
            await batch_sender(bot, to_send)
            save_sent(sent_ids)

        await asyncio.sleep(interval)

def start_feed_watcher(bot: Client):
    def run_asyncio():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_new_items(bot))

    thread = Thread(target=run_asyncio)
    thread.daemon = True
    thread.start()

# ---------------- Commands ---------------- #

@Client.on_message(filters.command("addfeed") & filters.user(Config.owner_id))
def add_feed(_, message):
    try:
        url = message.text.split(" ", 1)[1]
    except IndexError:
        return message.reply("❌ Usage: `/addfeed <url>`", quote=True)

    feeds = load_feeds()
    if url in feeds["feeds"]:
        return message.reply("⚠️ Feed already exists.")
    feeds["feeds"].append(url)
    save_feeds(feeds)
    message.reply("✅ Feed added!")

@Client.on_message(filters.command("listfeeds") & filters.user(Config.owner_id))
def list_feeds(_, message):
    feeds = load_feeds()
    text = "**📡 Current RSS Feeds:**\n\n"
    if not feeds["feeds"]:
        text += "No feeds added yet."
    else:
        for i, f in enumerate(feeds["feeds"], 1):
            text += f"{i}. {f}\n"
    text += f"\n🔘 Listener is {'enabled' if feeds.get('enabled', True) else 'disabled'}"
    message.reply(text)

@Client.on_message(filters.command("removefeed") & filters.user(Config.owner_id))
def remove_feed(_, message):
    try:
        index = int(message.text.split(" ", 1)[1]) - 1
    except:
        return message.reply("❌ Usage: `/removefeed <index>`", quote=True)

    feeds = load_feeds()
    if 0 <= index < len(feeds["feeds"]):
        removed = feeds["feeds"].pop(index)
        save_feeds(feeds)
        message.reply(f"✅ Removed feed:\n`{removed}`")
    else:
        message.reply("❌ Invalid index.")

@Client.on_message(filters.command("togglefeeds") & filters.user(Config.owner_id))
def toggle_feed_status(_, message):
    feeds = load_feeds()
    feeds["enabled"] = not feeds.get("enabled", True)
    save_feeds(feeds)
    status = "enabled" if feeds["enabled"] else "disabled"
    message.reply(f"🔁 Feed listener is now **{status}**")

@Client.on_message(filters.command("sfeed") & filters.user(Config.owner_id))
def restart(_f, message):
    start_feed_watcher(_f)

@Client.on_callback_query(filters.regex(r"^mgt_"))
async def magnet_button(client, callback_query):
    key = callback_query.data.replace("mgt_", "", 1)
    magnet = magnet_store.get(key)

    if magnet:
        #callback_query.answer("Magnet copied!", show_alert=True)
        await callback_query.message.reply_text(f"🔗 Magnet link:\n`{magnet}`")
    else:
        await callback_query.message.reply_text("Magnet not found or expired.")
