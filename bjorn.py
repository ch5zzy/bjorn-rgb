import time
import atexit
from cmdline import parse_cmdline
from config import Config
from env import config_update_time
from threading import Thread
from sys import argv

from util import import_unicorn

# Check whether the simulator should be used
args = parse_cmdline(argv)
unicorn = import_unicorn(args.sim)

# Initialize and fetch the config
config = Config(unicorn)
config.fetch()

unicorn.rotation(config.rotation)
unicorn.brightness(config.brightness)
display_width, display_height = unicorn.get_shape()

config_did_update = False
dim_mode = False


def config_worker():
    global config_did_update
    global dim_mode

    while True:
        config_did_update = config.fetch()

        # Dim the device if it is late
        dim_mode = config.dim_mode
        unicorn.brightness(config.dim_brightness if dim_mode else config.brightness)

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
    prev_frame_duration = None
    frame_skip = 0

    # Respawn the config thread if it dies
    if not config_thread.is_alive():
        print("Config thread is not alive, respawning.")
        spawn_config_thread()

    # Draw the image on the display
    for frame in config.frames:
        # Break out of this loop if the config was updated
        if config_did_update:
            config_did_update = False
            frame_start = None
            break

        # Compute frame skip from previous frame
        if prev_frame_duration != None:
            frame_skip = (
                (time.time() - frame_start) - prev_frame_duration
                if frame_start != None
                else 0
            )

        # Check if we should skip to the next frame or adjust the duration to account for skipping
        frame_duration = frame.info["duration"] * 0.001
        if frame_skip > frame_duration:
            frame_skip -= frame_duration
            continue
        elif frame_skip >= 0:
            frame_duration -= frame_skip
            frame_skip = 0

        # Show a frame until its duration has passed
        frame_start = time.time()
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

        # Update the previous frame duration for frame skip checking
        prev_frame_duration = frame_duration
