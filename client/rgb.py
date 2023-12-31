import time
from sys import argv
from PIL import Image, ImageSequence

from unicorn_hat_sim import unicornhathd as unicorn

unicorn.rotation(0)
unicorn.brightness(0.6)

width, height = unicorn.get_shape()

img = Image.open(argv[1])

def thumbnails(frames):
    thumbnails = []
    for frame in frames:
        thumbnail = frame.convert("RGBA")
        thumbnail.thumbnail((width, height), Image.NEAREST)
        thumbnails.append(thumbnail)
    return thumbnails

frames = thumbnails(ImageSequence.Iterator(img))

try:
    while True:
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
