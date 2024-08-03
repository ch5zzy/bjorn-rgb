from io import BytesIO
import time
from image import recolor, thumbnails
from util import check_wifi, safe_get
from PIL import Image
from env import jsonblob_config_url


default_rotation = -90
default_brightness = 0.4

default_dim_start_hour = 22
default_dim_start_min = 0
default_dim_end_hour = 8
default_dim_end_min = 0
default_dim_brightness = 0.05


class Config:

    def __init__(self, unicorn):
        # Load in the cached image and no internet image
        self._cache_file = "cache.webp"
        display_width, display_height = unicorn.get_shape()
        try:
            self._cache_img = Image.open(self._cache_file)
        except:
            self._cache_img = Image.new(mode="1", size=(display_width, display_height))
        self._no_wifi_img = recolor(
            Image.open("nowifi.webp"), (255, 255, 255), (124, 242, 252)
        )

        self._img = None
        self._had_wifi = False

        self.img_url = None
        self.frames = None
        self.rotation = default_rotation
        self.brightness = default_brightness
        self.dim_start_hour = default_dim_start_hour
        self.dim_start_min = default_dim_start_min
        self.dim_end_hour = default_dim_end_hour
        self.dim_end_min = default_dim_end_min
        self.dim_brightness = default_dim_brightness

        self._use_cache_img()

    def fetch(self) -> bool:
        # Display a Wi-Fi symbol if the device has not been connected to the internet
        if not check_wifi():
            print("Waiting for internet connection.")
            if not self._had_wifi:
                self._img = self._no_wifi_img
                self.frames = thumbnails(self._img)
            return False

        self._had_wifi = True

        response = safe_get(jsonblob_config_url)
        if response == None or response.status_code != 200:
            print("Unable to fetch config.")
            self._use_cache_img()
            return False

        config = response.json()

        # Set the rotation and brightness
        self.rotation = config["rotation"]
        self.brightness = config["brightness"]

        # Set the dimming settings
        self.dim_start_hour = config["dim_start"]["hour"]
        self.dim_start_min = config["dim_start"]["minute"]
        self.dim_end_hour = config["dim_end"]["hour"]
        self.dim_end_min = config["dim_end"]["minute"]
        self.dim_brightness = config["dim_brightness"]

        # Update the displayed image if it changed
        if config["image_url"] != self.img_url:
            # Only update the image if it is valid
            response = safe_get(config["image_url"])
            if response == None or response.status_code != 200:
                print("Unable to fetch image.")
                self._use_cache_img()
                return False

            self.img_url = config["image_url"]
            self._img = Image.open(BytesIO(response.content), formats=["WEBP"])
            self._img.save(self._cache_file, save_all=True, lossless=True, quality=0)
            self.frames = thumbnails(self._img)

            return True
        return False

    @property
    def dim_mode(self):
        current_hour = time.localtime().tm_hour
        current_min = time.localtime().tm_min
        after_start = (
            current_hour == self.dim_start_hour and current_min >= self.dim_start_min
        ) or current_hour >= self.dim_start_hour
        before_end = (
            current_hour == self.dim_end_hour and current_min < self.dim_end_min
        ) or current_hour < self.dim_end_hour
        return (
            (
                (
                    self.dim_start_hour == self.dim_end_hour
                    and self.dim_end_min < self.dim_start_min
                )
                or (self.dim_start_hour > self.dim_end_hour)
            )
            and (after_start or before_end)
        ) or (after_start and before_end)

    def _use_cache_img(self):
        self.img_url = None
        if self._img != self._cache_img:
            self._img = self._cache_img
            self.frames = thumbnails(self._img)
