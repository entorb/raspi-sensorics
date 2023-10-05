#!/usr/bin/env python3.9
# my raspi currently has only 3.9
"""
Connect to MQTT (mosquito) message broker.

started by /etc/systemd/system/mqtt_influx.service
"""

import datetime as dt
import json
from zoneinfo import ZoneInfo

# pip install paho-mqtt
import paho.mqtt.client as mqtt

from InfluxUploader import InfluxUploader
from mqtt_credentials import hostname, password, port, username

TZ_UTC = dt.timezone.utc
TZ_DE = ZoneInfo("Europe/Berlin")

# Create an MQTT client instance
mqtt_client = mqtt.Client("raspi3-client")
mqtt_client.username_pw_set(username, password)

# Create InfluxDB client instance
influx_client = InfluxUploader(verbose=False)
influx_measurement = "Shelly3"


def convert_shelly_timestamp_to_influx(timestamp: int) -> str:
    """
    Convert Shelly timestamp to Influx datetime string in UTC.

    trimming to last second not needed, since data is pushed
    via MQTT as soon as the minute is over/the register is updated
    """
    dt1 = dt.datetime.fromtimestamp(timestamp, tz=TZ_DE)
    # dt1 = dt1.replace(second=0)
    dt1 = dt1.astimezone(TZ_UTC)
    current_time = dt1.strftime("%Y-%m-%dT%H:%M:%SZ")
    return current_time


def on_connect(mqtt_client, userdata, flags, rc) -> None:
    """Callback when the client connects MQTT broker."""  # noqa: D401
    if rc == 0:
        print("Connected to MQTT")
        # topics look like "DeviceName/status/switch:0"
        mqtt_client.subscribe("+/status/switch:0")  # "+" = 1-level, "#" = all-level
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
    else:
        print("Connection to MQTT failed with result code " + str(rc))


def on_disconnect(mqtt_client, userdata, rc) -> None:
    """Callback when the client is disconnected from the MQTT broker."""  # noqa: D401
    if rc != 0:
        print(f"Unexpected disconnection. Error code: {rc}")


def on_message(mqtt_client, userdata, message) -> None:
    """Callback when a message is received from the MQTT broker."""  # noqa: D401
    # print(f"Received message on topic '{message.topic}': {message.payload.decode()}")
    devicename = message.topic.split("/")[0]
    if devicename == "Plug2":
        room = "Torben"
    elif devicename == "Plug3":
        room = "Wohnzimmer"
    else:
        print(f"Unknown Device '{devicename}' in topic '{message.topic}'")
        return

    # extract data from body and convert to dict
    s = message.payload.decode()
    data = json.loads(s)

    # selection and conversion of measurements
    # api spec: Last measured instantaneous active power (in Watts) delivered to the attached load   # noqa: E501
    watt_now = float(data["apower"])
    # api spec: Total energy consumed in Watt-hours
    kWh_total = round(float(data["aenergy"]["total"] / 1000), 3)
    # api spec: Energy consumption by minute (in Milliwatt-hours) for the last three minutes  # noqa: E501
    past_minutes = [float(x) for x in data["aenergy"]["by_minute"]]
    # api spec: Convert to avg watt per min
    watt_past_minutes = [round(x * 60 / 1000, 1) for x in past_minutes]
    # TODO: bug in Shelly APIv2: [0] is not constant
    watt_last = watt_past_minutes[1]
    # api spec: Temperature in Celsius (null if temperature is out of the measurement range)  # noqa: E501
    # temperature = float(data["temperature"]["tC"])
    # api spec: Unix timestamp of the first second of the last minute
    # TM: No, actually it is the current timestamp, not the timestamp related to past counters!   # noqa: E501
    timestamp = int(data["aenergy"]["minute_ts"])
    my_datetime = convert_shelly_timestamp_to_influx(timestamp)
    # print(devicename, room, watt_now, watt_last, kWh_total, timestamp, temperature)

    # upload to InfluxDB
    influx_client.upload(
        measurement=influx_measurement,
        tags={"room": room},
        fields={
            "watt_now": watt_now,
            "watt_last": watt_last,
            "kWh_total": kWh_total,
        },
        datetime=my_datetime,
    )


# Set the callback functions
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_disconnect = on_disconnect

# Connect to the MQTT broker
mqtt_client.connect(hostname, port, keepalive=60)

try:
    # NOT: while True, as that eats the CPU !!!
    mqtt_client.loop_forever()
except KeyboardInterrupt:
    print("Script interrupted. Disconnecting from MQTT broker.")
    mqtt_client.disconnect()
    mqtt_client.loop_stop()
