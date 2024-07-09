import time
import argparse
import atexit
from PIL import Image
from requests import get, head
from io import BytesIO
from env import (
    config_update_time,
    jsonblob_config_url,
    default_rotation,
    default_brightness,
    default_dim_start_hour,
    default_dim_start_min,
    default_dim_end_hour,
    default_dim_end_min,
    default_dim_brightness,
)
from threading import Thread
from sys import argv
from image import recolor, thumbnails

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

# Load in the cached image and no internet image
cache_file = "cache.webp"
try:
    cache_img = Image.open(cache_file)
except:
    cache_img = Image.new(mode="1", size=(display_width, display_height))
no_wifi_img = Image.open("nowifi.webp")

# Initialize image related variables
img = None
img_url = None
frames = None

# Mark that the device has not been connected to the internet before
had_wifi = False
never_wifi_img = recolor(no_wifi_img, (255, 255, 255), (124, 242, 252))
disconnected_wifi_img = recolor(no_wifi_img, (255, 255, 255), (252, 139, 124))

dim_start_hour = default_dim_start_hour
dim_start_min = default_dim_start_min
dim_end_hour = default_dim_end_hour
dim_end_min = default_dim_end_min

brightness = default_brightness
dim_brightness = default_dim_brightness


def display_cache():
    global img
    global img_url
    global frames

    img_url = None
    if img != cache_img:
        img = cache_img
        frames = thumbnails(img)


def safe_get(url: str):
    response = None
    try:
        response = get(url)
    except:
        pass
    return response


def fetch_config() -> bool:
    global img
    global img_url
    global frames
    global had_wifi
    global brightness
    global dim_start_hour
    global dim_start_min
    global dim_end_hour
    global dim_end_min
    global dim_brightness

    # Display a Wi-Fi symbol if the device is not connected to the internet
    try:
        head("https://example.com").raise_for_status()
        had_wifi = True
    except:
        print("Waiting for internet connection.")
        if img != never_wifi_img and img != disconnected_wifi_img:
            # Display a blue symbol if the device has not been connected to the internet before, red otherwise
            img = never_wifi_img if not had_wifi else disconnected_wifi_img
            frames = thumbnails(img)
        return False

    response = safe_get(jsonblob_config_url)
    if response == None or response.status_code != 200:
        print("Unable to fetch config.")
        display_cache()
        return False

    config = response.json()

    # Set the rotation and brightness
    unicorn.rotation(config["rotation"])
    brightness = config["brightness"]

    # Set the dimming settings
    dim_start_hour = config["dim_start"]["hour"]
    dim_start_min = config["dim_start"]["minute"]
    dim_end_hour = config["dim_end"]["hour"]
    dim_end_min = config["dim_end"]["minute"]
    dim_brightness = config["dim_brightness"]

    # Update the displayed image if it changed
    if config["image_url"] != img_url:
        # Only update the image if it is valid
        response = safe_get(config["image_url"])
        if response == None or response.status_code != 200:
            print("Unable to fetch image.")
            display_cache()
            return False

        img_url = config["image_url"]
        img = Image.open(BytesIO(response.content), formats=["WEBP"])
        img.save(cache_file, save_all=True, lossless=True, quality=0)
        frames = thumbnails(img)

        return True
    return False


# Display the cached image
display_cache()

# Fetch the config on start
fetch_config()

config_did_update = False
dim_mode = False


def config_worker():
    global config_did_update
    global dim_mode
    global brightness

    while True:
        config_did_update = fetch_config()

        # Dim the device if it is late
        current_hour = time.localtime().tm_hour
        current_min = time.localtime().tm_min
        after_start = (
            current_hour == dim_start_hour and current_min >= dim_start_min
        ) or current_hour >= dim_start_hour
        before_end = (
            current_hour == dim_end_hour and current_min < dim_end_min
        ) or current_hour < dim_end_hour
        dim_mode = (
            (
                (dim_start_hour == dim_end_hour and dim_start_min < dim_end_min)
                or (dim_start_hour > dim_end_hour)
            )
            and (after_start or before_end)
        ) or (after_start and before_end)
        if dim_mode:
            brightness = dim_brightness
        unicorn.brightness(brightness)

        time.sleep(config_update_time)


# Turn the display off when exiting
atexit.register(unicorn.off)

# Spawn a separate thread for fetching the config
config_thread = None


def spawn_config_thread():
    global config_thread

    config_thread = Thread(target=config_worker)
    config_thread.daemon = True
    config_thread.start()


spawn_config_thread()

while True:
    frame_start = None
    frame_duration = None

    # Respawn the config thread if it dies
    if not config_thread.is_alive():
        print("Config thread is not alive, respawning.")
        spawn_config_thread()

    # Draw the image on the display
    for frame in frames:
        # Break out of this loop if the config was updated
        if config_did_update:
            config_did_update = False
            frame_start = None
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
                    if dim_mode:
                        r = min(r * 1.3, 255)
                        b = b * 0.7
                    unicorn.set_pixel(x, y, r, g, b)

            unicorn.show()
            run_once = True
