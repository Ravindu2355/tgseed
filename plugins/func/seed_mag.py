import asyncio, time
from bot import seedr
from plugins.func.simples import humanr_size
async def seed_file(maglink, msg):
    if not seedr.check_session():
        await msg.edit_text("Sorry, Seedr session was invalid!...")
        return
    
    js = seedr.add_magnet(maglink)
    if js and js["success"] == True:
        folder_id = js["id"]
        ls_t = time.time()
        ls_msg = ''
        
        while True:
            folders = seedr.get_folder_items().folders
            fol = next((fol for fol in folders if fol["id"] == folder_id), None)
            
            if fol:  # If folder is found, break the loop
                break
            
            upT = (
                f"**Seeding...**\n\n"
                f"**Name:** {fol['name']}\n"
                f"**Progress:** {fol['progress']}%\n"
                f"**Leechers:** {fol['leechers']}\n"
                f"**Seeders:** {fol['seeders']}\n"
                f"**Size:** {humanr_size(fol['size'])}\n\n"
                f"**Warnings:** {fol.get('warnings', 'None')}"
            )
            
            t_diff = time.time() - ls_t
            if t_diff >= 10 and upT != ls_msg:
                await msg.edit_text(upT)
                ls_t = time.time()
                ls_msg = upT
            
            await asyncio.sleep(3)  # Await is mandatory in async functions
