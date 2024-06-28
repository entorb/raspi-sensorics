#!/usr/bin/env python3.9
# my raspi currently has only 3.9
"""
Access API gen1 of Shelly device (Plug S) using basic authentication.

see https://shelly-api-docs.shelly.cloud/gen1/#shelly-plug-plugs-settings
based on https://github.com/entorb/shelly-api

started via /etc/systemd/system/shelly1.service
"""

import datetime as dt
import json
import time
from zoneinfo import ZoneInfo

import requests

from InfluxUploader import InfluxUploader
from shelly_credentials import password, username
from shelly_credentials import shelly1_ip as shelly_ip
from shelly_credentials import username

TZ_UTC = dt.timezone.utc
TZ_DE = ZoneInfo("Europe/Berlin")

influx = InfluxUploader(verbose=False)

# read meter data
# see https://shelly-api-docs.shelly.cloud/gen1/#shelly-plug-plugs-status
shelly_url = f"http://{shelly_ip}/meter/0"

# Influx data setup
influx_measurement = "Shelly3"
influx_tags = {"room": "Balkon"}

# creating session with http basic auth
session = requests.Session()
session.auth = (username, password)


def convert_shelly_timestamp_to_influx(timestamp: int) -> str:
    """
    Convert Shelly timestamp to Influx datetime string in UTC.

    Seconds are trimmed to last full minute, to compensate for the delay
    since 'watt_last_minute' was measured.
    """
    # Shelly seems to be converting it wrong, the timestamp is in UTC
    # converting it back to a datetime gives local time but as UTC
    # compare print(timestamp) vs. print(time.time())

    # fixing the timezone
    # add UTC-timezone into to timestamp
    dt1 = dt.datetime.fromtimestamp(timestamp, tz=TZ_UTC)
    # overwrite by real timezone and trim seconds
    dt1 = dt1.replace(tzinfo=TZ_DE, second=0)
    # convert to UTC
    dt1 = dt1.astimezone(TZ_UTC)

    # format the UTC datetime to str as required by InfluxDB
    current_time = dt1.strftime("%Y-%m-%dT%H:%M:%SZ")
    return current_time


def fetch_data() -> None:
    """Fetch data from API and upload to InfluxDB."""
    try:
        response = session.get(shelly_url, timeout=3)

        if response.status_code == 200:
            # convert response to dict
            data = json.loads(response.text)

            # extract and convert relevant data
            # api spec: Current real AC power being drawn, in Watts
            watt_now = float(data["power"])
            # api spec: Total energy consumed by the attached electrical appliance in Watt-minute  # noqa: E501
            total = float(data["total"])
            kWh_total = round(total / 60 / 1000, 3)
            # api spec: Energy counter value for the last 3 round minutes in Watt-minute
            watt_past_minutes = [float(x) for x in data["counters"]]
            # api spec: Timestamp of the last energy counter value, with the applied timezone  # noqa: E501
            # TM: No, actually it is the current timestamp, not the timestamp related to past counters!   # noqa: E501
            timestamp = int(data["timestamp"])
            my_datetime = convert_shelly_timestamp_to_influx(timestamp=timestamp)

            influx.upload(
                measurement=influx_measurement,
                tags=influx_tags,
                fields={
                    "watt_now": watt_now,
                    "watt_last": watt_past_minutes[0],
                    "kWh_total": kWh_total,
                },
                datetime=my_datetime,
            )

        else:
            print(
                f"Error: Failed to access the API. Status code: {response.status_code}, text: {response.text}",  # noqa: E501
            )

    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")


def sleep_till_next_minute(offset: int = 3) -> None:
    """
    Sleep till next full minute plus 'offset' seconds.
    """
    current_time = dt.datetime.now()
    next_minute = (current_time + dt.timedelta(minutes=1)).replace(
        second=0,
        microsecond=0,
    )
    time_until_next_minute = (next_minute - current_time).total_seconds()
    time.sleep(time_until_next_minute + offset)


if __name__ == "__main__":
    while True:
        sleep_till_next_minute(offset=3)
        fetch_data()
