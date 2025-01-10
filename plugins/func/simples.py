import urllib.parse
from moviepy.editor import VideoFileClip
import os
import shutil
from lg import logger as l

def url_decode(encoded_string):
    return urllib.parse.unquote(encoded_string)

def url_encode(string):
    return urllib.parse.quote(string)

def mention_user(message:Message):
    user = message.from_user
    user_name = user.first_name
    user_id = user.id
    mention = f"[{user_name}](tg://user?id={user_id})"
    return mention

def generate_thumbnail(video_path, thumbnail_path):
    try:
        video = VideoFileClip(video_path)
        video.save_frame(thumbnail_path, t=1.0)  # Save thumbnail at 1 second
        return thumbnail_path
    except Exception as e:
        l.info(f"Error generating thumbnail: {e}")
        return None

def humanr_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']:
        if size < 1024:
            return f"{size:.{decimal_places}f} {unit}"
        size /= 1024


def clean_dir(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory,exist_ok=True)
            l.info(f"Directory '{directory}' does not exist.But created...")
            return True

        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)

            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)  # Remove files and symlinks
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Remove directories recursively

        return True

    except Exception as e:
        l.info(f"Error cleaning directory '{directory}': {e}")
        return False
