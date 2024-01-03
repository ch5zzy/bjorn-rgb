from dotenv import load_dotenv
from os import environ

jsonblob_api_url = "https://jsonblob.com/api/jsonBlob/"
imgbb_upload_url = "https://api.imgbb.com/1/upload"

config_update_time = 10

load_dotenv()

jsonblob_id = environ["JSONBLOB_ID"]
imgbb_api_key = environ["IMGBB_API_KEY"]

jsonblob_config_url = f"{jsonblob_api_url}{jsonblob_id}"
