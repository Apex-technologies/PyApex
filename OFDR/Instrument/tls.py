# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 14:01:38 2025

@author: marest
"""

from .common import send, query, VACCUM_LIGHT_SPEED
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
        self.__validUnits = ["dbm", "mw"]

        self.__power = 0.0
        self.__wavelength = 1550.0
        self.__status = "OFF"
        self.__operation_complete = 1

        self.__start_wavelength = 1520.0
        self.__stop_wavelength = 1630.0
        self.__speed = 100

    @property
    def __OPC(self):
        if not self.__SIMULATION:
            command = "*OPC?"
            self.__connexion.settimeout(None)
            ans = int(query(self.__connexion, command))
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
            if unit.lower() in self.__ValidUnits:
                self.__unit = unit

    @property
    def power(self):
        '''
        Get the power of the TLS equipment
        The returned power is expressed in the unit defined by the GetUnit() method
        '''

        if not self.__SIMULATION:
            self.__OPC
            command = "SOURce:POWer?"
            power = float(query(self.__connexion, command, self.__wait))

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
            command = "SOURce:POWer " + str("%.1f" % self.__power)
            send(self.__connexion, command, self.__wait)

    @property
    def wavelength(self):
        '''
        Get the static wavelength of the TLS equipment
        The wavelength is expressed in nm
        '''

        if not self.__SIMULATION:
            self.__OPC
            Command = "SOURce:WAVelength?"
            wavelength = float(query(self.__connexion, Command, self.__wait))

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
            command = "SOURce:WAVelength " + str("%.3f" %self.__wavelength)
            send(self.__connexion, command, self.__wait)

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
            Command = "SOURce:WAVelength?"
            wavelength = float(query(self.__connexion, Command, self.__wait))

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
            command = "SOURce:WAVelength " + str("%.3f" % self.__wavelength)
            send(self.__connexion, command, self.__wait)


    def on(self):
        '''
        Switch on the output power of TLS equipment
        '''

        if not self.__SIMULATION:
            self.__OPC
            command = "OUTPut 1"
            send(self.__connexion, command, self.__wait)

        self.__status = "ON"


    def off(self):
        '''
        Switch off the output power of the TLS equipment
        '''

        if not self.__SIMULATION:
            self.__OPC
            command = "OUTPut 0"
            send(self.__connexion, command, self.__wait)

        self.__status = "OFF"


    @property
    def status(self):
        '''
        Return the status ("ON" or "OFF") of the TLS equipment
        '''

        if not self.__SIMULATION:
            self.__OPC
            command = "OUTPut?"
            status = int(query(self.__connexion, command, self.__wait))

            if status == 1:
                self.__Status = "ON"
            else:
                self.__Status = "OFF"

        return self.__Status


    def operation_complete(self):
        '''
        Blocking method : return 1 after all laser operation are complete.

        '''

        if not self.__SIMULATION:
            self.__OPC
            command = "SOURce:OPC?"
            opc = query(self.__connexion, command, self.__wait)

            self.__operation_complete = opc

        return self.__operation_complete

    @property
    def start_wavelength(self):
        '''
        Get the start wavelength of the continuous sweep
        Wavelength is expressed in nm
        '''

        if not self.__SIMULATION:
            self.__OPC
            command = "SOURce:WAVelength:SWEep:STARt?"
            self.__start_wavelength = float(query(self.__connexion, command, self.__wait))

        return self.__start_wavelength

    @start_wavelength.setter
    def start_wavelength(self, wavelength):
        '''
        Set the start wavelength of the continuous sweep
        Wavelength is expressed in nm
        '''

        if not isinstance(wavelength, (float, int)):
            raise TypeError("Argmument should by int or float")

        if not self.__SIMULATION:
            self.__OPC
            command = "SOURce:WAVelength:SWEep:STARt " + str("%.3f" % wavelength)
            send(self.__connexion, command, self.__wait)

        self.__start_wavelength = wavelength


    @property
    def start_frequency(self):
        '''
        Get the start frequency of the continuous sweep
        frequency is expressed in GHz
        '''

        if not self.__SIMULATION:
            self.__OPC
            command = "SOURce:WAVelength:SWEep:STARt?"
            self.__start_wavelength = float(query(self.__connexion, command, self.__wait))

        return VACCUM_LIGHT_SPEED / self.__start_wavelength

    @start_frequency.setter
    def start_frequency(self, frequency):
        '''
        Set the start frequency of the continuous sweep
        Wavelength is expressed in GHz
        '''

        if not isinstance(frequency, (float, int)):
            raise TypeError("Argmument should by int or float")

        self.__start_wavelength = VACCUM_LIGHT_SPEED / frequency

        if not self.__SIMULATION:
            self.__OPC
            command = "SOURce:WAVelength:SWEep:STARt " + str("%.3f" % self.__start_wavelength)
            send(self.__connexion, command, self.__wait)

    @property
    def stop_wavelength(self):
        '''
        Get the start wavelength of the continuous sweep
        Wavelength is expressed in nm
        '''

        if not self.__SIMULATION:
            self.__OPC
            command = "SOURce:WAVelength:SWEep:STOP?"
            self.__stop_wavelength = float(query(self.__connexion, command, self.__wait))

        return self.__stop_wavelength

    @stop_wavelength.setter
    def stop_wavelength(self, wavelength):
        '''
        Set the start wavelength of the continuous sweep
        Wavelength is expressed in nm
        '''

        if not isinstance(wavelength, (float, int)):
            raise TypeError("Argmument should by int or float")

        if not self.__SIMULATION:
            self.__OPC
            command = "SOURce:WAVelength:SWEep:STOP " + str("%.3f" % wavelength)
            send(self.__connexion, command, self.__wait)

        self.__stop_wavelength = wavelength


    @property
    def stop_frequency(self):
        '''
        Get the start frequency of the continuous sweep
        frequency is expressed in GHz
        '''

        if not self.__SIMULATION:
            self.__OPC
            command = "SOURce:WAVelength:SWEep:STOP?"
            self.__stop_wavelength = float(query(self.__connexion, command, self.__wait))

        return VACCUM_LIGHT_SPEED / self.__stop_wavelength

    @stop_frequency.setter
    def stop_frequency(self, frequency):
        '''
        Set the start frequency of the continuous sweep
        Wavelength is expressed in GHz
        '''

        if not isinstance(frequency, (float, int)):
            raise TypeError("Argmument should by int or float")

        self.__stop_wavelength = VACCUM_LIGHT_SPEED / frequency

        if not self.__SIMULATION:
            self.__OPC
            command = "SOURce:WAVelength:SWEep:STOP " + str("%.3f" % self.__stop_wavelength)
            send(self.__connexion, command, self.__wait)


    @property
    def speed(self):
        '''
        Get the laser speed for the continuous sweep
        Speed is expressed in nm/s
        '''

        if not self.__SIMULATION:
            self.__OPC
            command = "SOURce:WAVelength:SWEep:SPEep?"
            self.__speed = float(query(self.__connexion, command, self.__wait))

        return self.__speed

    @speed.setter
    def speed(self, speed):
        '''
        Set the laser speed for the continuous sweep
        Speed is expressed in nm/s
        '''

        if not isinstance(speed, (float, int)):
            raise TypeError("Argmument should by int or float")

        self.__speed = round(speed)

        if not self.__SIMULATION:
            self.__OPC
            command = "SOURce:WAVelength:SWEep:SPEep " + str("%i" % self.__speed)
            send(self.__connexion, command, self.__wait)


    def start_sweep(self):
        """
        Initiate a continuous single sweep

        None.

        """
        if not self.__SIMULATION:
            self.__OPC
            command = "SOURce:WAVelength:SWEep:EXECute 1"
            send(self.__connexion, command, self.__wait)
        else:
            print("Sweeping")

    def stop_sweep(self):
        """
        Stop the continuous sweep

        """
        if not self.__SIMULATION:
            self.__OPC
            command = "SOURce:WAVelength:SWEep:EXECute 0"
            send(self.__connexion, command, self.__wait)
        else:
            print("Stop sweep")
