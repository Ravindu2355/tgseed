from pyrogram import Client, filters, types
from plugins.func.simples import mention_user
from plugins.autherHandle import is_auth
import re

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
    
    return None

# Message handler
@Client.on_message(filters.text & ~filters.edited)
async def detect_torrent_or_magnet(client, message):
    text = message.text.strip()
    if not is_auth(message.chat.id):
      await message.delete()
      return
    link_type = identify_link_type(text)
    if link_type == "magnet":
        
    elif link_type == "torrent":
        
    else:
        await message.reply("No torrent or magnet link detected.")
