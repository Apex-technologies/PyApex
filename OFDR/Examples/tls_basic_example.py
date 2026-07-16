# -*- coding: utf-8 -*-
"""
Created on Wed Sep  3 12:02:37 2025

Example of using Instrument.TLS.

This script demonstrates how to:
1. Connect to the device
2. Power on TLS and configure it for static operation
3. Retreive configuration

"""
import os
os.chdir("..")

from Instrument import Instrument

# Device connection parameters
HOST = "192.168.1.119"
PORT = 21212

# Try to connect to the instrument
dev = Instrument(HOST, PORT, False)

# Create TLS (Tunable Laser Source) object
Laser = dev.TLS()

# Display device identification
print("Device Identification number:")
print(dev.IDN)

# === Configure Laser for static operation ===
print("\n=== Change configuration ===")
Laser.on()
Laser.power = 9 # Max power (may differ from real external power due to device internal losses)
Laser.wavelength = 1550.0

print("\n=== Retreive configuration ===")
power = Laser.power
wl = Laser.wavelength
status = Laser.status

print("Laser Power = ", power)
print("Actual Wavelength = ", wl)
print("Status = ", status)
