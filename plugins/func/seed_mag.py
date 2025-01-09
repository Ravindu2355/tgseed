from bot import seedr

def seed_file(maglink):
  if seedr.check_session():
    js = seedr.add_magnet(maglink)
    if js and js["success"] == True:
      folder_id=js["id"]
      while seedr.get_folder_items().
