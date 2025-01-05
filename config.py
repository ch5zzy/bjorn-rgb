from enum import Enum
from io import BytesIO
from image import recolor, thumbnails
from util import check_wifi, safe_get
from PIL import Image
from env import jsonblob_config_url
from clock import Clock


class GraphicsMode(Enum):
    Image = "IMAGE"
    Script = "SCRIPT"


default_rotation = -90
default_brightness = 0.4

default_dim_start_hour = 22
default_dim_start_min = 0
default_dim_end_hour = 8
default_dim_end_min = 0
default_dim_brightness = 0.05
default_detect_timezone_from_ip = True

default_graphics_mode = GraphicsMode.Image


class Config:

    def __init__(self, unicorn, clock: Clock):
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
        self._bad_script_img = recolor(
            Image.open("badscript.webp"), (255, 255, 255), (252, 124, 124)
        )

        self._img = None
        self._had_wifi = False

        self._clock = clock

        self.graphics_mode = default_graphics_mode
        self.img_url = None
        self.frames = None
        self.rotation = default_rotation
        self.brightness = default_brightness
        self.dim_start_hour = default_dim_start_hour
        self.dim_start_min = default_dim_start_min
        self.dim_end_hour = default_dim_end_hour
        self.dim_end_min = default_dim_end_min
        self.dim_brightness = default_dim_brightness
        self.detect_timezone_from_ip = default_detect_timezone_from_ip
        self.setup_script = None
        self.loop_script = None

        self._use_cache_img()

    def fetch(self) -> bool:
        # Display a Wi-Fi symbol if the device has not been connected to the internet
        if not check_wifi():
            print("Waiting for internet connection.")
            if not self._had_wifi:
                self.set_image(self._no_wifi_img)
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
        self.detect_timezone_from_ip = config["detect_timezone_from_ip"]

        self.graphics_mode = config["graphics_mode"]
        if self.graphics_mode == GraphicsMode.Image.value:
            return self._update_image(config)
        elif self.graphics_mode == GraphicsMode.Script.value:
            return self._update_script(config)

    def set_image(self, img):
        self._img = img
        self.frames = thumbnails(self._img)

    def _update_image(self, config):
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

    def _update_script(self, config):
        did_update = (
            self.setup_script != config["script"]["setup"]
            or self.loop_script != config["script"]["loop"]
        )

        # Update the script used on the device
        self.setup_script = config["script"]["setup"]
        self.loop_script = config["script"]["loop"]

        return did_update

    @property
    def dim_mode(self):
        current_hour = self._clock.localtime().tm_hour
        current_min = self._clock.localtime().tm_min
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
