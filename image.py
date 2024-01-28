from PIL import Image, ImageSequence
from io import BytesIO
from base64 import b64encode


def resize(img_path: str, size=(16, 16)) -> str:
    frames = ImageSequence.Iterator(Image.open(img_path))

    # Resize each image individually
    thumbnails = []
    for frame in frames:
        frame = frame.resize(size, Image.NEAREST)
        thumbnails.append(frame)

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
            disposal=2,
        )
    else:
        thumbnails[0].save(
            buffer,
            save_all=True,
            duration=thumbnails[0].info["duration"],
            loop=0,
            format="GIF",
            disposal=2,
        )

    # Return a base64 encoded string
    return b64encode(buffer.getvalue())
