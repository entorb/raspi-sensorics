#!/usr/bin/env python3.9
# my raspi currently has only 3.9
"""
Access API gen1 of Shelly device (Plug S) using basic authentication.

see https://shelly-api-docs.shelly.cloud/gen1/#shelly-plug-plugs-settings
based on https://github.com/entorb/shelly-api
"""

import json
import requests
from zoneinfo import ZoneInfo

from shelly_credentials import password, shelly1_ip as shelly_ip, username

from InfluxUploader import InfluxUploader
import datetime as dt

TZ_UTC = dt.timezone.utc
TZ_DE = ZoneInfo("Europe/Berlin")

influx = InfluxUploader(verbose=False)


# public endpoint with no auth required
# url = f"http://{shelly_ip}/shelly"

# other endpoints require basic auth, if auth is configured in web interfaces
# status endpoint, shows much data, e.g. temperature
# see https://shelly-api-docs.shelly.cloud/gen1/#shelly-plug-plugs-meter-0
# url = f"http://{shelly1_ip}/status"

# read meter data
# see https://shelly-api-docs.shelly.cloud/gen1/#shelly-plug-plugs-status
url = f"http://{shelly_ip}/meter/0"

# creating session with http basic auth
session = requests.Session()
session.auth = (username, password)


# def write_data_to_file(data: dict) -> None:
#     with open("data.json", mode="w", encoding="utf-8", newline="\n") as fh:
#         json.dump(data, fh, ensure_ascii=False, sort_keys=False, indent=2)


def convert_shelly_timestamp_to_influx(timestamp: int) -> str:
    """Convert Shelly timestamp to Influx datetime string in UTC."""
    # Shelly seems to be converting it wrong, the timestamp is in UTC
    # converting it back to a datetime gives local time but as UTC
    # print(timestamp) vs. print(time.time())

    # fixing the timezone
    # add UTC-timezone into to timestamp
    dt1 = dt.datetime.fromtimestamp(timestamp, tz=TZ_UTC)
    # overwrite by real timezone
    dt1 = dt1.replace(tzinfo=TZ_DE)

    # Convert the datetime object to UTC
    dt2 = dt1.astimezone(TZ_UTC)

    # Format the UTC datetime to str as required by InfluxDB
    current_time = dt2.strftime("%Y-%m-%dT%H:%M:%SZ")
    return current_time


try:
    response = session.get(url, timeout=3)

    if response.status_code == 200:
        # print(response.text)
        # convert response to dict
        data = json.loads(response.text)
        # print(data)
        # write_data_to_file(data)

        # Current real AC power being drawn, in Watts
        watt_now = float(data["power"])
        # Total energy consumed by the attached electrical appliance in Watt-minute
        total = float(data["total"])
        kWh_total = round(total / 60 / 1000, 3)
        # print(kWh_total)
        # Energy counter value for the last 3 round minutes in Watt-minute
        watt_past_minutes = [float(x) for x in data["counters"]]
        # print(watt_past_minutes)
        # Timestamp of the last energy counter value, with the applied timezone
        # TM: No, actually it is the current timestamp, not the timestamp related to past counters!   # noqa: E501
        timestamp = int(data["timestamp"])

        my_measurement = "Shelly3"
        tags = {"room": "Balkon"}
        fields = {
            "watt_now": watt_now,
            "watt_last": watt_past_minutes[0],
            "kWh_total": kWh_total,
        }

        # current_time = convert_shelly_timestamp_to_influx(timestamp=timestamp)

        influx.upload(
            measurement=my_measurement,
            fields=fields,
            tags=tags,
            # datetime=current_time,
        )

    else:
        print(
            f"Failed to access the API. Status code: {response.status_code}, text: {response.text}",  # noqa: E501
        )

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {str(e)}")