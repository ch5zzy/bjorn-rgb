# Bjorn RGB

**See [bjorn-ctl](https://github.com/ch5zzy/bjorn-ctl) for the configuration tool for devices running this service.**

This app is meant to run on a Raspberry Pi to display an image on a connected [Unicorn HAT HD](https://www.adafruit.com/product/3580). It periodically pulls a configuration file (see [bjorn-ctl](https://github.com/ch5zzy/bjorn-ctl)) to update the displayed image and other settings.

## Running

Configure the provided `.env.sample`  file with a [jsonblob](https://jsonblob.com/) ID for storing the configuration. If using the [bjorn-ctl](https://github.com/ch5zzy/bjorn-ctl) tool for updating the configuration, this ID should match the one provided to the configuration tool. Rename the file to `.env`.

Follow the provided installation instructions for the [Unicorn HAT HD Python library](https://github.com/pimoroni/unicorn-hat-hd).

Then, install dependencies and run the script with `pip install -r requirements.txt; python3 bjorn.py`.

The provided `service/bjorn.service` can be modified and used to automatically run the script on boot. The `bjorn` script automatically pulls updates from the GitHub repo before running the app.

## WiFi

This script will display a wireless symbol the device is not connected to the internet upon starting. If you would like the WiFi network to be easily configurable without having to SSH into the device or connect it to a display, [wifi-setup](https://github.com/davidflanagan/wifi-setup/tree/master) may be a good option.
