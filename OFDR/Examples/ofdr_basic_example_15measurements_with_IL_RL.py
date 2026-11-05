# -*- coding: utf-8 -*-
"""
Created on Wed Sep  3 10:05:21 2025
Example of using Instrument.OFDR.

This version automatically takes 15 consecutive measurements and:
- saves Length, Amplitude, Polar1 complex and Polar2 complex data for each
  measurement as a pipe-delimited TXT file;
- calculates insertion loss and return loss from the developer-provided
  integration algorithms;
- saves one CSV summary containing the analysis result for every measurement.
"""
import csv
import os
from datetime import datetime

os.chdir("..")

from Instrument import Instrument
from matplotlib import pyplot as plt
import numpy as np


# Number of consecutive measurements to take
N_MEASUREMENTS = 15

# Analysis zones in metres
INSERTION_LOSS_ZONE_1 = (1.447264, 1.448848)
INSERTION_LOSS_ZONE_2 = (1.501184, 1.503352)
RETURN_LOSS_ZONE = (1.450439, 1.451008)


def _as_1d(array, name):
    """Return instrument data as a one-dimensional NumPy array."""
    result = np.asarray(array).reshape(-1)
    if result.size == 0:
        raise ValueError(f"{name} contains no data.")
    return result


def _zone_indices(length_data, zone):
    """Return nearest start/stop indices, matching the developer examples."""
    start_m, stop_m = zone
    start_index = int(np.abs(length_data - start_m).argmin())
    stop_index = int(np.abs(length_data - stop_m).argmin())

    if start_index > stop_index:
        start_index, stop_index = stop_index, start_index
    if start_index == stop_index:
        raise ValueError(
            f"Zone {start_m:.6f} m to {stop_m:.6f} m contains no interval "
            "at the current length-axis sampling."
        )

    return start_index, stop_index


def calculate_insertion_loss_db(length_data, polar1, polar2):
    """Apply the developer-provided two-zone insertion-loss calculation."""
    zone_1_start, zone_1_stop = _zone_indices(
        length_data, INSERTION_LOSS_ZONE_1
    )
    zone_2_start, zone_2_stop = _zone_indices(
        length_data, INSERTION_LOSS_ZONE_2
    )

    polar1_power = np.abs(polar1) ** 2
    polar2_power = np.abs(polar2) ** 2

    result_1 = (
        np.sum(polar1_power[zone_1_start:zone_1_stop])
        + np.sum(polar2_power[zone_1_start:zone_1_stop])
    )
    result_2 = (
        np.sum(polar1_power[zone_2_start:zone_2_stop])
        + np.sum(polar2_power[zone_2_start:zone_2_stop])
    )

    if result_1 <= 0 or result_2 <= 0:
        raise ValueError("Insertion-loss integration produced non-positive power.")

    insertion_loss_linear = 0.5 * result_1 / result_2
    return float(10 * np.log10(insertion_loss_linear))


def calculate_return_loss_db(length_data, polar1, polar2):
    """Apply the developer-provided one-zone return-loss calculation."""
    zone_start, zone_stop = _zone_indices(length_data, RETURN_LOSS_ZONE)

    polar1_power = np.abs(polar1) ** 2
    polar2_power = np.abs(polar2) ** 2
    integrated_power = (
        np.sum(polar1_power[zone_start:zone_stop])
        + np.sum(polar2_power[zone_start:zone_stop])
    )

    if integrated_power <= 0:
        raise ValueError("Return-loss integration produced non-positive power.")

    return float(10 * np.log10(integrated_power))


def format_complex(value):
    """Format a complex128 value unambiguously for the TXT output."""
    return f"{value.real:.12e}{value.imag:+.12e}j"


def save_measurement_txt(
    filename,
    timestamp,
    length_data,
    amplitude_data,
    polar1,
    polar2,
):
    """Save all retrieved measurement arrays in pipe-delimited TXT format."""
    length_data = _as_1d(length_data, "Length")
    amplitude_data = _as_1d(amplitude_data, "Amplitude")
    polar1 = _as_1d(polar1, "Polar1 complex")
    polar2 = _as_1d(polar2, "Polar2 complex")

    sizes = {
        length_data.size,
        amplitude_data.size,
        polar1.size,
        polar2.size,
    }
    if len(sizes) != 1:
        raise ValueError(
            "Length, amplitude, Polar1 and Polar2 arrays must contain the "
            "same number of points."
        )

    with open(filename, "w", encoding="utf-8", newline="\n") as file:
        file.write(timestamp.strftime("%Y-%m-%d %H:%M:%S") + "\n")
        file.write("\n")
        file.write(
            "Length (m)|Amplitude (dB)|Polar1 complex|Polar2 complex\n"
        )

        for length_value, amplitude_value, polar1_value, polar2_value in zip(
            length_data,
            amplitude_data,
            polar1,
            polar2,
        ):
            file.write(
                f"{length_value:.6f}|{amplitude_value:.3f}|"
                f"{format_complex(polar1_value)}|"
                f"{format_complex(polar2_value)}\n"
            )


