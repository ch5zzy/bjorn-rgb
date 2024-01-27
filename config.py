from upload import update_config, upload_image
import argparse
from sys import argv, exit
from os import path
from PIL import Image

parser = argparse.ArgumentParser()
parser.prog = "config"
parser.add_argument("image_path")
parser.add_argument("-b", "--brightness", default=0.6, type=float)
parser.add_argument("-r", "--rotation", default=-90, type=int)

args = parser.parse_args(argv[1:])

# Check that the file exists and is of the right ratio
if not path.isfile(args.image_path):
    print("Image path is not valid.")
    exit(-1)
else:
    img = Image.open(args.image_path)
    if img.size[0] != img.size[1]:
        print("Image must have 1:1 ratio.")
        exit(-1)

# Check brightness range
if args.brightness < 0 or args.brightness > 1:
    print("Brightness must be between 0 and 1.")
    exit(-1)

# Check rotation range
max_rot = 270
if args.rotation < -max_rot or args.rotation > max_rot:
    print("Rotation must be between -270 and 270.")
    exit(-1)

# Construct the config
config = dict[str]()
config["image_url"] = upload_image(args.image_path)
config["brightness"] = args.brightness
config["rotation"] = args.rotation

if update_config(config):
    print("Configuration updated successfully!")
else:
    print("Configuration could not be updated.")
