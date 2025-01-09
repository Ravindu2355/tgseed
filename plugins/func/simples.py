import urllib.parse


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

