import os

class Config(object):
  apiid = int(os.getenv("apiid"))
  
  apihash = os.getenv("apihash")
  
  tk = os.getenv("tk")
  
  AUTH = os.getenv("auth")
  
  OWNER =os.getenv("owner")

  PRARAL_LIMIT = int(os.getenv("pps",3))

  seedr_email = os.getenv("seedrEmail")

  seedr_pw = os.getenv("seedrPw")
