import os, time
from moviepy.editor import VideoFileClip
from pyrogram.errors import FloodWait
from plugins.func.simples import humanr_size, clean_dir, generate_thumbnail

# Utility function to update progress
async def update_progress(msg, current, total, file_name, start_time, last_update_time, last_progress_text, update_interval=10):
    elapsed_time = time.time() - start_time
    speed = current / elapsed_time if elapsed_time > 0 else 0
    eta = calculate_eta(total, current, speed)

    # Format progress text
    progress_text = (
        f"**Uploading...**\n\n"
        f"**File Name:** `{file_name}`\n"
        f"**Uploaded:** {current / total * 100:.2f}%\n"
        f"**Size:** {humanr_size(current)} / {humanr_size(total)}\n"
        f"**Speed:** {humanr_size(speed)}/s\n"
        f"**ETA:** {eta}s\n"
    )

    # Send progress updates every `update_interval` seconds
    if time.time() - last_update_time >= update_interval and progress_text != last_progress_text:
        try:
            await msg.edit_text(progress_text)
            return time.time(), progress_text
        except FloodWait as e:
            await asyncio.sleep(e.value)  # Handle flood wait

    return last_update_time, last_progress_text

async def upload_document(client, msg, file_path):
    file_name = file_path.split("/")[-1]
    total_size = os.path.getsize(file_path)
    start_time = time.time()
    last_update_time = time.time()
    last_progress_text = ""

    async def progress(current, total):
        nonlocal last_update_time, last_progress_text
        last_update_time, last_progress_text = await update_progress(
            msg, current, total, file_name, start_time, last_update_time, last_progress_text
        )

    # Upload the document
    await client.send_document(
        chat_id=msg.chat.id,
        document=file_path,
        progress=progress
    )

    # Notify completion
    await msg.edit_text(f"**Upload Complete!**\n\n**File:** `{file_name}`")

async def upload_video(client, msg, file_path, thumb_path=None):
    file_name = file_path.split("/")[-1]
    total_size = os.path.getsize(file_path)
    start_time = time.time()
    last_update_time = time.time()
    last_progress_text = ""
    #genarate thumbnail
    if not thumb_path:
      await msg.edit_text("**Genarating Thumbnail...!**")
      thumb_path = f"{file_path}.jpg"
      generate_thumbnail(video_path, thumbnail_path)
    # Extract video duration using MoviePy
    try:
        video_clip = VideoFileClip(file_path)
        duration = int(video_clip.duration)  # Duration in seconds
        video_clip.close()
    except Exception as e:
        await msg.edit_text(f"Failed to extract video duration: {e}")
        return
    await msg.edit_text("**Starting Upload..!**")
    async def progress(current, total):
        nonlocal last_update_time, last_progress_text
        last_update_time, last_progress_text = await update_progress(
            msg, current, total, file_name, start_time, last_update_time, last_progress_text
        )

    # Upload the video
    await client.send_video(
        chat_id=msg.chat.id,
        video=file_path,
        duration=duration,
        thumb=thumb_path,
        progress=progress
    )

    # Notify completion
    await msg.edit_text(f"**Upload Complete!**\n\n**Video:** `{file_name}`")
