# -*- coding: utf-8 -*-
"""
Transport abstraction layer for TCP/IP and RS232 communication.

Provides a unified interface for sending SCPI commands and receiving responses
over either TCP socket or serial (RS232) connections.

@author: marest
"""

import time
import socket

VACCUM_LIGHT_SPEED = 299792458


class Transport:
    """
    Base class for all transport layers.
    Subclasses must implement send, receive, settimeout and close.
    """

    def send(self, command: str, waiting: float = 0.):
        """
        Send a SCPI command string (appends \\n automatically).

        Parameters
        ----------
        command : str
            SCPI command to send.
        waiting : float, optional
            Delay before sending (seconds). The default is 0.

        """
        raise NotImplementedError

    def receive(self) -> str:
        """
        Receive a single-line response from the device.

        Returns
        -------
        str
            The decoded response.

        """
        raise NotImplementedError

    def query(self, command: str, waiting: float = 0.) -> str:
        """
        Send a command and return the response.

        Parameters
        ----------
        command : str
            SCPI command to send.
        waiting : float, optional
            Delay before sending and after sending (seconds). The default is 0.

        Returns
        -------
        str
            The decoded response.

        """
        self.send(command, waiting)
        time.sleep(waiting)
        return self.receive()

    def settimeout(self, timeout):
        """
        Set the read timeout.

        Parameters
        ----------
        timeout : float or None
            Timeout in seconds. None means blocking (no timeout).

        """
        raise NotImplementedError

    def close(self):
        """Close the connection."""
        raise NotImplementedError


class TCPTransport(Transport):
    """
    Transport layer over TCP/IP socket.

    Parameters
    ----------
    host : str
        IP address of the device.
    port : int, optional
        TCP port number. The default is 21212.

    """

    def __init__(self, host: str, port: int = 21212):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(20.0)
        self._sock.connect((host, port))

    def send(self, command: str, waiting: float = 0.):
        if not isinstance(command, str):
            raise TypeError("Command should be string type.")
        time.sleep(waiting)
        self._sock.sendall((command + '\n').encode())

    def receive(self) -> str:
        data = self._sock.recv(2**24)
        return data.decode()

    def settimeout(self, timeout):
        self._sock.settimeout(timeout)

    def close(self):
        try:
            self._sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self._sock.close()


class SerialTransport(Transport):
    """
    Transport layer over RS232 serial port.

    Parameters
    ----------
    port : str
        Serial port name (e.g. 'COM3' on Windows, '/dev/ttyUSB0' on Linux).
    baudrate : int, optional
        Baud rate. The default is 115200.
    timeout : float, optional
        Read timeout in seconds. The default is 10.

    """

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 10):
        import serial
        self._ser = serial.Serial(
            port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout,
        )

    def send(self, command: str, waiting: float = 0.):
        if not isinstance(command, str):
            raise TypeError("Command should be string type.")
        time.sleep(waiting)
        self._ser.write((command + '\n').encode())
        self._ser.flush()

    def receive(self) -> str:
        line = self._ser.readline()
        if line == b'':
            raise TimeoutError("Timeout waiting for response")
        return line.decode().strip()

    def settimeout(self, timeout):
        self._ser.timeout = timeout

    def close(self):
        self._ser.close()
