import time
import argparse
import atexit
from PIL import Image, ImageSequence
from requests import get
from io import BytesIO
from env import (
    config_update_time,
    jsonblob_config_url,
    default_rotation,
    default_brightness,
)
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

unicorn.rotation(default_rotation)
unicorn.brightness(default_brightness)
display_width, display_height = unicorn.get_shape()

cache_file = "cache.webp"


def fetch_config() -> bool:
    global img
    global img_url
    global frames

    # Display a Wi-Fi symbol if the device is not connected to the internet
    try:
        get("https://mozilla.org")
    except:
        print("Waiting for internet connection.")
        img = Image.open("nowifi.gif")
        frames = thumbnails(ImageSequence.Iterator(img))
        return

    response = get(jsonblob_config_url)
    if response.status_code != 200:
        print("Unable to fetch config.")
        return

    config = response.json()

    # Set the rotation and brightness
    unicorn.rotation(config["rotation"])
    unicorn.brightness(config["brightness"])

    # Update the displayed image if it changed
    if config["image_url"] != img_url:
        # Only update the image if it is valid
        response = get(config["image_url"])
        if response.status_code != 200:
            print("Unable to fetch image.")
            return

        img_url = config["image_url"]
        img = Image.open(BytesIO(response.content), formats=["WEBP"])
        img.save(cache_file, save_all=True, lossless=True, quality=0)
        frames = thumbnails(ImageSequence.Iterator(img))

        return True
    return False


def thumbnails(frames):
    thumbnails = []
    for frame in frames:
        thumbnail = frame.convert("RGB")
        thumbnails.append(thumbnail)
    return thumbnails


# Load in the cached image
try:
    img = Image.open(cache_file)
except:
    img = Image.new(mode="1", size=(display_width, display_height))
img_url = None
frames = thumbnails(ImageSequence.Iterator(img))

# Fetch the config on start
fetch_config()

config_did_update = False


def config_worker():
    global config_did_update

    while True:
        config_did_update = fetch_config()
        time.sleep(config_update_time)


# Turn the display off when exiting
atexit.register(unicorn.off)

# Spawn a separate thread for fetching the config
t = Thread(target=config_worker)
t.daemon = True
t.start()

frame_start = None
frame_duration = None
while True:
    # Draw the image on the display
    for frame in frames:
        # Break out of this loop if the config was updated
        if config_did_update:
            config_did_update = False
            break

        # Calculate the time to skip over in the current frame
        frame_skip = (
            (time.time() - frame_start) - frame_duration if frame_start != None else 0
        )

        # Show a frame until its duration has passed
        frame_start = time.time() - frame_skip
        frame_duration = frame.info["duration"] * 0.001
        run_once = False
        while not run_once or time.time() - frame_start < frame_duration:
            frame_width, frame_height = frame.size
            for x in range(display_width):
                for y in range(display_height):
                    if x >= frame_width or y >= frame_height:
                        continue

                    pixel = frame.getpixel((frame_width - x - 1, y))
                    r, g, b = pixel
                    unicorn.set_pixel(x, y, r, g, b)

            unicorn.show()
            run_once = True
