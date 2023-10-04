#!/usr/bin/python3

"""Test script für MH-Z19."""

# pip3 install mh-z19
import mh_z19

print(mh_z19.read())
# not working because Bluetooth and serial have a conflict on Raspi3
