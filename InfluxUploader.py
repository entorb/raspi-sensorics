#!/usr/bin/python3

from influxdb import InfluxDBClient
from configparser import ConfigParser


class InfluxUploader():
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        if self.verbose:
            print("InfluxUploader: verbose = True")
        self.config = ConfigParser(interpolation=None)
        # interpolation=None -> treats % in values as char % instead of interpreting it
        self.config.read('InfluxUploader.ini', encoding='utf-8')
        self.con = self.connect()

    def connect(self) -> InfluxDBClient:
        client = InfluxDBClient(
            host=self.config.get('Connection', 'host'),
            port=self.config.getint('Connection', 'port'),
            username=self.config.get('Connection', 'username'),
            password=self.config.get('Connection', 'password'))
        client.switch_database(self.config.get('Connection', 'database'))
        return client

    def upload(self, measurement: str, fields: dict, tags: dict = {}):
        json = [
            {
                "measurement": measurement,
                "fields": fields,
                "tags": tags
            }]

        if self.verbose:
            print(f"uploading:\n {json}")

        # time_precision is important for performance
        if self.con.write_points(json, time_precision="s") == True:
            print("data inserted into InfluxDB")
        else:
            print("ERROR: Write to InfluxDB not successful")

    # def query(self, query):
    # # TODO: not needed for a pure upload class
    #     print("Querying data: " + query)
    #     result = self.con.query(query)
    #     print("Result: {0}".format(result))

    def test(self):
        print("list of databases:")
        print(self.con.get_list_database())


def test():
    influx_uploader = InfluxUploader(verbose=True)
    influx_uploader.test()

    # requires grant read on mydb to myuser
    # influx_uploader.query('SHOW MEASUREMENTS')


if __name__ == "__main__":
    test()
