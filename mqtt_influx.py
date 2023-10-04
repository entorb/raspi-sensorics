#!/usr/bin/env python3.9
# my raspi currently has only 3.9
"""
Connect to MQTT (mosquito) message broker.

started by /etc/systemd/system/mqtt_influx.service
"""

# pip install paho-mqtt
import json

import paho.mqtt.client as mqtt

from InfluxUploader import InfluxUploader
from mqtt_credentials import hostname, password, port, username

# Create an MQTT client instance
mqtt_client = mqtt.Client("raspi3-client")
mqtt_client.username_pw_set(username, password)

# Create InfluxDB client instance
influx_client = InfluxUploader(verbose=False)


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
    # Last measured instantaneous active power (in Watts) delivered to the attached load   # noqa: E501
    watt_now = float(data["apower"])
    # Total energy consumed in Watt-hours
    kWh_total = round(float(data["aenergy"]["total"] / 1000), 3)
    # Energy consumption by minute (in Milliwatt-hours) for the last three minutes
    past_minutes = [float(x) for x in data["aenergy"]["by_minute"]]
    # Convert to avg watt per min
    watt_past_minutes = [round(x * 60 / 1000, 1) for x in past_minutes]
    # TODO: bug in Shelly APIv2: [0] is not constant
    watt_last = watt_past_minutes[1]

    # Unix timestamp of the first second of the last minute
    # TM: No, actually it is the current timestamp, not the timestamp related to past counters!   # noqa: E501
    # timestamp = int(data["aenergy"]["minute_ts"])
    # Temperature in Celsius (null if temperature is out of the measurement range)
    # temperature = float(data["temperature"]["tC"])

    # print(devicename, room, watt_now, watt_last, kWh_total, timestamp, temperature)

    # upload to InfluxDB
    my_measurement = "Shelly3"
    fields = {
        "watt_now": watt_now,
        "watt_last": watt_last,
        "kWh_total": kWh_total,
    }
    tags = {"room": room}

    influx_client.upload(
        measurement=my_measurement,
        fields=fields,
        tags=tags,
    )


# Set the callback functions
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_disconnect = on_disconnect

# Connect to the MQTT broker
mqtt_client.connect(hostname, port, keepalive=60)

try:
    mqtt_client.loop_forever()
    # NOT: while True, as that eats the CPU !!!
except KeyboardInterrupt:
    print("Script interrupted. Disconnecting from MQTT broker.")
    mqtt_client.disconnect()
    mqtt_client.loop_stop()
