from pyrogram import Client, filters, types
from plugins.func.simples import mention_user


@Client.on_message(filters.command("start"))
async def _ms(client, message:types.Message):
    await message.reply(
      f"**💫Rx Seedr Torrent Uper💫**\n\n**Hi🫡...{mention_user(message)}😍\n\nGive me a Torrent Link or magnet link for upload**"
    )

@Client.on_message(filters.command("help"))
async def _mh(client, msg:types.Message):
  await msg.reply(
    f"**💫Rx Seedr Torrent Uper💫**\n\n💢This is a bot who made for download/seed torrents to directly to telegram...\n\n💘Please remember that this is only for its authers🫡...\n\nIf you got eny Unexpected dissaponment,\nSorry about that🥲..."
  )
