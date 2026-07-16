# -*- coding: utf-8 -*-
"""
Created on Wed Sep  3 11:07:40 2025

Example of using Instrument.OFDR with spectral analysis.

This script demonstrates how to:
1. Connect to the device
2. Configure and run a basic OFDR measurement
3. Configure and run spectral analysis
4. Retrieve and plot the results

"""

import os

# adjust working directory (imports)
os.chdir("..")

from Instrument import Instrument
from matplotlib import pyplot as plt


# Device connection parameters
HOST = "192.168.1.18"
PORT = 21212

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
OFDR.max_length = int(length_mode[0])

# Select span from available options
span_list = OFDR.get_span_list()
print("OFDR span available :", span_list)
OFDR.span = float(span_list[0])

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

# === Configure Spectral Analysis ===
print("\n=== Configuring spectral analysis ===")
# Important: must run a measurement before configuring analysis
center_window = 0.0211# m
width = 0.01 # m
OFDR.set_conf_spectral_analysis(center_window, width)

center, width, window_type = OFDR.get_conf_spectral_analysis()
print("Spectral analysis configuration:")
print(f" - Window center : {center:.6f} m")
print(f" - Window width  : {width:.6f} m")
print(f" - Window type   : {window_type}")

print("\nExecuting analysis...")
OFDR.execute_spectral_analysis()

print("...waiting for analysis to complete...")
dev.OPC

print("\nRetrieving results...")
wl = OFDR.get_wavelength_axis()
wl_dependent_loss = OFDR.get_return_loss()
wl_dependent_group_delay = OFDR.get_group_delay()

plt.figure()
plt.plot(wl, wl_dependent_loss)
plt.grid()
plt.xlabel("Wavelength (nm)")
plt.ylabel("Wavlenght Dependent Loss (dB)")
plt.title("Spectral Analysis")
plt.tight_layout()
plt.show()


