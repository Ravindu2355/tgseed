import asyncio, time, json
from bot import seedr
from plugins.func.simples import humanr_size, clean_dir
from plugins.func.dl import download_file
from plugins.func.tgup import upload_video, upload_document
from config import Config 
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def seed_file(maglink, client, msg):
    if not seedr.check_session():
        await msg.edit_text("Sorry, Seedr session was invalid!...")
        return
    
    js = seedr.add_magnet(maglink)
    if js and js["success"] == True:
        folder_title = js["title"]
        folder_id = 0
        ls_t = time.time()
        ls_msg = ''
        while True:
            jso = seedr.get_folder_items()
            folders = jso["folders"]
            fol = next((fol for fol in folders if fol["path"] == folder_title), None)
            #await msg.reply(f"folders: {json.dumps(folders)} \n\nfolder: {json.dumps(fol)}\n\nfolder_id: {folder_title}")
            
            if fol:# If folder is found, break the loop
                #await msg.reply(f"Found: {json.dumps(fol)}")
                folder_id = fol["id"]
                break

            if jso['torrents']:
                tor=jso['torrents'][0]
                
                upT = (
                f"**Seeding...**\n\n"
                f"  **Name:** {tor['name']}\n"
                f"  **Progress:** {tor['progress']}%\n"
                f"  **Leechers:** {tor['leechers']}\n"
                f"  **Seeders:** {tor['seeders']}\n"
                f"  **Size:** {humanr_size(tor['size'])}\n\n"
                f"  **Warnings:** {tor.get('warnings', 'None')}"
                )
            
                t_diff = time.time() - ls_t
                if t_diff >= 10 and upT != ls_msg:
                    await msg.edit_text(upT)
                    ls_t = time.time()
                    ls_msg = upT
            
            await asyncio.sleep(10)  # Await is mandatory in async functions
        infol = seedr.get_folder_items(folder_id)
        if not infol:
            await msg.edit_text(f"**Error!**\nSorry cant get folder data id:{folder_id}")
            return
        if infol['files'] and len(infol['files']) >= 1:
            for file in infol['files']:
                dlr = seedr.get_download_url(int(file['id']))
                if not dlr:
                    await msg.edit_text(f"Sorry cannot get download links for this file!\n\nName : {file['name']}")
                if dlr and dlr['success'] == True:
                    fmsg = (
                        f"**File Found!**\n\n"
                        f"  **Name:** {file['name']}\n"
                        f"  **Video:** {file['is_video']}\n"
                        f"  **Size:** {humanr_size(file['size'])}\n"
                        f"  **DLURL:** {dlr['url']}"
                        f" **It will upload soon**"
                    )
                    if 'thumb' in file:
                       prmsg = await client.send_photo(
                            chat_id=msg.chat.id,
                            photo=file['thumb'],
                            caption=fmsg
                        )
                    else:
                       prmsg = await client.send_message(
                            chat_id=msg.chat.id,
                            text=fmsg
                       )
                    if file["size"] >= Config.sizelimit:
                        await client.send_message(
                            chat_id=msg.chat.id,
                            text="Sorry This file was larger than my size 2GB please use download link in upper msg and another method for upload it.\nAfter get the file click below button to delete the file!.",
                            reply_markup = InlineKeyboardMarkup(
                            [
                                  [
                                      InlineKeyboardButton("Done!", callback_data=f"del_fol_{folder_id}")
                                  ]
                            ])
                        )
                        return
                    await msg.edit_text("**File Downloading to Server...!**")
                    dlpath = download_file(client, msg, dlr['url'], file['name'])
                    if file['is_video']:
                        await upload_video(client, msg, dlpath)
                    else:
                        await upload_document(client, msg, dlpath)
                    clean_dir(Config.dl_dir)
                    asyncio.sleep(2)
                    
            await msg.delete()            
        else:
            await msg.edit_text("**Sorry Cannot find files!...**")
        seedr.delete([{
                "type":"folder",
                "id":folder_id
            }])
        
    else:
        await msg.edit_text("Sorry torrent not added to seeding client")
