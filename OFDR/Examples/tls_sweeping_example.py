# -*- coding: utf-8 -*-
"""
Created on Wed Sep  3 11:34:20 2025

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


# === Configure Laser for static mode operation ===
print("\n=== Change configuration ===")
Laser.start_wavelength = 1545.0 # nm
Laser.stop_wavelength = 1555.0 # nm
Laser.speed = 100 # nm/s


print("Laser ON")
Laser.on()

print("\n=== Retreive configuration ===")
start_wavelength = Laser.start_wavelength
stop_wavelength = Laser.stop_wavelength
speed = Laser.speed

sweeping_time = (stop_wavelength - start_wavelength)/speed

print("Start Wavelength = %.3f" % start_wavelength)
print("Stop Wavelength = %.3f" % stop_wavelength)
print("Speed = %.1f" % speed)
print("Sweeping Time = %.3f" % sweeping_time)


print("\n=== Start continous sweep ===")
Laser.start_sweep()
