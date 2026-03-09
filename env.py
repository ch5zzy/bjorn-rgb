from dotenv import load_dotenv
from os import environ

jsonblob_api_url = "https://jsonblob.com/api/jsonBlob/"
imgbb_upload_url = "https://api.imgbb.com/1/upload"

config_update_time = 30

load_dotenv()

jsonblob_id = environ["JSONBLOB_ID"]
imgbb_api_key = environ["IMGBB_API_KEY"]
local_config_path = environ["LOCAL_CONFIG_PATH"]
if len(local_config_path) == 0:
    local_config_path = None

jsonblob_config_url = f"{jsonblob_api_url}{jsonblob_id}"
