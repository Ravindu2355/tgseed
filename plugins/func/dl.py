import os
import time
import aiohttp
import asyncio
from pyrogram.errors import FloodWait
from config import Config
from plugins.func.simples import humanr_size


def calculate_eta(total_size, downloaded_size, speed):
    if speed > 0:
        return int((total_size - downloaded_size) / speed)
    return -1  # Cannot calculate ETA if speed is zero

async def download_file(client, msg, url, file_name, save_dir=Config.dl_dir, update_interval=10):
    # Ensure the directory exists
    os.makedirs(save_dir, exist_ok=True)

    # Extract file name from URL
    save_path = os.path.join(save_dir, file_name)

    # Progress variables
    start_time = time.time()
    last_update_time = time.time()
    last_progress_text = ""

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            # Check if the response is OK
            if response.status != 200:
                await msg.edit_text("Failed to download the file...!")
                return

            total_size = int(response.headers.get("Content-Length", 0))
            downloaded_size = 0

            # Open file for writing
            with open(save_path, "wb") as f:
                async for chunk in response.content.iter_chunked(1024 * 1024):  # 1 MB chunks
                    f.write(chunk)
                    downloaded_size += len(chunk)

                    # Calculate elapsed time and speed
                    elapsed_time = time.time() - start_time
                    speed = downloaded_size / elapsed_time if elapsed_time > 0 else 0
                    eta = calculate_eta(total_size, downloaded_size, speed)

                    # Format progress text
                    progress_text = (
                        f"**Downloading...**\n\n"
                        f"**File Name:** `{file_name}`\n"
                        f"**Downloaded:** {downloaded_size / total_size * 100:.2f}%\n"
                        f"**Size:** {humanr_size(downloaded_size)} / {humanr_size(total_size)}\n"
                        f"**Speed:** {humanr_size(speed)}/s\n"
                        f"**ETA:** {eta}s\n"
                    )

                    # Update progress every `update_interval` seconds
                    if time.time() - last_update_time >= update_interval and progress_text != last_progress_text:
                        try:
                            await msg.edit_text(progress_text)
                            last_update_time = time.time()
                            last_progress_text = progress_text
                        except FloodWait as e:
                            await asyncio.sleep(e.value)

    # Notify completion
    await msg.edit_text(f"**Download Complete!**\n\n**File saved to:** `{save_path}`")
    return save_path
  
