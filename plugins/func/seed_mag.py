import asyncio, time, json
from bot import seedr
from plugins.func.simples import humanr_size, clean_dir
from plugins.func.dl import download_file
from plugins.func.tgup import upload_video, upload_document
from config import Config 
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from lg import logger as l

def is_valid_extension(filename, invalid_extensions):
    return not any(filename.endswith(ext) for ext in invalid_extensions)

# Example usage
invalid_exts = ['.txt', '.info', '.log', '.json', '. nfo', '.nfo']
#print(is_invalid_extension("example.mp4", invalid_exts))  # True (valid file)
#print(is_invalid_extension("document.txt", invalid_exts))  # False (invalid file)


async def seed_file(maglink, client, msg):
    if not seedr.check_session():
        await msg.edit_text("Sorry, Seedr session was invalid!...\nRetring...")
        if seedr.login():
            l.info("Successfully loged into seedr account!...")
            if not seedr.check_session():
                l.info("Sorry cant log into seedr account")
                await msg.edit_text("Sorry, Failed to login!....")
                return
            #l.info(f"account settings: {json.dumps(seedr.get_account_settings())}")
        else:
            l.info("Sorry cant log into seedr account")
            await msg.edit_text("Sorry, Failed to login!....")
            # Run the bot
            return
    
    js = seedr.add_magnet(maglink)
    if js and not js.get("success"):
        if js.get("wt"):
            await msg.edit_text("sorry! list is full!")
            return
    if js and js.get("success"):
      if js["success"] == True:
        folder_title = js["title"]
        folder_id = 0
        ls_t = time.time()
        ls_msg = ''
        st_t=time.time();
        timelim=Config.timelim or 30
        wr = 1
        tid = None
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
                if time.time() - st_t >= timelim and upT == ls_msg:
                    await msg.edit_text("**Task expired!**\nThat was too slow or not working!\n\n")
                    tid = tor['id']
                    wr = 0
                    break
                t_diff = time.time() - ls_t
                if t_diff == 0 or t_diff >= 10:
                    if upT != ls_msg:
                        await msg.edit_text(upT)
                        ls_t = time.time()
                        ls_msg = upT
            
            await asyncio.sleep(10) # Await is mandatory in async functions
        if wr == 0:
            wr = 1
            try:
                seedr.delete([{
                "type":"torrent",
                "id":tid
            }])
            except Exeption as e:
                print("err")
            print("returning")
            return
        infol = seedr.get_folder_items(folder_id)
        if not infol:
            await msg.edit_text(f"**Error!**\nSorry cant get folder data id:{folder_id}")
            return
        if infol['files'] and len(infol['files']) >= 1:
            for file in infol['files']:
              fname_s = file['name']
              isvN=is_valid_extension(fname_s, invalid_exts)
              if isvN:
                dlr = seedr.get_download_url(int(file['id']))
                if not dlr:
                    await msg.edit_text(f"Sorry cannot get download links for this file!\n\nName : {file['name']}")
                if dlr and dlr['success'] == True:
                    fmsg = (
                        f"**File Found!**\n\n"
                        f"  **Name:** {file['name']}\n"
                        f"  **Video:** {file['is_video']}\n"
                        f"  **Size:** {humanr_size(file['size'])}\n"
                        f"  **DLURL:** {dlr['url']}\n"
                        f" **It will upload soon**"
                    )
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
                    dlpath = await download_file(client, msg, dlr['url'], file['name'])
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
