#!/usr/bin/python3

"""Read list of active hosts from Fritzbox."""

# installation
# pip3 install fritzconnection

from InfluxUploader import InfluxUploader
from fritzconnection.lib.fritzhosts import FritzHosts

influx = InfluxUploader(verbose=False)
my_measurement = "FritzHosts"

# fc = FritzConnection(address='192.168.178.1')
# print(fc)  # print router model informations


fh = FritzHosts(  # noqa: S106
    address="192.168.178.1",
    user="raspi",
    password="xxx",
)

# d = fh.get_specific_host_entry_by_ip('192.168.178.112')
# for key, value in d.items():
#     print(f"{key} = {value}")

l_mac_blacklist = []
l_mac_blacklist.append("A1:B2:C3:D4:E6:F6")


hosts = fh.get_hosts_info()
for index, host in enumerate(hosts, start=1):
    status = "active" if host["status"] else "-"
    ip = host["ip"] if host["ip"] else "-"
    mac = host["mac"] if host["mac"] else "-"
    hn = host["name"]
    # print(f'{index:>3}: {ip:<16} {hn:<28} {mac:<17}   {status}')
    if status == "active" and mac not in l_mac_blacklist:
        print(f"{index:>3}: {ip:<16} {hn:<28} {mac:<17}   {status}")
        d_fields = {"active": 1}
        d_tags = {"hostname": hn, "mac": mac}
        influx.upload(measurement=my_measurement, fields=d_fields, tags=d_tags)
        # print(hn)
