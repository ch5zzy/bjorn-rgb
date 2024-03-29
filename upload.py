from requests import post, put
from image import resize
from env import jsonblob_config_url, imgbb_upload_url, imgbb_api_key
from PIL import Image


def update_config(config: dict[str, str]) -> bool:
    return put(jsonblob_config_url, json=config).status_code == 200


def upload_image(img_path: str, interpolation=Image.Resampling.NEAREST) -> str:
    return post(
        imgbb_upload_url,
        data={
            "key": imgbb_api_key,
            "image": resize(img_path, interpolation=interpolation),
        },
    ).json()["data"]["url"]
