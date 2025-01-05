import time
from util import safe_get
from timezonefinder import TimezoneFinder
import geocoder
import ntplib
from os import environ


class Clock:

    def __init__(self):
        self._offset = 0

    def localtime(self):
        return time.localtime(time.time() + self._offset)

    def update_for_location(self):
        # Update the timezone and offset from system time
        timezone = self._get_timezone()
        if timezone != None:
            print("Setting timezone to " + timezone + ".")
            environ["TZ"] = timezone
            time.tzset()

            self._offset = self._get_ntp_time() - time.time()

    def _get_timezone(self):
        response = safe_get("https://api.ipify.org")
        if response == None or response.status_code != 200:
            return None

        ip = response.text
        lat, lng = geocoder.ip(ip).latlng

        return TimezoneFinder().timezone_at(lat=lat, lng=lng)

    def _get_ntp_time(self):
        try:
            client = ntplib.NTPClient()
            response = client.request("pool.ntp.org", version=3)
            return response.tx_time
        except:
            return None
