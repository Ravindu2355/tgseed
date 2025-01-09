import urllib.parse
from moviepy.editor import VideoFileClip

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
        print(f"Error generating thumbnail: {e}")
        return None
