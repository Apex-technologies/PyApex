# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 12:00:42 2025

@author: marest
"""

import time
from .common import TCPTransport, SerialTransport


class Instrument:
    """
    Remote control of Apex instrument via TCP/IP or RS232.

    Parameters
    ----------
    ip : str, optional
        IP address for TCP/IP connection.
    port : int, optional
        TCP port number. The default is 21212.
    com_port : str, optional
        Serial port name for RS232 connection (e.g. 'COM3').
    baudrate : int, optional
        Serial baud rate. The default is 115200.
    simulation : bool, optional
        If True, run in simulation mode. The default is False.

    Examples
    --------
    TCP/IP connection::

        instrument = Instrument(ip="192.168.1.100", port=21212)

    RS232 connection::

        instrument = Instrument(com_port="COM3", baudrate=115200)

    """

    def __init__(self, ip: str = None, port: int = 21212,
                 com_port: str = None, baudrate: int = 115200,
                 simulation: bool = False):

        self.__SIMULATION = simulation
        self.__CONNECTED = False

        if simulation:
            self.connexion = None
            self.__CONNECTED = True
            print("Connected successfully to the equipment (simulation)")

        elif com_port is not None:
            try:
                self.connexion = SerialTransport(com_port, baudrate)
                self.__CONNECTED = True
                print(f"Connected successfully via RS232 ({com_port})")
            except Exception as e:
                raise ConnectionError(f"Impossible to connect to serial port {com_port}") from e

        elif ip is not None:
            try:
                self.connexion = TCPTransport(ip, port)
                self.__CONNECTED = True
                print(f"Connected successfully via TCP/IP ({ip}:{port})")
            except Exception as e:
                raise ConnectionError(f"Impossible to connect to ({ip}, {port})") from e

        else:
            raise ValueError("Provide 'ip' for TCP/IP or 'com_port' for RS232 connection")

    def close(self):
        """
        Close connection to the equipment.
        """
        if self.connexion is not None:
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
        Get the connection timeout.
        The returned value is expressed in seconds.
        """
        if self.connexion is not None:
            return self.connexion.settimeout
        return None

    @timeout.setter
    def timeout(self, timeout):
        """
        Set the connection timeout.
        TimeOut is expressed in seconds.
        """
        if not isinstance(timeout, (int, float, type(None))):
            raise TypeError("TimeOut should be int, float or None")

        if self.connexion is not None:
            self.connexion.settimeout(timeout)

    @property
    def IDN(self):
        """
        Return string ID of the equipment.
        """
        if self.__SIMULATION:
            return "APEX-Technologies_Simulation_mode"
        else:
            return self.connexion.query("*IDN?")

    def TLS(self):
        """
        Return a TLS object for using the Tunable Laser Source of the AP2XXX.
        """
        from .tls import TunableLaser
        return TunableLaser(self, self.__SIMULATION)

    # =============================================================================
    #                       Standard SCPI commands
    # =============================================================================
    @property
    def OPC(self):
        """
        Operation complete query (blocking).

        Returns
        -------
        int
            Returns 1 when the instrument operation is complete.

        """
        if not self.__SIMULATION:
            time.sleep(0.1)
            self.connexion.settimeout(None)
            ans = int(self.connexion.query("*OPC?"))
            self.connexion.settimeout(20)
            return ans

    @property
    def ESE(self):
        """
        Event Status Enable query.

        Returns
        -------
        int
            Returns an integer from 0 to 255, representing the Standard Status Enable Register.

        """
        if not self.__SIMULATION:
            return int(self.connexion.query("*ESE?"))

    @ESE.setter
    def ESE(self, value):
        """
        Event Status Enable command.

        Parameters
        ----------
        value : int
           Must be between 0 and 255 representing a mask for the event register bits.

        """
        if not isinstance(value, int):
            raise TypeError("Argument should be int")

        if not self.__SIMULATION:
            self.connexion.send("*ESE " + str(value))

    @property
    def ESR(self):
        """
        Standard Event Status Register Query.

        Returns
        -------
        int
            Returns an integer from 0 to 255, representing the Standard Status Event Register.
            After reading, the register is reset.

        """
        if not self.__SIMULATION:
            return int(self.connexion.query("*ESR?"))

    @property
    def SRE(self):
        """
        Service Request Enable Query.

        Returns
        -------
        int
            Returns an integer from 0 to 255, representing the Service Request Enable Register.

        """
        if not self.__SIMULATION:
            return int(self.connexion.query("*SRE?"))

    @SRE.setter
    def SRE(self, value):
        """
        Service Request Enable Command.

        Parameters
        ----------
        value : int
            Must be between 0 and 255 representing a mask for the Service Request Enable register bits.
        """
        if not isinstance(value, int):
            raise TypeError("Argument should be int")

        if not self.__SIMULATION:
            self.connexion.send("*SRE " + str(value))

    @property
    def STB(self):
        """
        Read Status Byte Query.

        Returns
        -------
        int
            Returns an integer from 0 to 255, representing the Status Bytes Register.

        """
        if not self.__SIMULATION:
            return int(self.connexion.query("*STB?"))

    def TST(self):
        """
        Self-Test Query. Runs a test to verify that everything is working correctly on the device.

        Returns
        -------
        int
            Returns 0 if everything is working correctly.

        """
        if not self.__SIMULATION:
            return int(self.connexion.query("*TST?"))

    def CLS(self):
        """
        Clear Status. Clears error/event queue, standard event register and status bytes register.

        """
        if not self.__SIMULATION:
            self.connexion.send("*CLS")

    def RST(self):
        """
        Reset Command: Returns to a known configuration.
        This disables the internal laser, resets the OFDR configuration (mode, range, center, etc.).
        Registers are not affected.

        """
        if not self.__SIMULATION:
            self.connexion.send("*RST")

    def system_error(self):
        """
        System Error Command. Returns error code if any.

        Returns
        -------
        int
            Error Code.

        """
        if not self.__SIMULATION:
            return int(self.connexion.query("SYST:ERR?"))

    def system_version(self):
        """
        Return SCPI system version.

        Returns
        -------
        str
            SCPI version.

        """
        if not self.__SIMULATION:
            return self.connexion.query("SYST:VERS?")

    def OPC_command(self):
        """
        *OPC command (without query).
        Sets the OPC bit in the Standard Event Status Register when all
        pending operations are complete.
        """
        if not self.__SIMULATION:
            self.connexion.send("*OPC")

    def WAI(self):
        """
        *WAI command. Waits until all pending operations are complete
        before accepting the next command.
        """
        if not self.__SIMULATION:
            self.connexion.send("*WAI")

    # =============================================================================
    #                       Status subsystem
    # =============================================================================

    @property
    def operation_status(self):
        """
        Query the Operation Status Register (STAT:OPER?).

        Returns
        -------
        int
            Operation status register value.

        """
        if not self.__SIMULATION:
            return int(self.connexion.query("STATus:OPERation:EVENt?"))
        return 0

    @property
    def operation_condition(self):
        """
        Query the Operation Status Condition Register (STAT:OPER:COND?).

        Returns
        -------
        int
            Operation condition register value.

        """
        if not self.__SIMULATION:
            return int(self.connexion.query("STATus:OPERation:CONDition?"))
        return 0

    @property
    def operation_enable(self):
        """
        Query the Operation Status Enable Register (STAT:OPER:ENAB?).

        Returns
        -------
        int
            Operation enable register value.

        """
        if not self.__SIMULATION:
            return int(self.connexion.query("STATus:OPERation:ENABle?"))
        return 0

    @operation_enable.setter
    def operation_enable(self, mask):
        """
        Set the Operation Status Enable Register (STAT:OPER:ENAB).

        Parameters
        ----------
        mask : int
            Bitmask (0-65535).

        """
        if not isinstance(mask, int):
            raise TypeError("Argument should be int")
        if not self.__SIMULATION:
            self.connexion.send("STATus:OPERation:ENABle " + str(mask))

    @property
    def questionable_status(self):
        """
        Query the Questionable Status Register (STAT:QUEST?).

        Returns
        -------
        int
            Questionable status register value.

        """
        if not self.__SIMULATION:
            return int(self.connexion.query("STATus:QUEStionable:EVENt?"))
        return 0

    @property
    def questionable_condition(self):
        """
        Query the Questionable Status Condition Register (STAT:QUEST:COND?).

        Returns
        -------
        int
            Questionable condition register value.

        """
        if not self.__SIMULATION:
            return int(self.connexion.query("STATus:QUEStionable:CONDition?"))
        return 0

    @property
    def questionable_enable(self):
        """
        Query the Questionable Status Enable Register (STAT:QUEST:ENAB?).

        Returns
        -------
        int
            Questionable enable register value.

        """
        if not self.__SIMULATION:
            return int(self.connexion.query("STATus:QUEStionable:ENABle?"))
        return 0

    @questionable_enable.setter
    def questionable_enable(self, mask):
        """
        Set the Questionable Status Enable Register (STAT:QUEST:ENAB).

        Parameters
        ----------
        mask : int
            Bitmask (0-65535).

        """
        if not isinstance(mask, int):
            raise TypeError("Argument should be int")
        if not self.__SIMULATION:
            self.connexion.send("STATus:QUEStionable:ENABle " + str(mask))

    def status_preset(self):
        """
        Preset status registers (STAT:PRES).
        Sets all enable registers to 0.
        """
        if not self.__SIMULATION:
            self.connexion.send("STATus:PRESet")

    # =============================================================================
    #                       Remote lock (APEX specific)
    # =============================================================================

    def lock(self):
        """
        Lock the instrument in remote mode (APEX:LOCK ON).
        The front-end GUI will display a "Remote" indicator.
        """
        if not self.__SIMULATION:
            self.connexion.send("APEX:LOCK ON")

    def unlock(self):
        """
        Unlock the instrument from remote mode (APEX:LOCK OFF).
        """
        if not self.__SIMULATION:
            self.connexion.send("APEX:LOCK OFF")
