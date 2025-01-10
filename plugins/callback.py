from pyrogram import Client
from bot import seedr

@Client.on_callback_query()
async def callback_query_handler(client, callback_query):
    if callback_query.data.startswith("del_"):
        _, type, file_id = callback_query.data.split("_", 2)
        if seedr.delete([{"type":type,"id":file_id}]):
          await callback_query.message.edit_text(f"Deleted {type} with ID: {file_id}")
        else:
          await callback_query.message.edit_text("Sorry system err!...")
