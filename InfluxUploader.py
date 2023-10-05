#!/usr/bin/env python3.10

"""
InfluxDB Uploader.

upload data into InfluxDB
read credentials from .ini file
"""

# install via
# pip3 install influxdb-client

from configparser import ConfigParser

from influxdb import InfluxDBClient


class InfluxUploader:
    """InfluxUploader Class."""

    def __init__(self, verbose: bool = False) -> None:  # noqa: D107
        self.verbose = verbose
        if self.verbose:
            print("InfluxUploader: verbose = True")
        self.config = ConfigParser(interpolation=None)
        # interpolation=None -> treats % in values as char % instead of interpreting it
        self.config.read("InfluxUploader.ini", encoding="utf-8")
        self.con = self.connect()

    def connect(self) -> InfluxDBClient:
        """Connect to DB."""
        client = InfluxDBClient(
            host=self.config.get("Connection", "host"),
            port=self.config.getint("Connection", "port"),
            username=self.config.get("Connection", "username"),
            password=self.config.get("Connection", "password"),
        )
        client.switch_database(self.config.get("Connection", "database"))
        return client

    def upload(
        self,
        measurement: str,
        fields: dict[str, int | float],
        tags: dict[str, str],
        datetime: str = "",
    ) -> None:
        """
        Upload measurement data.

        datetime string, created via datetime module
          dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        """
        json = [
            {
                "measurement": measurement,
                "tags": tags,
                "fields": fields,
            },
        ]
        if datetime != "":
            # dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            json[0]["time"] = datetime
            if self.verbose:
                print("adding timestamp")

        if self.verbose:
            print(f"uploading:\n {json}")

        # time_precision is important for performance
        if self.con.write_points(json, time_precision="s") is True:
            if self.verbose:
                print("data inserted into InfluxDB")
        else:
            print("ERROR: Write to InfluxDB not successful")

    # def query(self, query):
    # # TODO: not needed for a pure upload class
    #     print("Querying data: " + query)
    #     result = self.con.query(query)
    #     print("Result: {0}".format(result))

    def test(self) -> None:
        """Test access by reading list of databases."""
        print("list of databases:")
        print(self.con.get_list_database())


def test() -> None:
    """Test."""
    influx_uploader = InfluxUploader(verbose=True)
    influx_uploader.test()

    # requires grant read on mydb to myuser
    # influx_uploader.query('SHOW MEASUREMENTS')


if __name__ == "__main__":
    test()
