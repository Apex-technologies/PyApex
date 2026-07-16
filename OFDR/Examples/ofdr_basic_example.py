# -*- coding: utf-8 -*-
"""
Created on Wed Sep  3 10:05:21 2025

Example of using Instrument.OFDR.

This script demonstrates how to:
1. Connect to the device
2. Configure an OFDR measurement
3. Run a measurement
4. Retrieve and display the data

"""
import os
os.chdir("..")

from Instrument import Instrument
from matplotlib import pyplot as plt


# Device connection parameters
HOST = "192.168.1.216"
PORT = 11111

# Try to connect to the instrument
dev = Instrument(HOST, PORT, False)

# Create OFDR object from the instrument
OFDR = dev.OFDR()

# Display device identification
print("Device Identification number:")
print(dev.IDN)




# === Configure OFDR ===
print("\n=== Initial configuration (defaults) ===")
conf = OFDR.get_configuration()

# Set mode: REFL (reflection) or TRANS (transmission)
OFDR.mode = "REFL" # or TRANS

# Select maximum length from available options
length_mode = OFDR.get_max_length_list()
print("\nOFDR length mode available :", length_mode)
OFDR.max_length = int(length_mode[2])

# Select span from available options
span_list = OFDR.get_span_list()
print("OFDR span available :", span_list)
OFDR.span = float(span_list[1])

# Set center wavelength in nm
OFDR.center = 1575.0

# Select Fourier window (SQUA = square, HANN = Hann window)
OFDR.fourier_window = "SQUA"

# Set group index (depends on fiber characteristics)
OFDR.group_index = 1.465

print("\n=== Applied configuration ===")
conf = OFDR.get_configuration()



# === Run measurement ===
print("\nExecuting single measurement...")
OFDR.single()

print("...waiting for measurement to complete...")
dev.OPC # Wait for operation complete

# === Retrieve and plot results ===
print("\nRetrieving measurement data...")
length = OFDR.get_length_axis()
amp = OFDR.get_amplitude()

plt.figure()
plt.plot(length, amp)
plt.grid()
plt.xlabel("Length (m)")
plt.ylabel("Amplitude (dB)")
plt.title("OFDR Measurement")
plt.tight_layout()
plt.show()

