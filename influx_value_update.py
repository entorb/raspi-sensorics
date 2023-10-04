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

measurement = "ShellyV1"

# Query the data you want to modify
# query = f'SELECT * from {measurement} where "kWh total" > 10'
query = f'SELECT * from {measurement} where "total" > 1000'
result = client.query(query)

# Iterate over the query result, modify and overwrite data
for p1 in result.get_points():
    tags = {"room": p1["room"]}
    fields = {
        # "kWh total": p1["kWh total"],  # / 1000,
        "kWh total": round(p1["total"] / 60 / 1000, 3)
        # "watt_avg_last_min": p1["watt_avg_last_min"],
        # "watt_now": p1["watt_now"],
        # "total": 123.456,
    }
    p2 = [
        {
            "measurement": measurement,
            "fields": fields,
            "tags": tags,
            "time": p1["time"],
        },
    ]
    # overwrite data
    client.write_points(p2)


# Close the connection
client.close()
