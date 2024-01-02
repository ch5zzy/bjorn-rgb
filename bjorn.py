import time
from sys import argv
from PIL import Image, ImageSequence
from requests import get
from io import BytesIO
from env import config_update_time, jsonblob_api_url, jsonblob_id
from threading import Thread

from unicorn_hat_sim import unicornhathd as unicorn

unicorn.rotation(0)
width, height = unicorn.get_shape()


def fetch_config():
    global img
    global frames

    config = get(f"{jsonblob_api_url}{jsonblob_id}").json()

    # Set the rotation and brightness
    unicorn.rotation(0)
    unicorn.brightness(config["brightness"])

    # Update the displayed image
    img = Image.open(BytesIO(get(config["image_url"]).content), formats=["GIF"])
    frames = thumbnails(ImageSequence.Iterator(img))


def thumbnails(frames):
    thumbnails = []
    for frame in frames:
        thumbnail = frame.convert("RGBA")
        thumbnail.thumbnail((width, height), Image.NEAREST)
        thumbnails.append(thumbnail)
    return thumbnails


# Fetch the config on start
fetch_config()

last_update = time.time()
try:
    while True:
        # Fetch the most recent config on update
        now = time.time()
        if now - last_update >= config_update_time:
            last_update = now
            t = Thread(target=fetch_config)
            t.start()

        # Draw the image on the display
        for frame in frames:
            w, h = frame.size
            for x in range(width):
                for y in range(height):
                    if x >= w or y >= h:
                        continue

                    pixel = frame.getpixel((w - x - 1, y))
                    r, g, b, a = pixel
                    unicorn.set_pixel(x, y, r, g, b)

            unicorn.show()
            time.sleep(frame.info["duration"] * 0.001)

except KeyboardInterrupt:
    unicorn.off()
