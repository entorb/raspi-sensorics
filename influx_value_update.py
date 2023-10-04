#!/usr/bin/env python3.9
"""
Update Fields or Tags in an InfluxDB Measurement.
"""

from influxdb import InfluxDBClient
from configparser import ConfigParser

config = ConfigParser(interpolation=None)
config.read("InfluxUploader.ini", encoding="utf-8")


def connect() -> InfluxDBClient:
    """Connect to DB."""
    client = InfluxDBClient(
        host=config.get("Connection", "host"),
        port=config.getint("Connection", "port"),
        username=config.get("Connection", "username"),
        password=config.get("Connection", "password"),
    )
    client.switch_database(config.get("Connection", "database"))
    return client


client = connect()

# measurement = "Shelly"

# Query the data you want to modify
# query = f'SELECT * from {measurement} where "kWh total" > 10'
query = "SELECT kWh_total,watt_last,watt_now,room_1 from Shelly2"
result = client.query(query)

# Iterate over the query result, modify and overwrite data
for p1 in result.get_points():
    print(p1["time"])
    tags = {"room": p1["room_1"]}
    fields = {
        "kWh_total": p1["kWh_total"],  # / 1000,
        "watt_last": p1["watt_last"],
        "watt_now": p1["watt_now"],
    }
    p2 = [
        {
            "measurement": "Shelly3",
            "fields": fields,
            "tags": tags,
            "time": p1["time"],
        },
    ]
    # overwrite data
    client.write_points(p2)


# Close the connection
client.close()
