#!/usr/bin/env python3


"""TM: based on
Demo file showing how to use the miflora library.
from https://github.com/open-homeautomation/miflora

TODO: check out the newer demo file


usage:
./mi-flower-care.py poll 1 Kaktus


TM: found via http://geomodule.com/sw-eng-notes/2017/11/04/raspberry-pi-xiaomi-flower-care-sensor/

HowTo: find MAC of sensor
sudo hcitool lescan
C4:7C:8D:6A:E6:B6 Flower care

HowTo install bluetooth requirements
sudo apt-get install python3-pip
sudo pip3 install bluepy
git clone https://github.com/open-homeautomation/miflora.git
cd miflora/
. ./build.sh
python3 setup.py build
sudo python3 setup.py install

Example
python3 demo.py poll C4:7C:8D:6A:E6:B6
 Getting data from Mi Flora
 FW: 3.2.1
 Name: Flower care
 Temperature: 28.8
 Moisture: 8
 Light: 90
 Conductivity: 0
 Battery: 100
"""

import argparse
import logging
import re
import sys

from InfluxUploader import InfluxUploader


from btlewrap import available_backends, BluepyBackend, GatttoolBackend, PygattBackend

from miflora.miflora_poller import (
    MiFloraPoller,
    MI_CONDUCTIVITY,
    MI_MOISTURE,
    MI_LIGHT,
    MI_TEMPERATURE,
    MI_BATTERY,
)
from miflora import miflora_scanner


def valid_miflora_mac(
    mac,
    pat=re.compile(r"C4:7C:8D:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}"),
):
    """Check for valid mac adresses."""
    if not pat.match(mac.upper()):
        raise argparse.ArgumentTypeError(
            f'The MAC address "{mac}" seems to be in the wrong format',
        )
    return mac


def poll(args):
    """Poll data from the sensor."""
    backend = _get_backend(args)

    macs = {}
    macs[1] = "C4:7C:8D:6A:E6:B6"

    mac = macs[args.sensor]

    poller = MiFloraPoller(mac, backend)

    tags = {}
    # tags["MAC"] = args.mac
    tags["MAC"] = mac
    tags["SensorNo"] = args.sensor
    tags["Plant"] = args.plant

    print("Getting data from Mi Flora")
    fields = {}
    fields["Temperature"] = poller.parameter_value(MI_TEMPERATURE)
    fields["Moisture"] = poller.parameter_value(MI_MOISTURE)
    fields["Light"] = poller.parameter_value(MI_LIGHT)
    fields["Conductivity"] = poller.parameter_value(MI_CONDUCTIVITY)
    fields["Battery"] = poller.parameter_value(MI_BATTERY)
    # print(fields)
    # print(tags)

    # print("FW: {}".format(poller.firmware_version()))
    # print("Name: {}".format(poller.name()))
    # print("Temperature: {}".format(fields["Temperature"]))
    # print("Moisture: {}".format(fields["Moisture"]))
    # print("Light: {}".format(fields["Light"]))
    # print("Conductivity: {}".format(fields["Conductivity"]))
    # print("Battery: {}".format(fields["Battery"]))

    # print (poller.parameter_value(MI_TEMPERATURE))

    influx = InfluxUploader(verbose=True)
    influx.upload(measurement="mi-flower-care", fields=fields, tags=tags)


def scan(args):
    """Scan for sensors."""
    backend = _get_backend(args)
    print("Scanning for 10 seconds...")
    devices = miflora_scanner.scan(backend, 10)
    print(f"Found {len(devices)} devices:")
    for device in devices:
        print(f"  {device}")


def _get_backend(args):
    """Extract the backend class from the command line arguments."""
    if args.backend == "gatttool":
        backend = GatttoolBackend
    elif args.backend == "bluepy":
        backend = BluepyBackend
    elif args.backend == "pygatt":
        backend = PygattBackend
    else:
        raise Exception(f"unknown backend: {args.backend}")
    return backend


def list_backends(_):
    """List all available backends."""
    backends = [b.__name__ for b in available_backends()]
    print("\n".join(backends))


def main():
    """Main function.

    Mostly parsing the command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--backend",
        choices=["gatttool", "bluepy", "pygatt"],
        default="gatttool",
    )
    parser.add_argument("-v", "--verbose", action="store_const", const=True)
    subparsers = parser.add_subparsers(help="sub-command help")

    # the poll parameter is defined here
    parser_poll = subparsers.add_parser("poll", help="poll data from a sensor")
    # parser_poll.add_argument('--mac', type=valid_miflora_mac, default='C4:7C:8D:6A:E6:B6')
    # poll parameter requires arguments: sensor (int)
    parser_poll.add_argument(
        "sensor",
        choices=[1],
        type=int,
        default=1,
        help="sensor no",
    )
    # poll parameter requires arguments: plant
    parser_poll.add_argument(
        "plant",
        choices=[
            "Ranke",
            "Rasen",
            "Hochbeet",
            "Kaktus",
        ],
        default="Rasen",
        help="name of plant",
    )
    parser_poll.set_defaults(func=poll)

    parser_scan = subparsers.add_parser("scan", help="scan for devices")
    parser_scan.set_defaults(func=scan)

    parser_scan = subparsers.add_parser(
        "backends",
        help="list the available backends",
    )
    parser_scan.set_defaults(func=list_backends)

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)

    # here the function given as parameter is started, in my case poll
    args.func(args)


if __name__ == "__main__":
    main()
