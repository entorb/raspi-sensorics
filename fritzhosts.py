#!/usr/bin/python3

# reads list of active hosts from Fritzbox

# installation
# pip3 install fritzconnection

from InfluxUploader import InfluxUploader
from fritzconnection.lib.fritzhosts import FritzHosts
from fritzconnection import FritzConnection

influx = InfluxUploader(verbose=False)
my_measurement = 'FritzHosts'

# fc = FritzConnection(address='192.168.178.1')
# print(fc)  # print router model informations


fh = FritzHosts(address='192.168.178.1', user='raspi',
                password='WwRLWlp3OcVMOna4kIIO')

# d = fh.get_specific_host_entry_by_ip('192.168.178.112')
# for key, value in d.items():
#     print(f"{key} = {value}")

l_mac_blacklist = []
l_mac_blacklist.append('E0:C7:67:D9:AE:C4')  # FR
l_mac_blacklist.append('24:1B:7A:AE:DD:84')  # FR
# l_mac_blacklist.append('B8:27:EB:05:7C:7E')  # raspi3


hosts = fh.get_hosts_info()
for index, host in enumerate(hosts, start=1):
    status = 'active' if host['status'] else '-'
    ip = host['ip'] if host['ip'] else '-'
    mac = host['mac'] if host['mac'] else '-'
    hn = host['name']
    # print(f'{index:>3}: {ip:<16} {hn:<28} {mac:<17}   {status}')
    if status == 'active' and mac not in l_mac_blacklist:
        print(f'{index:>3}: {ip:<16} {hn:<28} {mac:<17}   {status}')
        d_fields = {'active': 1}
        d_tags = {'hostname': hn, 'mac': mac}
        influx.upload(measurement=my_measurement, fields=d_fields, tags=d_tags)
        # print(hn)
