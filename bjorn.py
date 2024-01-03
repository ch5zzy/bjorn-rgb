import time
import argparse
from PIL import Image, ImageSequence
from requests import get
from io import BytesIO
from env import config_update_time, jsonblob_config_url
from threading import Thread
from sys import argv

# Check whether the simulator should be used
parser = argparse.ArgumentParser()
parser.prog = "bjorn"
parser.add_argument("-s", "--sim", action="store_true", default=False)

args = parser.parse_args(argv[1:])

if args.sim:
    from unicorn_hat_sim import unicornhathd as unicorn
else:
    import unicornhathd as unicorn

unicorn.rotation(0)
display_width, display_height = unicorn.get_shape()


def fetch_config():
    global img
    global img_url
    global frames

    response = get(jsonblob_config_url)
    if response.status_code != 200:
        print("Unable to fetch config.")
        return

    config = response.json()

    # Set the rotation and brightness
    unicorn.rotation(0)
    unicorn.brightness(config["brightness"])

    # Update the displayed image if it changed
    if config["image_url"] != img_url:
        # Only update the image if it is valid
        response = get(config["image_url"])
        if response.status_code != 200:
            print("Unable to fetch image.")
            return

        img_url = config["image_url"]
        img = Image.open(BytesIO(response.content), formats=["GIF"])
        img.save("cache.gif", save_all=True)
        frames = thumbnails(ImageSequence.Iterator(img))


def thumbnails(frames):
    thumbnails = []
    for frame in frames:
        thumbnail = frame.convert("RGBA")
        thumbnails.append(thumbnail)
    return thumbnails


# Load in the cached image
img = Image.open("cache.gif")
img_url = None
frames = thumbnails(ImageSequence.Iterator(img))

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
            frame_width, frame_height = frame.size
            for x in range(display_width):
                for y in range(display_height):
                    if x >= frame_width or y >= frame_height:
                        continue

                    pixel = frame.getpixel((frame_width - x - 1, y))
                    r, g, b, a = pixel
                    unicorn.set_pixel(x, y, r, g, b)

            unicorn.show()
            time.sleep(frame.info["duration"] * 0.001)

except KeyboardInterrupt:
    unicorn.off()
