# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 12:00:42 2025

@author: marest
"""


import socket
import time
from .common import query, send

class Instrument:
    """
    TCP/IP remote control of Apex instrument

    Parameters
    ----------
    IPaddress : str
        IP address of the equipment.
    PortNumber : int, optional
        Port number. The default is 21212.
    Simulation : bool, optional
        Indicates to the program if it has to run in simulation mode or not. The default is False.

    """
    def __init__(self, ip: str, port: int=21212, simulation: bool=False):
        """
        Constructor of the equipment.

        Parameters
        ----------
        IPaddress : str
            IP address of the equipment.
        PortNumber : int, optional
            Port number. The default is 21212.
        Simulation : bool, optional
            Indicates to the program if it has to run in simulation mode or not. The default is False.

        """

        self.__HOST = ip
        self.__PORT = port
        self.__SIMULATION = simulation
        self.__CONNECTED = False

        self.__open()

    def __open(self):
        """
        Open connexion to the equipment.
        This method is called by the constructor of the class
        """
        self.connexion = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
        self.connexion.settimeout(20.0)

        if self.__SIMULATION:
            self.__CONNECTED = True
            print("Connected successfully to the equipment")
        else:
            try:
                self.connexion.connect((self.__HOST, self.__PORT))
                self.__CONNECTED = True
                print("Connected successfully to the equipment")

            except Exception as e:
                raise ConnectionError(f"Impossible to connect to ({self.__HOST}, {self.__PORT})") from e

    def close(self):
        """
        Close connection to the equipment

        """

        if self.__SIMULATION:
            self.__CONNECTED = False
        else:
            try:
                self.connexion.close()
                self.__CONNECTED = False
            except Exception:
                raise ConnectionError(f"Impossible to reach ({self.__HOST}, {self.__PORT})")

        self.connexion.close()
        self.__CONNECTED = False
        print("Connection closed")

    @property
    def isconnected(self):
        """
        Returns the status of the connection. True if an equipment
        is connected, False otherwise.
        """
        return self.__CONNECTED

    @property
    def timeout(self):
        """
        Get the timeout of the Ethernet connection
        The returned value is expressed in seconds
        """

        timeout = self.connexion.gettimeout()
        return timeout


    @timeout.setter
    def timeout(self, timeout):
        """
        Set the timeout of the Ethernet connection
        TimeOut is expressed in seconds.
        """
        if not isinstance(timeout, (int, float)):
            raise TypeError("TimeOut should be int or float")

        self.connexion.settimeout(timeout)


    @property
    def IDN(self):
        """
        Return string ID of the equipment
        """
        if self.__SIMULATION:
            return "APEX-Technologies_Simulation_mode"
        else:
            ID = query(self.connexion, "*IDN?")
            return ID

    def OFDR(self):
        """
        Return an OFDR object for using the OFDR device
        """
        from .ofdr import OFDR
        return OFDR(self, self.__SIMULATION)

    def TLS(self):
        """
        Return a TLS object for using the Tunable Laser Source of the AP2XXX
        """
        from .tls import TunableLaser
        return TunableLaser(self, self.__SIMULATION)


    # TODO: add GetOpticalBand and Set in case of multiple laser instrument
    # def GetOpticalBand(self):
    #     '''
    #     Gets the actual optical band. The band can be:
    #         - O
    #         - C&L
    #     The optical band choice is only available for AP2X8X
    #     '''
    #     from random import randint

    #     if self.__Simulation:
    #         Bands = ["0", "C&L"]
    #         Band = Bands[randint(0, 1)]
    #     else:
    #         Send(self.Connexion, "CHBAND?\n")
    #         Band = Receive(self.Connexion)[:-1]
    #         Band = Band.replace("&&", "&")

    #     return Band


    # def SetOpticalBand(self, Band):
    #     '''
    #     Sets the optical band. The band can be:
    #     The available bands can be listed by the 'ListBands' command
    #     The optical band choice is only available for AP2X8X
    #     '''
    #     from PyApex.Constantes import APXXXX_ERROR_ARGUMENT_TYPE

    #     if not isinstance(Band, (str)):
    #         raise ApexError(APXXXX_ERROR_ARGUMENT_TYPE, "Band")

    #     ValidBands = self.ListBands()
    #     index = -1
    #     for vb in ValidBands:
    #         if Band.lower() == vb.lower():
    #             index = ValidBands.index(vb)

    #     if not self.__Simulation and index >= 0:
    #         Send(self.Connexion, "CHBAND" + str(index) + "\n")


    # =============================================================================
    #                       Standard SCPI commands
    # =============================================================================
    @property
    def OPC(self):
        """
        Operation complete query (block execution).

        Returns
        -------
        int
            Returns 1 when the instrument operation is complete

        """
        if not self.__SIMULATION:
            time.sleep(0.1)
            command = "*OPC?"
            self.connexion.settimeout(None)
            ans = int(query(self.connexion, command))
            self.connexion.settimeout(20)
            return ans

    # TODO: missing *OPC sans ? and *WAI to implement
    @property
    def ESE(self):
        """
        Event Status Enable query

        Returns
        -------
        int
            Returns an integer from 0 to 255, representing the Standard Status Enable Register.

        """
        if not self.__SIMULATION:
            command = "*ESE?"
            return int(query(self.connexion, command))

    @ESE.setter
    def ESE(self, value):
        """
        Event Status Enable command.

        Parameters
        ----------
        value : int
           Must be between 0 and 255 representing a mask for the event register bits.

        """
        if not isinstance(value, (int)):
            raise TypeError("Argmument should by int")

        if not self.__SIMULATION:
            command = "*ESE " + str(value)
            send(self.connexion, command)

    @property
    def ESR(self):
        """
        Standard Event Status Register Query

        Returns
        -------
        int
            Returns an integer from 0 to 255, representing the Standard Status Event Register.
            After reading, the register is reset.

        """
        if not self.__SIMULATION:
            command = "*ESR?"
            return int(query(self.connexion, command))

    @property
    def SRE(self):
        """
        Service Request Enable Query

        Returns
        -------
        int
            Returns an integer from 0 to 255, representing the Service Request Enable Register.

        """
        if not self.__SIMULATION:
            command = "*SRE?"
            return int(query(self.connexion, command))

    @SRE.setter
    def SRE(self, value):
        """
        Service Request Enable Command

        Parameters
        ----------
        value : int
            Must be between 0 and 255 representing a mask for the Service Request Enable register bits.
        """
        if not isinstance(value, (int)):
            raise TypeError("Argmument should by int")

        if not self.__SIMULATION:
            command = "*SRE " + str(value)
            send(self.connexion, command)

    @property
    def STB(self):
        """
        Read Status Byte Query

        Returns
        -------
        int
            Returns an integer from 0 to 255, representing the Status Bytes Register.

        """
        if not self.__SIMULATION:
            command = "*STB?"
            return int(query(self.connexion, command))

    def TST(self):
        """
        Self-Test Query. Runs a test to verify that everything is working correctly on the device.


        Returns
        -------
        int
            Returns 0 if everything is working correctly.

        """
        if not self.__SIMULATION:
            command = "*TST?"
            return int(query(self.connexion, command))

    def CLS(self):
        """
        Clear Status. Clears error/event queue, standard event register and status bytes register.

        """
        if not self.__SIMULATION:
            command = "*CLS"
            send(self.connexion, command)

    def RST(self):
        """
        Reset Command: Returns to a known configuration.
        This disables the internal laser, resets the OFDR configuration (mode, range, center, etc.).
        Registers are not affected.

        """
        if not self.__SIMULATION:
            command = "*RST"
            send(self.connexion, command)

    def system_error(self):
        """
        System Error Command. Returns error code if any

        Returns
        -------
        int
            Error Code.

        """
        if not self.__SIMULATION:
            command = "SYST:ERR?"
            return int(query(self.connexion, command))

    def system_version(self):
        """
        Return SCPI system version

        Returns
        -------
        int
            SCPI version.

        """
        if not self.__SIMULATION:
            command = "SYST:VERS?"
            return query(self.connexion, command)
