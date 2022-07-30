#!/usr/bin/python3

import urllib.request

from InfluxUploader import InfluxUploader

# fetch from http
fp = urllib.request.urlopen("http://192.168.178.52/v_energies.html")
s_bytes = fp.read()
s = s_bytes.decode("utf8")
fp.close()

# extract only table of energies
s = s[s.find("<b>ENERGIES</b><br>"):len(s)]
s = s[s.find("<table>")+7:s.find("</table>")]
# replace html table tags
s = s.replace("</td></tr>", "\n")
s = s.replace("<tr><td>", "")
s = s.replace("</td><td>", "\t")
s = s[0:len(s)-1]  # remove last linebreak

# split string s by spaces, use (s.split(",")) to split on "," etc
E = s.split("\n")

for idx, line in enumerate(E):
    # for l in E:
    E2 = line.split("\t")
    E2[0] = E2[0].replace(" ", "_")
    E2[1] = float(E2[1])
    E[idx] = E2.copy()
# print(E)
# print(len(E))
# print(E[1][0])


fp = urllib.request.urlopen("http://192.168.178.52/v_phases.html")
s_bytes = fp.read()
s = s_bytes.decode("utf8")
fp.close()

# extract only table of phases
s = s[s.find("<b>PHASES</b><br>"):len(s)]
s = s[s.find(
    "<table><tr><td></td><td>A</td><td>B</td><td>C</td><td></td></tr>"):len(s)]
s = s[s.find("<table>")+7:s.find("</table>")]

s = s[s.find("<td>P</td><td>")+14:s.find("</td><td>W</td>")]
s = s.replace("</td><td>", "\t")

#P = s.split("\t")
P = [float(x) for x in s.split("\t")]
# print (P)


# fetch from http
fp = urllib.request.urlopen("http://192.168.178.52/v_cc.html")
s_bytes = fp.read()
s = s_bytes.decode("utf8")
fp.close()

# extract only table of energies
s = s[s.find("<b>CC</b><br>"):len(s)]
s = s[s.find("<table>")+7:s.find("</table>")]
# replace html table tags
s = s.replace("</td></tr>", "\n")
s = s.replace("<tr><td>", "")
s = s.replace("</td><td>", "\t")
s = s[0:len(s)-1]  # remove last linebreak

# split string s by spaces, use (s.split(",")) to split on "," etc
CC = s.split("\n")

for idx, line in enumerate(CC):
    # for l in E:
    CC2 = line.split("\t")
    CC2[0] = CC2[0].replace(" ", "_")
    CC2[1] = float(CC2[1])
    CC[idx] = CC2.copy()


fields = {
    E[0][0]: E[0][1],
    E[1][0]: E[1][1],
    E[2][0]: E[2][1],
    E[3][0]: E[3][1],
    E[4][0]: E[4][1],
    E[5][0]: E[5][1],
    E[6][0]: E[6][1],
    E[7][0]: E[7][1],
    E[8][0]: E[8][1],
    "Phase A": P[0],
    "Phase B": P[1],
    "Phase C": P[2],
    "CC_"+CC[0][0]: CC[0][1],
    "CC_"+CC[1][0]: CC[1][1],
    "CC_"+CC[2][0]: CC[2][1]
}


influx = InfluxUploader(verbose=False)
influx.upload(measurement='smartfox', fields=fields, tags={})
