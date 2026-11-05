# -*- coding: utf-8 -*-

"""
Created on Wed Sep 3 10:43:12 2025
Example of using Instrument.OFDR with Temperature / Strain analysis.

"""

import os
from datetime import datetime

# Adjust working directory (imports)
os.chdir("..")
from Instrument import Instrument
from matplotlib import pyplot as plt
import numpy as np
import time


def save_length_amplitude_txt(filename, length_data, amplitude_data):
    """Save Length vs Amplitude using the OFDR TXT pipe-delimited format."""
    length_data = np.asarray(length_data).reshape(-1)
    amplitude_data = np.asarray(amplitude_data).reshape(-1)

    if length_data.size != amplitude_data.size:
        raise ValueError(
            "Length and amplitude arrays must contain the same number of points: "
            f"{length_data.size} != {amplitude_data.size}"
        )

    with open(filename, "w", encoding="utf-8", newline="\n") as file:
        file.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        file.write("\nLength (m)|Amplitude (dB)\n")

        for length_value, amplitude_value in zip(length_data, amplitude_data):
            file.write(f"{length_value:.6f}|{amplitude_value:.3f}\n")


# Device connection parameters
HOST = "192.168.137.2"
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
OFDR.mode = "REFL"  # or TRANS

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

# Set group index (depends on fibre characteristics)
OFDR.group_index = 1.465
print("\n=== Applied configuration ===")
conf = OFDR.get_configuration()

# === Run reference measurement ===
print("\nExecuting single measurement...")
OFDR.single()
print("...waiting for measurement to complete...")
dev.OPC  # Wait for operation complete

print("\nRetrieving reference measurement data...")
reference_length = OFDR.get_length_axis()
reference_amplitude = OFDR.get_amplitude()

reference_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
reference_filename = f"OFDR_reference_{reference_timestamp}.txt"
save_length_amplitude_txt(
    reference_filename,
    reference_length,
    reference_amplitude,
)
print(f"Reference measurement saved to: {reference_filename}")

plt.figure()
plt.plot(reference_length, reference_amplitude)
plt.grid()
plt.xlabel("Length (m)")
plt.ylabel("Amplitude (dB)")
plt.title("OFDR Reference Measurement")
plt.tight_layout()
plt.show()

print("\nStoring measurement data as reference for analysis...")
OFDR.set_data_ref()
print(
    "Note: once data is stored as reference, it cannot be retrieved again "
    "using get_data commands."
)

# === Configure Temperature / Strain Analysis ===
print("\n=== Configuring Temperature / Strain analysis ===")

# Important: must run a measurement before configuring analysis
center_window = 0.8  # m
width = 0.5  # m
resolution = 1e-3  # m
OFDR.set_conf_temp_strain_analysis(
    center_window,
    width,
    resolution,
    coef_temp=7.0e-6,
    coef_strain=0.787,
    window_type="LENG",
)

# Get configuration
OFDR.get_conf_temp_strain_analysis()

# Wait for physical change (temperature or strain variation)
input("\nApply the change, then press Enter to continue...")
print("\nWaiting 5 seconds before second measurement...")
time.sleep(5)

# Make the second measurement
print("Execute second OFDR measurement")
OFDR.single()
print("...waiting for measurement to complete...")
dev.OPC

print("\nRetrieving second measurement data...")
measurement_length = OFDR.get_length_axis()
measurement_amplitude = OFDR.get_amplitude()

measurement_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
measurement_filename = f"OFDR_measurement_{measurement_timestamp}.txt"
save_length_amplitude_txt(
    measurement_filename,
    measurement_length,
    measurement_amplitude,
)
print(f"Second measurement saved to: {measurement_filename}")

print("Execute analysis")
OFDR.execute_temp_strain_analysis()
print("...waiting for analysis to complete...")
dev.OPC

print("\nRetrieving Temperature / Strain analysis results...")
spectral_shift = OFDR.get_spectral_shift()
temperature = OFDR.get_temperature()
strain = OFDR.get_strain()
quality = OFDR.get_quality()
# length_temp = OFDR.get_temp_strain_length_axis()

# Build the X-axis from the window, matched to the actual point count
n = len(strain)
length_axis = np.linspace(
    center_window - width / 2,
    center_window + width / 2,
    n,
)

# Unit conversions
strain_ue = np.array(strain) * 1e6
shift_ghz = np.array(spectral_shift) / 1e9

# Temperature
plt.figure()
plt.plot(length_axis, temperature)
plt.grid()
plt.xlabel("Length (m)")
plt.ylabel("Temperature shift (°C)")
plt.tight_layout()
plt.show()

# Strain
plt.figure()
plt.plot(length_axis, strain_ue)
plt.grid()
plt.xlabel("Length (m)")
plt.ylabel("Strain shift (µε)")
plt.tight_layout()
plt.show()

# Spectral shift
plt.figure()
plt.plot(length_axis, shift_ghz)
plt.grid()
plt.xlabel("Length (m)")
plt.ylabel("Spectral shift (GHz)")
plt.tight_layout()
plt.show()

# Existing CSV export of the strain analysis result
data = np.column_stack((length_axis, strain_ue))
np.savetxt(
    "strain_profile.csv",
    data,
    delimiter=",",
    header="Length,Strain_uE",
    comments="",
    fmt="%.6f",
)

# =============================================================================
# TROUBLESHOOTING NOTE - SCPI timeout while TCP connects
# =============================================================================
# Symptom: TCP connects (Test-NetConnection / TcpClient.Connect succeed), the
#          instrument GUI takes measurements fine, ping and shared folder work,
#          but SCPI commands (e.g. *IDN?) return no bytes and eventually time
#          out. A socket that OPENS but never ANSWERS is not a routing/firewall
#          issue (those refuse or drop the connection outright).
#
# Most likely cause: a stuck / locked SCPI session. These instruments often
#          allow only ONE remote-control client. If a previous run crashed or
#          was killed without releasing the socket, the server still thinks the
#          dead client owns the session, so new sockets are accepted at the TCP
#          layer but never serviced.
#   Fix:   Reboot the instrument (full restart, not just the software) to
#          release the orphaned session. Ensure no other script/tool holds 11111.
#
# Second cause: terminator mismatch on read. The reply may use \r\n while the
#          reader waits for \n (or vice-versa), so the read blocks until timeout.
#   Test:  send "*IDN?\r\n" instead of "*IDN?\n" and check if the ID returns.
#
# IMPORTANT - staying connected: do NOT add socket close() calls to "fix" this.
#          The session is intentionally kept open so subsequent measurements can
#          reuse the same connection. Only power-cycle the instrument to clear a
#          locked session; a healthy session should be left open.
# =============================================================================