from dotenv import load_dotenv
from os import environ

default_rotation = -90
default_brightness = 0.4

default_dim_start_hour = 22
default_dim_start_min = 0
default_dim_end_hour = 8
default_dim_end_min = 0
default_dim_brightness = 0.05

jsonblob_api_url = "https://jsonblob.com/api/jsonBlob/"
imgbb_upload_url = "https://api.imgbb.com/1/upload"

config_update_time = 30

load_dotenv()

jsonblob_id = environ["JSONBLOB_ID"]
imgbb_api_key = environ["IMGBB_API_KEY"]

jsonblob_config_url = f"{jsonblob_api_url}{jsonblob_id}"
