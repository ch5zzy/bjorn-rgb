from requests import post, put
from image import resize
from env import jsonblob_api_url, jsonblob_id, imgbb_api_url, imgbb_api_key


def update_config(config: dict[str, str]) -> bool:
    return put(f"{jsonblob_api_url}{jsonblob_id}", json=config).status_code == 200


def upload_image(img_path: str) -> str:
    return post(
        imgbb_api_url,
        data={"key": imgbb_api_key, "image": resize(img_path)},
    ).json()["data"]["url"]