def save_analysis_csv(filename, analysis_rows):
    """Save the IL/RL result for every measurement, with zone metadata."""
    with open(filename, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Insertion loss zone 1 (m)",
            f"{INSERTION_LOSS_ZONE_1[0]:.6f} to "
            f"{INSERTION_LOSS_ZONE_1[1]:.6f}",
        ])
        writer.writerow([
            "Insertion loss zone 2 (m)",
            f"{INSERTION_LOSS_ZONE_2[0]:.6f} to "
            f"{INSERTION_LOSS_ZONE_2[1]:.6f}",
        ])
        writer.writerow([
            "Return loss zone (m)",
            f"{RETURN_LOSS_ZONE[0]:.6f} to {RETURN_LOSS_ZONE[1]:.6f}",
        ])
        writer.writerow([])
        writer.writerow(["Filename", "Insertion loss (dB)", "Return loss (dB)"])

        for filename_value, insertion_loss_db, return_loss_db in analysis_rows:
            writer.writerow([
                filename_value,
                f"{insertion_loss_db:.6f}",
                f"{return_loss_db:.6f}",
            ])


# === Device connection parameters ===
HOST = "192.168.137.2"
PORT = 11111

# Try to connect to the instrument
dev = Instrument(HOST, PORT, False)

# Create OFDR object from the instrument
OFDR = dev.OFDR()

# Display device identification
print("Device Identification number:")
print(dev.IDN)

# === Configure OFDR (once, before the loop) ===
print("\n=== Initial configuration (defaults) ===")
conf = OFDR.get_configuration()

# Set mode: REFL (reflection) or TRANS (transmission)
OFDR.mode = "REFL"  # or TRANS

# Select maximum length from available options
length_mode = OFDR.get_max_length_list()
print("\nOFDR length mode available:", length_mode)
OFDR.max_length = int(length_mode[0])

# Select span from available options
span_list = OFDR.get_span_list()
print("OFDR span available:", span_list)
OFDR.span = float(span_list[0])

# Set centre wavelength in nm
OFDR.center = 1575.0

# Select Fourier window (SQUA = square, HANN = Hann window)
OFDR.fourier_window = "SQUA"

# Set group index (depends on fibre characteristics)
OFDR.group_index = 1.465

print("\n=== Applied configuration ===")
conf = OFDR.get_configuration()

# === Run N_MEASUREMENTS consecutive measurements ===
run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
saved_files = []
analysis_rows = []

for i in range(1, N_MEASUREMENTS + 1):
    print(f"\n=== Measurement {i} of {N_MEASUREMENTS} ===")

    print("Executing single measurement...")
    OFDR.single()
    print("...waiting for measurement to complete...")
    dev.OPC  # Wait for operation complete

    print("Retrieving measurement data...")
    measurement_timestamp = datetime.now()
    length = _as_1d(OFDR.get_length_axis(), "Length")
    amp = _as_1d(OFDR.get_amplitude(), "Amplitude")
    polar1, polar2 = OFDR.get_complex_data()
    polar1 = _as_1d(polar1, "Polar1 complex")
    polar2 = _as_1d(polar2, "Polar2 complex")

    filename = f"OFDR_measurement_{run_timestamp}_{i:02d}.txt"
    save_measurement_txt(
        filename,
        measurement_timestamp,
        length,
        amp,
        polar1,
        polar2,
    )
    saved_files.append(filename)

    insertion_loss_db = calculate_insertion_loss_db(length, polar1, polar2)
    return_loss_db = calculate_return_loss_db(length, polar1, polar2)
    analysis_rows.append((filename, insertion_loss_db, return_loss_db))

    print(f"Saved: {filename}")
    print(f"Insertion loss: {insertion_loss_db:.4f} dB")
    print(f"Return loss: {return_loss_db:.4f} dB")

analysis_filename = f"OFDR_analysis_{run_timestamp}.csv"
save_analysis_csv(analysis_filename, analysis_rows)

print(f"\nDone. {len(saved_files)} measurements saved:")
for name in saved_files:
    print("  " + name)
print("Analysis summary saved: " + analysis_filename)

# === Display the last measurement (optional) ===
plt.figure()
plt.plot(length, amp)
plt.grid()
plt.xlabel("Length (m)")
plt.ylabel("Amplitude (dB)")
plt.title(f"OFDR Measurement {N_MEASUREMENTS} of {N_MEASUREMENTS}")
plt.tight_layout()
plt.show()
