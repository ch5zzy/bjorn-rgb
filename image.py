from PIL import Image, ImageSequence
from io import BytesIO
from base64 import b64encode


def resize(img_path: str, size=(16, 16)) -> str:
    frames = ImageSequence.Iterator(Image.open(img_path))

    # Resize each image individually
    thumbnails = []
    for frame in frames:
        thumbnail = frame.convert("RGBA")
        thumbnail.thumbnail(size, Image.NEAREST)
        thumbnails.append(thumbnail)

    # Save the image to a buffer
    buffer = BytesIO()
    if len(thumbnails) > 1:
        thumbnails[0].save(
            buffer,
            save_all=True,
            append_images=thumbnails[1:],
            duration=thumbnails[0].info["duration"],
            loop=0,
            format="GIF",
        )
    else:
        thumbnails[0].save(
            buffer,
            save_all=True,
            duration=thumbnails[0].info["duration"],
            loop=0,
            format="GIF",
        )

    # Return a base64 encoded string
    return b64encode(buffer.getvalue())
