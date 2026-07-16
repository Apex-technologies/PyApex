# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 12:23:36 2025

@author: marest
"""

import time
import select
import numpy as np

VACCUM_LIGHT_SPEED = 299792458

def send(socket, command: str, waiting: float=0.):
    """
    Send a command to the device

    Parameters
    ----------
    socket : socket
        Connection to the device.
    command : str
        Command to send.

    """
    if not isinstance(command, (str)):
        raise TypeError("Commmand should be string type.")
    else:
        command += '\n'
        time.sleep(waiting)
        socket.sendall(command.encode())

def receive(socket, bufsize: int=int(2**24)):
    """
    Receive meassage from device

    Parameters
    ----------
    socket : socket
        Connection to the device.
    bufsize : int, optional
        Reception buffer size. The default is int(2**24).

    Returns
    -------
    str
        Device answer

    """
    ans = socket.recv(bufsize)
    return ans.decode()


def query(socket, command: str, waiting=0):
    """
    Send a command to the device and receive a response.

    Parameters
    ----------
    socket : socket
        Connection to the device.
    command : str
        Command to send.
    waiting : TYPE, optional
        DESCRIPTION. The default is 0.2.

    Returns
    -------
    ans : TYPE
        DESCRIPTION.

    """
    """"""
    send(socket, command, waiting)
    time.sleep(waiting)
    ans = receive(socket)
    return ans

def query_data(socket, command, waiting=0.2):
    """
    Send a command to the device and receive a vector data (repeated bucnh received until no data to
    receive).

    Parameters
    ----------
    socket : socket
        Connection to the device.
    command : str
        Command to send.
    waiting : TYPE, optional
        DESCRIPTION. The default is 0.2.

    Returns
    -------
    data : bytes
        vetor data.

    """
    send(socket, command)
    time.sleep(waiting)

    socket.setblocking(False)
    data = b''
    try:
        while True:
            try:
                # Vérifie s'il y a des données à lire sans consommer (max 0.2 sec)
                rlist, _, _ = select.select([socket], [], [], 0.2)
                if not rlist:
                    break  # rien à lire pour l'instant

                # Lis les données disponibles
                chunk = socket.recv(int(2**21))

                # sécurité supplémentaire
                if not chunk: break

                data += chunk
                time.sleep(waiting)  # attendre un peu plus de données
            except Exception:
                print("BlockingIOError")
                break
    finally:
        socket.setblocking(True)
        socket.settimeout(20.0)

    return data

def decode_data(data, dtype=float):
    return np.frombuffer(data, dtype)

def query_data_and_decode(socket, command, waiting=0.2, dtype=float):

    data = query_data(socket, command, waiting)
    try:
        data = decode_data(data, dtype)
    except Exception:
        print("No data to decode")

    return data
