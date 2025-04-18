from pyrogram import Client, filters, types
from plugins.func.simples import mention_user
from plugins.autherHandle import is_auth
import re, json
from bot import seedr
from plugins.func.seed_mag import seed_file

# Function to identify and classify the type of link
def identify_link_type(text):
    # Magnet link pattern
    magnet_pattern = r"magnet:\?xt=urn:[a-z0-9]+:[a-zA-Z0-9]{32,40}"
    # Torrent file pattern
    torrent_pattern = r"https?://\S+\.torrent"
    
    # Check if it's a magnet link
    if re.search(magnet_pattern, text, re.IGNORECASE):
        return "magnet"
    # Check if it's a torrent link
    elif re.search(torrent_pattern, text, re.IGNORECASE):
        return "torrent"
    elif "http" in text and "/torrent/" in text:
        return "torrent"
    return None

# Message handler
#@Client.on_message(filters.text)
MAGNET_REGEX = r"^magnet:\?xt=urn:btih:[A-Za-z0-9]{40,50}"
TORRENT_URL_REGEX = r"(https?://[^\s]+\.torrent)"

@Client.on_message(filters.text & (filters.regex(MAGNET_REGEX) | filters.regex(TORRENT_URL_REGEX)))
async def detect_torrent_or_magnet(client, message, rtext=""):
    text = message.text.strip()
    if rtext:
        text = rtext
    if not is_auth(message.chat.id):
      await message.delete()
      return
    link_type = identify_link_type(text)
    if not seedr.check_session():
        seedr.login()
    if link_type == "magnet":
        msg = await message.reply("Magnet Link found Proccesing!...")
        await seed_file(text, client, msg)
    elif link_type == "torrent":
        msg = await message.reply("Torrent Link found Proccesing!...")
        magt = seedr.fetch_torrent(text)
        if "torrents" in magt:
            await seed_file(magt["torrents"][0]["magnet"], client, msg)
        else:
            await msg.edit_text(f"Sorry cannot extract Magnet links from it!...{json.dumps(magt)}")
    else:
        await message.reply("No torrent or magnet link detected.")
