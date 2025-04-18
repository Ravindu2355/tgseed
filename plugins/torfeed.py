import asyncio
import json
import feedparser
import time
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

FEEDS_FILE = "feeds.json"
SEEN_FILE = "seen.json"
CHECK_INTERVAL = 60  # seconds
CHAT_ID = "1387186514"  # replace or fetch dynamically if needed

def load_json(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

feeds = load_json(FEEDS_FILE, [])
seen = load_json(SEEN_FILE, [])

async def check_feeds_task(app: Client):
    while True:
        for i, feed in enumerate(feeds):
            if not feed.get("enabled", True):
                continue
            try:
                d = feedparser.parse(feed["url"])
                for entry in d.entries:
                    guid = entry.get("guid") or entry.get("id") or entry.get("link")
                    if guid in seen:
                        continue
                    seen.append(guid)
                    save_json(SEEN_FILE, seen)
                    await send_torrent(app, entry)
            except Exception as e:
                print(f"Error checking feed {feed['url']}: {e}")
        await asyncio.sleep(CHECK_INTERVAL)

def format_size(size_bytes):
    size_bytes = int(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

async def send_torrent(app, entry):
    title = entry.title.strip()
    magnet = entry.link
    uploader = entry.get("dc_creator", "Unknown")
    pub_date = entry.get("published", "")
    comments = entry.get("comments", "")
    info_hash = entry.get("torrent_infohash", "")
    size = "Unknown"
    try:
        size = format_size(entry.torrent_contentlength)
    except:
        pass

    text = (
        f"🎬 **New Torrent Found!**\n\n"
        f"📥 **Title**: `{title}`\n"
        f"🗂️ **Size**: `{size}`\n"
        f"🕵️‍♂️ **Uploader**: `{uploader}`\n"
        f"📅 **Published**: `{pub_date}`\n"
        f"\n🔗 [View on TPB]({comments})"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🧲 Magnet Link", callback_data=f"mgt_{magnet}")]
    ])

    try:
        await app.send_message(
            CHAT_ID,
            text,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
    except Exception as e:
        print("Send error:", e)

# --- Command Handlers ---

@Client.on_message(filters.command("addfeed"))
async def add_feed(_, message):
    if len(message.command) < 2:
        return await message.reply("Usage: /addfeed [url]")
    url = message.command[1]
    feeds.append({"url": url, "enabled": True})
    save_json(FEEDS_FILE, feeds)
    await message.reply("✅ Feed added and enabled.")

@Client.on_message(filters.command("listfeeds"))
async def list_feeds(_, message):
    if not feeds:
        return await message.reply("No feeds added.")
    reply = ""
    for i, feed in enumerate(feeds):
        status = "✅ ON" if feed.get("enabled", True) else "❌ OFF"
        reply += f"{i + 1}. {status} - `{feed['url']}`\n"
    await message.reply(reply)

@Client.on_message(filters.command("togglefeed"))
async def toggle_feed(_, message):
    if len(message.command) < 2 or not message.command[1].isdigit():
        return await message.reply("Usage: /togglefeed [index]")
    idx = int(message.command[1]) - 1
    if 0 <= idx < len(feeds):
        feeds[idx]["enabled"] = not feeds[idx].get("enabled", True)
        save_json(FEEDS_FILE, feeds)
        await message.reply(f"Toggled feed {idx + 1} to {'ON' if feeds[idx]['enabled'] else 'OFF'}.")
    else:
        await message.reply("Invalid feed index.")

@Client.on_message(filters.command("removefeed"))
async def remove_feed(_, message):
    if len(message.command) < 2 or not message.command[1].isdigit():
        return await message.reply("Usage: /removefeed [index]")
    idx = int(message.command[1]) - 1
    if 0 <= idx < len(feeds):
        removed = feeds.pop(idx)
        save_json(FEEDS_FILE, feeds)
        await message.reply(f"❌ Removed feed: {removed['url']}")
    else:
        await message.reply("Invalid feed index.")

@Client.on_callback_query(filters.regex(r"mgt_"))
async def handle_magnet_callback(client, callback_query):
    magnet = callback_query.data[4:]
    await callback_query.answer()
    try:
        await callback_query.message.reply(f"🧲 **Magnet Link**:\n`{magnet}`")
    except Exception as e:
        print("Callback reply error:", e)

# --- Hook to Start Background Feed Checker ---
def start_feed_watcher(app: Client):
    app.loop.create_task(check_feeds_task(app))
