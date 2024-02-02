from PIL import Image, ImageSequence
from io import BytesIO
from base64 import b64encode
import numpy as np


def resize(img_path: str, size=(16, 16)) -> str:
    frames = thumbnails(Image.open(img_path))

    # Convert the image to a buffer
    buffer = frames_to_buffer(frames)

    # Return a base64 encoded string
    return b64encode(buffer.getvalue())


def thumbnails(img, size=(16, 16)):
    frames = ImageSequence.Iterator(img)

    thumbnails = []
    for frame in frames:
        frame = frame.resize(size, Image.NEAREST)
        thumbnail = frame.convert("RGB")
        thumbnails.append(thumbnail)
    return thumbnails


def recolor(img: Image, original: tuple[int], new: tuple[int]) -> Image:
    frames = thumbnails(img)

    new_frames = []
    for frame in frames:
        frame_data = np.array(frame)

        # Replace occurrences of the original color with the new color
        r, g, b = frame_data.T
        replaceable_areas = (r == original[0]) & (g == original[1]) & (b == original[2])
        frame_data[..., :][replaceable_areas.T] = new

        new_frame = Image.fromarray(frame_data)
        new_frame.info = frame.info
        new_frames.append(new_frame)

    buffer = frames_to_buffer(new_frames)
    return Image.open(buffer, formats=["WEBP"])


def frames_to_buffer(frames) -> BytesIO:
    # Save the image to a buffer
    buffer = BytesIO()
    first_frame_duration = (
        frames[0].info["duration"] if "duration" in frames[0].info else 0
    )

    if len(frames) > 1:
        frames[0].save(
            buffer,
            save_all=True,
            append_images=frames[1:],
            duration=first_frame_duration,
            loop=0,
            format="WEBP",
            lossless=True,
            quality=100,
        )
    else:
        frames[0].save(
            buffer,
            save_all=True,
            duration=first_frame_duration,
            loop=0,
            format="WEBP",
            lossless=True,
            quality=100,
        )

    return buffer
