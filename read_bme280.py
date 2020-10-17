#!/usr/bin/python3

# reads temperature, pressure, humidity from bme280 sensor, connected via cable to raspi GPIO using i2c protocol

from Bme280 import Bme280
from InfluxUploader import InfluxUploader

bme280 = Bme280()
temperature, pressure, humidity = bme280.readBME280All()

my_measurement = 'bme280'

d_fields = {'temperature': temperature,
            'pressure': pressure, 'humidity': humidity}
d_tags = {'room': 'Schlafzimmer'}

influx = InfluxUploader(verbose=False)
influx.upload(measurement=my_measurement, fields=d_fields, tags=d_tags)
