# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 14:01:38 2025

@author: marest
"""

from .common import VACCUM_LIGHT_SPEED
import numpy as np

class TunableLaser():


    def __init__(self, equipment, simulation=False):
        '''
        Constructor of the TLS embedded in an equipment.
        Equipment is the Instrument class of the equipment
        Simulation is a boolean to indicate to the program if it has to run in simulation mode or not
        '''
        self.__connexion = equipment.connexion
        self.__SIMULATION = simulation
        self.__wait = 0.2 # wait between command

        # Variables and constants of the equipment
        self.__unit = "dBm"
        self.__valid_units = ["dbm", "mw"]

        self.__power = 0.0
        self.__wavelength = 1550.0
        self.__status = "OFF"
        self.__operation_complete = 1

        self.__start_wavelength = 1520.0
        self.__stop_wavelength = 1630.0
        self.__speed = 100
        self.__mode = 2
        self.__dwell_time = 0.0
        self.__cycle = 1
        self.__delay = 0.0
        self.__step_size = 0.01

    @property
    def __OPC(self):
        if not self.__SIMULATION:
            self.__connexion.settimeout(None)
            ans = int(self.__connexion.query("*OPC?"))
            self.__connexion.settimeout(20)
            return ans

    @property
    def unit(self):
        '''
        Get the power unit of the TLS equipment
        The return unit is a string
        '''
        return self.__unit

    @unit.setter
    def unit(self, unit):
        '''
        Set the power unit of the TLS equipment
        Unit is a string which could be "dBm" for logaritmic or "mW" for linear power
        '''

        try:
            unit = str(unit)
        except:
            raise TypeError("Argument should be str 'dBm' ou 'mW'")
        else:
            if unit.lower() in self.__valid_units:
                self.__unit = unit

    @property
    def power(self):
        '''
        Get the power of the TLS equipment
        The returned power is expressed in the unit defined by the GetUnit() method
        '''

        if not self.__SIMULATION:
            self.__OPC
            power = float(self.__connexion.query("SOURce:POWer?", self.__wait))

            if self.__unit.lower() == "mw":
                power = 10.0**(power / 10.0)

            self.__power = power

        return self.__power

    @power.setter
    def power(self, power):
        '''
        Set the power of the TLS equipment
        The power is expressed in the unit defined by the GetUnit() method
        '''

        if not isinstance(power, (int, float)):
            raise TypeError("Argument should be int or float")

        if self.__unit.lower() == "mw":
            power = 10.0 * np.log10(power)
        self.__power = power

        if not self.__SIMULATION:
            self.__OPC
            self.__connexion.send("SOURce:POWer " + str("%.1f" % self.__power), self.__wait)

    @property
    def wavelength(self):
        '''
        Get the static wavelength of the TLS equipment
        The wavelength is expressed in nm
        '''

        if not self.__SIMULATION:
            self.__OPC
            wavelength = float(self.__connexion.query("SOURce:WAVelength?", self.__wait))

            self.__wavelength = wavelength

        return self.__wavelength

    @wavelength.setter
    def wavelength(self, wavelength):
        '''
        Set the static wavelength of the TLS equipment
        The wavelength is expressed in nm
        '''
        if not isinstance(wavelength, (int, float)):
            raise TypeError("Argument should be int or float")

        self.__wavelength = wavelength

        if not self.__SIMULATION:
            self.__OPC
            self.__connexion.send("SOURce:WAVelength " + str("%.3f" % self.__wavelength), self.__wait)

    @property
    def frequency(self):
        '''
        Get the static frequency of the TLS equipment
        The frequency is expressed in GHz
        '''
        if self.__SIMULATION:
            frequency = VACCUM_LIGHT_SPEED / self.__wavelength
        else:
            self.__OPC
            wavelength = float(self.__connexion.query("SOURce:WAVelength?", self.__wait))

            frequency = VACCUM_LIGHT_SPEED / wavelength
            self.__wavelength = wavelength

        return frequency

    @frequency.setter
    def frequency(self, frequency):
        '''
        Set the static frequency of the TLS equipment
        The frequency is expressed in GHz
        '''

        if not isinstance(frequency, (int, float)):
            raise TypeError("Argument should be int or float")

        self.__wavelength = VACCUM_LIGHT_SPEED / frequency

        if not self.__SIMULATION:
            self.__OPC
            self.__connexion.send("SOURce:WAVelength " + str("%.3f" % self.__wavelength), self.__wait)


    def on(self):
        '''
        Switch on the output power of TLS equipment
        '''

        if not self.__SIMULATION:
            self.__OPC
            self.__connexion.send("OUTPut 1", self.__wait)

        self.__status = "ON"


    def off(self):
        '''
        Switch off the output power of the TLS equipment
        '''

        if not self.__SIMULATION:
            self.__OPC
            self.__connexion.send("OUTPut 0", self.__wait)

        self.__status = "OFF"


    @property
    def status(self):
        '''
        Return the status ("ON" or "OFF") of the TLS equipment
        '''

        if not self.__SIMULATION:
            self.__OPC
            status = int(self.__connexion.query("OUTPut?", self.__wait))

            if status == 1:
                self.__status = "ON"
            else:
                self.__status = "OFF"

        return self.__status


    def operation_complete(self):
        '''
        Blocking method : return 1 after all laser operation are complete.
        '''

        if not self.__SIMULATION:
            self.__OPC

        return self.__operation_complete

    @property
    def start_wavelength(self):
        '''
        Get the start wavelength of the continuous sweep
        Wavelength is expressed in nm
        '''

        if not self.__SIMULATION:
            self.__OPC
            self.__start_wavelength = float(self.__connexion.query("SOURce:WAVelength:SWEep:STARt?", self.__wait))

        return self.__start_wavelength

    @start_wavelength.setter
    def start_wavelength(self, wavelength):
        '''
        Set the start wavelength of the continuous sweep
        Wavelength is expressed in nm
        '''

        if not isinstance(wavelength, (float, int)):
            raise TypeError("Argument should be int or float")

        if not self.__SIMULATION:
            self.__OPC
            self.__connexion.send("SOURce:WAVelength:SWEep:STARt " + str("%.3f" % wavelength), self.__wait)

        self.__start_wavelength = wavelength


    @property
    def start_frequency(self):
        '''
        Get the start frequency of the continuous sweep
        frequency is expressed in GHz
        '''

        if not self.__SIMULATION:
            self.__OPC
            self.__start_wavelength = float(self.__connexion.query("SOURce:WAVelength:SWEep:STARt?", self.__wait))

        return VACCUM_LIGHT_SPEED / self.__start_wavelength

    @start_frequency.setter
    def start_frequency(self, frequency):
        '''
        Set the start frequency of the continuous sweep
        Frequency is expressed in GHz
        '''

        if not isinstance(frequency, (float, int)):
            raise TypeError("Argument should be int or float")

        self.__start_wavelength = VACCUM_LIGHT_SPEED / frequency

        if not self.__SIMULATION:
            self.__OPC
            self.__connexion.send("SOURce:WAVelength:SWEep:STARt " + str("%.3f" % self.__start_wavelength), self.__wait)

    @property
    def stop_wavelength(self):
        '''
        Get the stop wavelength of the continuous sweep
        Wavelength is expressed in nm
        '''

        if not self.__SIMULATION:
            self.__OPC
            self.__stop_wavelength = float(self.__connexion.query("SOURce:WAVelength:SWEep:STOP?", self.__wait))

        return self.__stop_wavelength

    @stop_wavelength.setter
    def stop_wavelength(self, wavelength):
        '''
        Set the stop wavelength of the continuous sweep
        Wavelength is expressed in nm
        '''

        if not isinstance(wavelength, (float, int)):
            raise TypeError("Argument should be int or float")

        if not self.__SIMULATION:
            self.__OPC
            self.__connexion.send("SOURce:WAVelength:SWEep:STOP " + str("%.3f" % wavelength), self.__wait)

        self.__stop_wavelength = wavelength


    @property
    def stop_frequency(self):
        '''
        Get the stop frequency of the continuous sweep
        frequency is expressed in GHz
        '''

        if not self.__SIMULATION:
            self.__OPC
            self.__stop_wavelength = float(self.__connexion.query("SOURce:WAVelength:SWEep:STOP?", self.__wait))

        return VACCUM_LIGHT_SPEED / self.__stop_wavelength

    @stop_frequency.setter
    def stop_frequency(self, frequency):
        '''
        Set the stop frequency of the continuous sweep
        Frequency is expressed in GHz
        '''

        if not isinstance(frequency, (float, int)):
            raise TypeError("Argument should be int or float")

        self.__stop_wavelength = VACCUM_LIGHT_SPEED / frequency

        if not self.__SIMULATION:
            self.__OPC
            self.__connexion.send("SOURce:WAVelength:SWEep:STOP " + str("%.3f" % self.__stop_wavelength), self.__wait)


    @property
    def speed(self):
        '''
        Get the laser speed for the continuous sweep
        Speed is expressed in nm/s
        '''

        if not self.__SIMULATION:
            self.__OPC
            self.__speed = float(self.__connexion.query("SOURce:WAVelength:SWEep:SPEed?", self.__wait))

        return self.__speed

    @speed.setter
    def speed(self, speed):
        '''
        Set the laser speed for the continuous sweep
        Speed is expressed in nm/s
        '''

        if not isinstance(speed, (float, int)):
            raise TypeError("Argument should be int or float")

        self.__speed = round(speed)

        if not self.__SIMULATION:
            self.__OPC
            self.__connexion.send("SOURce:WAVelength:SWEep:SPEed " + str("%i" % self.__speed), self.__wait)


    def start_sweep(self):
        """
        Initiate a continuous single sweep.
        """
        if not self.__SIMULATION:
            self.__OPC
            self.__connexion.send("SOURce:WAVelength:SWEep:EXECute 1", self.__wait)
        else:
            print("Sweeping")

    def stop_sweep(self):
        """
        Stop the continuous sweep.
        Does not call __OPC so it can interrupt a running sweep.
        """
        if not self.__SIMULATION:
            self.__connexion.send("SOURce:WAVelength:SWEep:EXECute 0", self.__wait)
        else:
            print("Stop sweep")

    def abort(self):
        """
        Abort any running sweep (alias for stop_sweep using ABORt SCPI command).
        Does not call __OPC so it can interrupt a running sweep.
        """
        if not self.__SIMULATION:
            self.__connexion.send("ABORt", self.__wait)

    # =========================================================================
    #                       Sweep mode
    # =========================================================================

    VALID_MODES = {0: "static", 1: "auto_step", 2: "continuous"}

    @property
    def mode(self):
        '''
        Get the scan mode of the TLS.

        Returns
        -------
        int
            0 = static, 1 = auto step, 2 = continuous
        '''
        if not self.__SIMULATION:
            self.__OPC
            self.__mode = int(self.__connexion.query("SOURce:WAVelength:SWEep:MODE?", self.__wait))
        return self.__mode

    @mode.setter
    def mode(self, mode):
        '''
        Set the scan mode of the TLS.

        Parameters
        ----------
        mode : int
            0 = static, 1 = auto step, 2 = continuous
        
        Raises
        ------
        TypeError
            If mode is not an int.
        ValueError
            If mode is not 0, 1 or 2.
        '''
        if not isinstance(mode, int):
            raise TypeError("Argument should be int")
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid mode {mode}. Valid modes: {self.VALID_MODES}")

        self.__mode = mode

        if not self.__SIMULATION:
            self.__OPC
            self.__connexion.send("SOURce:WAVelength:SWEep:MODE " + str(mode), self.__wait)

    @property
    def dwell_time(self):
        '''
        Get the dwell time.
        In continuous mode: time between multiple sweeps.
        In auto step mode: time between steps.
        Expressed in seconds.
        '''
        if not self.__SIMULATION:
            self.__OPC
            self.__dwell_time = float(self.__connexion.query("SOURce:WAVelength:SWEep:DWELl?", self.__wait))
        return self.__dwell_time

    @dwell_time.setter
    def dwell_time(self, dwell_time):
        '''
        Set the dwell time.
        Expressed in seconds.
        '''
        if not isinstance(dwell_time, (int, float)):
            raise TypeError("Argument should be int or float")

        self.__dwell_time = float(dwell_time)

        if not self.__SIMULATION:
            self.__OPC
            self.__connexion.send("SOURce:WAVelength:SWEep:DWELl " + str("%.3f" % self.__dwell_time), self.__wait)

    @property
    def cycle(self):
        '''
        Get the number of sweep cycles.
        '''
        if not self.__SIMULATION:
            self.__OPC
            self.__cycle = int(self.__connexion.query("SOURce:WAVelength:SWEep:CYCLe?", self.__wait))
        return self.__cycle

    @cycle.setter
    def cycle(self, cycle):
        '''
        Set the number of sweep cycles.

        Parameters
        ----------
        cycle : int
            Number of cycles (>= 1).
        '''
        if not isinstance(cycle, int):
            raise TypeError("Argument should be int")

        self.__cycle = cycle

        if not self.__SIMULATION:
            self.__OPC
            self.__connexion.send("SOURce:WAVelength:SWEep:CYCLe " + str(cycle), self.__wait)

    @property
    def cycle_remaining(self):
        '''
        Get the number of sweep cycles remaining (query only).
        '''
        if not self.__SIMULATION:
            self.__OPC
            return int(self.__connexion.query("SOURce:WAVelength:SWEep:COUNt?", self.__wait))
        return 0

    @property
    def delay(self):
        '''
        Get the delay time between single sweeps.
        Expressed in seconds.
        '''
        if not self.__SIMULATION:
            self.__OPC
            self.__delay = float(self.__connexion.query("SOURce:WAVelength:SWEep:DELay?", self.__wait))
        return self.__delay

    @delay.setter
    def delay(self, delay):
        '''
        Set the delay time between single sweeps.
        Expressed in seconds.
        '''
        if not isinstance(delay, (int, float)):
            raise TypeError("Argument should be int or float")

        self.__delay = float(delay)

        if not self.__SIMULATION:
            self.__OPC
            self.__connexion.send("SOURce:WAVelength:SWEep:DELay " + str("%.3f" % self.__delay), self.__wait)

    @property
    def step_size(self):
        '''
        Get the step size for step scan mode.
        Expressed in nm.
        '''
        if not self.__SIMULATION:
            self.__OPC
            self.__step_size = float(self.__connexion.query("SOURce:WAVelength:SWEep:STEP?", self.__wait))
        return self.__step_size

    @step_size.setter
    def step_size(self, step_size):
        '''
        Set the step size for step scan mode.
        Expressed in nm.
        '''
        if not isinstance(step_size, (int, float)):
            raise TypeError("Argument should be int or float")

        self.__step_size = float(step_size)

        if not self.__SIMULATION:
            self.__OPC
            self.__connexion.send("SOURce:WAVelength:SWEep:STEP " + str("%.3f" % self.__step_size), self.__wait)

    # =========================================================================
    #                       Hardware limits (query only)
    # =========================================================================

    @property
    def min_wavelength(self):
        '''
        Get the minimum settable wavelength (nm).
        '''
        if not self.__SIMULATION:
            self.__OPC
            return float(self.__connexion.query("SOURce:WAVelength:MIN?", self.__wait))
        return self.__start_wavelength

    @property
    def max_wavelength(self):
        '''
        Get the maximum settable wavelength (nm).
        '''
        if not self.__SIMULATION:
            self.__OPC
            return float(self.__connexion.query("SOURce:WAVelength:MAX?", self.__wait))
        return self.__stop_wavelength

    @property
    def min_power(self):
        '''
        Get the minimum settable power (dBm).
        '''
        if not self.__SIMULATION:
            self.__OPC
            return float(self.__connexion.query("SOURce:POWer:MIN?", self.__wait))
        return 0.0

    @property
    def max_power(self):
        '''
        Get the maximum settable power (dBm).
        '''
        if not self.__SIMULATION:
            self.__OPC
            return float(self.__connexion.query("SOURce:POWer:MAX?", self.__wait))
        return 10.0

    @property
    def min_step_size(self):
        '''
        Get the minimum step size (nm).
        '''
        if not self.__SIMULATION:
            self.__OPC
            return float(self.__connexion.query("SOURce:WAVelength:SWEep:STEP:MIN?", self.__wait))
        return 0.01

    @property
    def min_scan_range(self):
        '''
        Get the minimum scan range (nm).
        '''
        if not self.__SIMULATION:
            self.__OPC
            return float(self.__connexion.query("SOURce:WAVelength:SWEep:RANGe:MIN?", self.__wait))
        return 0.01

    @property
    def max_scan_range(self):
        '''
        Get the maximum scan range (nm).
        '''
        if not self.__SIMULATION:
            self.__OPC
            return float(self.__connexion.query("SOURce:WAVelength:SWEep:RANGe:MAX?", self.__wait))
        return self.__stop_wavelength - self.__start_wavelength

    # =========================================================================
    #                       Trigger
    # =========================================================================

    @property
    def trigger_out_type(self):
        '''
        Get the trigger output type.

        Returns
        -------
        str
            "SYNC" or "ETALON"
        '''
        if not self.__SIMULATION:
            self.__OPC
            return self.__connexion.query("TRIGger:OUTput:TYPE?", self.__wait).strip()
        return "SYNC"

    @trigger_out_type.setter
    def trigger_out_type(self, trig_type):
        '''
        Set the trigger output type.

        Parameters
        ----------
        trig_type : str
            "SYNC" or "ETALON"
        '''
        if not isinstance(trig_type, str):
            raise TypeError("Argument should be str ('SYNC' or 'ETALON')")

        if not self.__SIMULATION:
            self.__OPC
            self.__connexion.send("TRIGger:OUTput:TYPE " + trig_type.upper(), self.__wait)

    @property
    def trigger_out_polarity(self):
        '''
        Get the trigger output polarity.

        Returns
        -------
        int
            0 = negative, 1 = positive
        '''
        if not self.__SIMULATION:
            self.__OPC
            return int(self.__connexion.query("TRIGger:OUTput:POLarity?", self.__wait))
        return 1

    @trigger_out_polarity.setter
    def trigger_out_polarity(self, polarity):
        '''
        Set the trigger output polarity.

        Parameters
        ----------
        polarity : int
            0 = negative, 1 = positive
        '''
        if not isinstance(polarity, int):
            raise TypeError("Argument should be int (0 or 1)")

        if not self.__SIMULATION:
            self.__OPC
            self.__connexion.send("TRIGger:OUTput:POLarity " + str(polarity), self.__wait)

    @property
    def trigger_in_status(self):
        '''
        Get the trigger input status.

        Returns
        -------
        int
            0 = disabled, 1 = enabled
        '''
        if not self.__SIMULATION:
            self.__OPC
            return int(self.__connexion.query("TRIGger:INput:STATus?", self.__wait))
        return 0

    @trigger_in_status.setter
    def trigger_in_status(self, status):
        '''
        Set the trigger input status.

        Parameters
        ----------
        status : int
            0 = disabled, 1 = enabled
        '''
        if not isinstance(status, int):
            raise TypeError("Argument should be int (0 or 1)")

        if not self.__SIMULATION:
            self.__OPC
            self.__connexion.send("TRIGger:INput:STATus " + str(status), self.__wait)

    @property
    def trigger_in_polarity(self):
        '''
        Get the trigger input polarity.

        Returns
        -------
        int
            0 = negative, 1 = positive
        '''
        if not self.__SIMULATION:
            self.__OPC
            return int(self.__connexion.query("TRIGger:INput:POLarity?", self.__wait))
        return 0

    @trigger_in_polarity.setter
    def trigger_in_polarity(self, polarity):
        '''
        Set the trigger input polarity.

        Parameters
        ----------
        polarity : int
            0 = negative, 1 = positive
        '''
        if not isinstance(polarity, int):
            raise TypeError("Argument should be int (0 or 1)")

        if not self.__SIMULATION:
            self.__OPC
            self.__connexion.send("TRIGger:INput:POLarity " + str(polarity), self.__wait)

    # =========================================================================
    #                       Calibration
    # =========================================================================

    def wavelength_calibration(self):
        '''
        Run a wavelength self-calibration (*TST? command).

        Returns
        -------
        int
            0 if calibration succeeded, 1 if failed.
        '''
        if not self.__SIMULATION:
            self.__OPC
            self.__connexion.settimeout(None)
            result = int(self.__connexion.query("*TST?"))
            self.__connexion.settimeout(20)
            return result
        return 0
