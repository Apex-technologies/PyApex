# -*- coding: utf-8 -*-
"""
Created on Wed Sep  3 10:43:12 2025


Example of using Instrument.OFDR with Temperature / Strain analysis.

This script demonstrates how to:
1. Connect to the device
2. Configure and run a basic OFDR measurement
3. Store reference data for analysis
4. Configure and run temperature/strain analysis
5. Retrieve and plot the results
"""

import os

# adjust working directory (imports)
os.chdir("..")

from Instrument import Instrument
from matplotlib import pyplot as plt
import time


# Device connection parameters
HOST = "192.168.1.119"
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

# === Retrieve data if needed ===
print("\nRetrieving measurement data...")
length = OFDR.get_length_axis()
amp = OFDR.get_amplitude()

plt.figure()
plt.plot(length, amp)
plt.grid()
plt.xlabel("Length (m)")
plt.ylabel("Amplitude (dB)")
plt.title("OFDR Reference Measurement")
plt.tight_layout()
plt.show()

print("\nStoring measurement data as reference for analysis...")
OFDR.set_data_ref() # be careful, once in ref, if an other single is performed data can not be retreived using get_data commands
print("Note: once data is stored as reference, it cannot be retrieved again using get_data commands.")

# === Configure Temperature / Strain Analysis ===
print("\n=== Configuring Temperature / Strain analysis ===")
# Important: must run a measurement before configuring analysis
center_window = 1.0 # m
width = 0.2 # m
resolution = 1e-2 # m

OFDR.set_conf_temp_strain_analysis(center_window, width, resolution,
                                   coef_temp=7.0e-6, coef_strain=0.787,
                                   window_type="LENG")

# get configuration
OFDR.get_conf_temp_strain_analysis()


# Wait for physical change (temperature or strain variation)
print("\nWaiting 5 seconds before second measurement...")
time.sleep(5)

# We make the second measurement
print("Execute second OFDR measurement")
OFDR.single()

print("...waiting for measurement to complete...")
dev.OPC

print("Execute analysis")
OFDR.execute_temp_strain_analysis()

print("...waiting for analysis to complete...")
dev.OPC

print("\nRetrieving Temperature / Strain analysis results...")
spectral_shift = OFDR.get_spectral_shift()
temperature = OFDR.get_temperature()
strain = OFDR.get_strain()
quality = OFDR.get_quality()

length_temp = OFDR.get_temp_strain_length_axis()


plt.figure()
plt.plot(length_temp, temperature)
plt.grid()
plt.grid()
plt.xlabel("Length (m)")
plt.ylabel("Temperature shift (°C)")
plt.tight_layout()
plt.show()
