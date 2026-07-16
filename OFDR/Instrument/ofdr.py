# -*- coding: utf-8 -*-
"""
Created on Mon Sep  1 09:50:15 2025

@author: marest
"""

from .common import send, query, query_data_and_decode
import numpy as np


class OFDR():


    def __init__(self, equipment, simulation=False):
        '''
        Constructor of the OFDR embedded in an equipment.
        Equipment is the Instrument class of the equipment
        Simulation is a boolean to indicate to the program if it has to run in simulation mode or not
        '''
        self.__connexion = equipment.connexion
        self.__SIMULATION = simulation

        # Variables and constants of the equipment
        self.__unit = "dBm"
        self.__validUnits = ["dbm", "mw"]

        self.__power = 0.0
        self.__wavelength = 1550.0
        self.__status = "OFF"
        self.__OPC = 1

        self.__start_wavelength = 1520.0
        self.__stop_wavelength = 1630.0
        self.__conf = []
        self.__mode = "REFL"
        self.__group_index = 1.465
        self.__fourier_window = "SQUA"
        self.__span = 110.0
        self.__center = 1575.0
        self.__max_length = 11

    def get_configuration(self, calc_length_res=True, display=True):
        """
        Gets OFDR measurement settings for the next measurement

        Parameters
        ----------
        calc_length_res : boll, optional
            Calculate the equivalent resolution and add it the return parameters. The default is True.
        display : bool, optional
            Print settings. The default is True.

        Returns
        -------
        setting list
            [Max length, wavelength span, center wavelength,
             Window, group index, length resolution (optional)]

        """

        if not self.__SIMULATION:
            command = "CONFiguration?"
            conf = query(self.__connexion, command)
            self.__conf = conf.strip().split(";")

            if calc_length_res:
                length_res = 1e-3*float(self.__conf[3])**2/((1+int(not bool(int(self.__conf[0])))) * float(self.__conf[5]) * float(self.__conf[2]))
                self.__conf.append(length_res)
            if display:
                if self.__conf[0]==0:
                    print("Transmission mode")
                else:
                    print("Reflection mode")

                print("Max Length =", self.__conf[1], "m")
                print("Wavelength Span =", self.__conf[2], "nm")
                print("Center Wavelength =", self.__conf[3], "nm")
                print("Fourier Window =", self.__conf[4])
                print("Group Index =", self.__conf[5])
                print("Length Resolution = %.3f" % self.__conf[6], 'µm')
        else:
            self.__conf = ['0', '11', '110.96', '1575.0', 'square', '1.465']

        return self.__conf

    @property
    def mode(self):
        """
        Get working mode (reflection or transmssion) for the next measurement

        Returns
        -------
        str
            Returns "REFL" for reflection mode or "TRAN" for transmission mode.

        """
        if not self.__SIMULATION:
            command = "CONFiguration:MODe?"
            mode = int(query(self.__connexion, command))

            if mode == 0:
                self.__mode = "REFL"
            else:
                self.__mode = "TRAN"


        return self.__mode

    @mode.setter
    def mode(self, mode):
        """
        Set working mode (reflection or transmssion) for the next measurement

        Parameters
        ----------
        mode : str
            Should be "REFL" (reflection mode) or "TRAN" transmission mode.

        """
        if not isinstance(mode, (str)):
            raise TypeError("Argument should be str")
        if mode not in ("REFL", "TRAN"):
            raise ValueError("Argument should be REFL or TRAN")

        self.__mode = mode

        if not self.__SIMULATION:
            command = "CONFiguration:MODe " + mode
            send(self.__connexion, command)


    @property
    def group_index(self):
        """
        Get group index for the next measurement

        Returns
        -------
        float
            Group index setting.

        """
        if not self.__SIMULATION:
            command = "SENSe:GIND?"
            self.__group_index = float(query(self.__connexion, command))

        return self.__group_index

    @group_index.setter
    def group_index(self, index):
        """
        Set group index for the next measurement

        Parameters
        ----------
        index : float
            Group index value.

        """
        if not isinstance(index, (int, float)):
            raise TypeError("Argument should be int or float")
        self.__group_index = index

        if not self.__SIMULATION:
            command = "SENSe:GIND " + str(index)
            send(self.__connexion, command)


    @property
    def fourier_window(self):
        """
        Get fourier windowing technique for the next measurement.

        Returns
        -------
        str
            "SQUA" for square window (default) or "HANN" for hanning window.

        """
        if not self.__SIMULATION:
            command = "SENSe:WINdow?"
            fourier_window = query(self.__connexion, command).strip()

        if fourier_window == "square":
            self.__fourier_window = "SQUA"
        else:
            self.__fourier_window = "HANN"

        return self.__fourier_window

    @fourier_window.setter
    def fourier_window(self, window):
        """
        Set fourier windowing technique for the next measurement

        Parameters
        ----------
        window : str
            "SQUA" for square window (default) or "HANN" for hanning window.

        """
        if not isinstance(window, (str)):
            raise TypeError("Argument should be str")
        if window not in ("SQUA", "HANN"):
            raise ValueError("Argument should be SQUA or HANN")

        self.__fourier_window = window

        if not self.__SIMULATION:
            command = "SENSe:WINdow " + window
            send(self.__connexion, command)

    @property
    def span(self):
        """
        Get wavelength span for the ext measurement

        Returns
        -------
        float
            Wavelength span in nm.

        """
        if not self.__SIMULATION:
            command = "SENSe:WAVelength:SPAN?"
            self.__span = float(query(self.__connexion, command))

        return self.__span

    @span.setter
    def span(self, sp):
        """
        Set wavelength span for the next measurement

        Parameters
        ----------
        sp : float
            Wavelength span in nm.

        """
        if not isinstance(sp, (int, float)):
            raise TypeError("Argument should be int or float")

        self.__span = abs(sp)

        if not self.__SIMULATION:
            command = "SENSe:WAVelength:SPAN " + str(self.__span)
            send(self.__connexion, command)

    @property
    def center(self):
        """
        Get center wavelength for the next measurement

        Returns
        -------
        float
            Center wavelength in nm.

        """
        if not self.__SIMULATION:
            command = "SENSe:WAVelength:CENTer?"
            self.__center = float(query(self.__connexion, command))

        return self.__center

    def get_span_list(self):
        """
        List all available span in the current length mode

        Returns
        -------
        span_list : list
            List of span in nm.

        """
        if not self.__SIMULATION:
            command = "SENSe:WAVelength:SPAN:LIST?"
            span_list = query(self.__connexion, command).strip().split(';')
        else:
            span_list = [110, 55, 27.5, 12.0, 7.0]

        return span_list

    @center.setter
    def center(self, ct):
        """
        Set center wavelength for the next measurement

        Parameters
        ----------
        ct : float
            Center wavelength in nm.

        """
        if not isinstance(ct, (int, float)):
            raise TypeError("Argument should be int or float")

        self.__center = abs(ct)
        if not self.__SIMULATION:
            command = "SENSe:WAVelength:CENT " + str(self.__center)
            send(self.__connexion, command)

    @property
    def max_length(self):
        """
        Get max length for the next measurement

        Returns
        -------
        int
            Max length in meter.

        """
        if not self.__SIMULATION:
            command = "SENSe:LENGth:MAX?"
            self.__max_length = int(query(self.__connexion, command))

        return self.__max_length

    @max_length.setter
    def max_length(self, length):
        """
        Set max length for the next measurement

        Parameters
        ----------
        length : int, float
            Max length in meter.

        """
        if not isinstance(length, (int, float)):
            raise TypeError("Argument should be int or float")

        self.__max_length = abs(length)
        if not self.__SIMULATION:
            command = "SENSe:LENGth:MAX " + str(self.__max_length)
            send(self.__connexion, command)

    def get_max_length_list(self):
        """
        List all available max length in the current device

        Returns
        -------
        length_list : list
            List of max length in meter.

        """

        if not self.__SIMULATION:
            command = "SENSe:LENGth:LIST?"
            length_list = query(self.__connexion, command).strip().split(';')
        else:
            length_list = [11, 45, 244]

        return length_list


    def single(self):
        """
        Initiate a single measurement

        """
        if not self.__SIMULATION:
            command = "INITiate"
            send(self.__connexion, command)

    def stop(self):
        """
        Stop all current operation

        """
        if not self.__SIMULATION:
            command = "ABORt"
            send(self.__connexion, command)


    def get_time_axis(self):
        """
        Retrieve time axis data

        Returns
        -------
        data : array
            Time vector (s)

        """
        if not self.__SIMULATION:
            command = ":MEMory:DATA:TIME?"
            data = query_data_and_decode(self.__connexion, command, dtype=float)
            return data

    def get_length_axis(self):
        """
        Retrieve length axis data

        Returns
        -------
        data : array
            length vector (m)

        """
        if not self.__SIMULATION:
            command = ":MEMory:DATA:LENGth?"
            data = query_data_and_decode(self.__connexion, command, dtype=float)
            return data

    def get_amplitude(self):
        """
        Retrieve amplitude data

        Returns
        -------
        data : array
            amplitude vector (dB).

        """
        if not self.__SIMULATION:
            command = ":MEMory:DATA:AMP?"
            data = query_data_and_decode(self.__connexion, command, dtype=float)
            return data

    def get_amplitude_polar(self):
        """
        Retrieve polarization amplitude data

        Returns
        -------
        polar1 : array
            Polarization 1 amplitude (dB)
        polar2 : array
            Polarization 2 amplitude (dB).

        """
        if not self.__SIMULATION:
            command = ":MEMory:DATA:AMP:POL1?"
            polar1 = query_data_and_decode(self.__connexion, command, dtype=float)

            command = ":MEMory:DATA:AMP:POL2?"
            polar2 = query_data_and_decode(self.__connexion, command, dtype=float)

            return polar1, polar2

    def get_phase_derivative(self):
        """
        Retrieve phase derivative data

        Returns
        -------
        data : array
            Phase derivative vector (nm).

        """
        if not self.__SIMULATION:
            command = ":MEMory:DATA:PHD?"
            data = query_data_and_decode(self.__connexion, command, dtype=float)
            return data

    def get_phase_derivative_polar(self):
        """
        Retrieve polarization phase derivative data

        Returns
        -------
        polar1 : array
            Polarization 1 phase derivative (nm)
        polar2 : array
            Polarization 2 phase derivative (nm).

        """
        if not self.__SIMULATION:
            command = ":MEMory:DATA:PHD:POL1?"
            polar1 = query_data_and_decode(self.__connexion, command, dtype=float)

            command = ":MEMory:DATA:PHD:POL2?"
            polar2 = query_data_and_decode(self.__connexion, command, dtype=float)

            return polar1, polar2

    def get_complex_data(self):
        """
        Retieve complex "raw" data

        Returns
        -------
        polar1 : array
            Polarization 1 complex data.
        polar2 : array
            Polarization 2 complex data.

        """
        if not self.__SIMULATION:
            command = ":MEMory:DATA:POL1?"
            polar1 = query_data_and_decode(self.__connexion, command, dtype=np.complex128)

            command = ":MEMory:DATA:POL2?"
            polar2 = query_data_and_decode(self.__connexion, command, dtype=np.complex128)

            return polar1, polar2


    def get_wavelength_axis(self):
        """
        Retrieve wavelength axis (useful for spectral analysis)

        Returns
        -------
        data : array
            Wavelength vector (m).

        """
        if not self.__SIMULATION:
            command = ":MEMory:DATA:WAV?"
            data = query_data_and_decode(self.__connexion, command, dtype=float)
            return data

    def get_wavlength_limits(self):
        """
        Returns Maximum and minimum wavelength of the measurement

        Returns
        -------
        float, float
            Min wavelength, Max wavelength.

        """
        if not self.__SIMULATION:
            command = ":MEMory:DATA:WAV:MAX?"
            maxi = query(self.__connexion, command)

            command = ":MEMory:DATA:WAV:MIN?"
            mini = query(self.__connexion, command)

            return float(mini), float(maxi)


    def clear_memory(self):
        """
        Clear recorded data (last measurement data)

        """
        if not self.__SIMULATION:
            command = ":MEMory:CLEar"
            send(self.__connexion, command)


    def set_conf_spectral_analysis(self, center, width, window_type="LENG"):
        """
        Configure spectral analysis settings

        Parameters
        ----------
        center : float
            Center window (in the unit set by window_type).
        width : float
            Window width (in the unit set by window_type).
        window_type : str, optional
            Define unit for center and width "LENG" for length unit or "TIME" for time unit.
            The default is "LENG".

        """
        if not isinstance(center, (int, float)):
            raise TypeError("center should be int or float")
        if not isinstance(width, (int, float)):
            raise TypeError("width should be int or float")
        if not isinstance(window_type, (str)):
            raise TypeError("window_type should be str")

        if window_type not in ("LENG", "TIME"):
            raise ValueError("Argument should be LENG or TIME")

        if not self.__SIMULATION:
            command = "CALCulate:SPECtral:WINdow:TYPE " + window_type
            send(self.__connexion, command)

            command = "CALCulate:SPECtral:WINdow:CENTer " + str(center).upper()
            send(self.__connexion, command)

            command = "CALCulate:SPECtral:WINdow:SPAN " + str(width).upper()
            send(self.__connexion, command)

    def get_conf_spectral_analysis(self, display=True):
        """
        Get spectral analysis configuration

        Parameters
        ----------
        display : bool, optional
            Print the configuration. The default is True.

        Returns
        -------
        center : float
            Window center.
        width : float
            Window width.
        window_type : str
            "LENG" for length unit or "TIME" for time unit.

        """

        if not self.__SIMULATION:
            command = "CALCulate:SPECtral:WINdow:TYPE?"
            window_type = query(self.__connexion, command).strip()

            if window_type=="length":
                window_type = "LENG"
            else:
                window_type = "TIME"

            command = "CALCulate:SPECtral:WINdow:CENTer?"
            center = query(self.__connexion, command)
            center = float(center)

            command = "CALCulate:SPECtral:WINdow:SPAN?"
            width = query(self.__connexion, command)
            width = float(width)

            if display:
                print("Center Window =", center)
                print("Window width =", width)
                print("Window type =", window_type)

            return center, width, window_type

    def execute_spectral_analysis(self):
        """
        Execute spectral analysis

        """
        if not self.__SIMULATION:
            command = "CALCulate:SPECtral:EXECute"
            send(self.__connexion, command)

    def get_return_loss(self):
        """
        Retrieve return loss data from analysis results

        Returns
        -------
        data : array
            Return loss vector (dB).

        """
        if not self.__SIMULATION:
            command = "CALCulate:SPECtral:DATA:RL?"
            data = query_data_and_decode(self.__connexion, command, dtype=float)
            return data

    def get_group_delay(self):
        """
        Retrieve group delay data from analysis results

        Returns
        -------
        data : array
            group delay vector (s).

        """
        if not self.__SIMULATION:
            command = "CALCulate:SPECtral:DATA:GD?"
            data = query_data_and_decode(self.__connexion, command, dtype=float)
            return data

    def clear_data_spectral_analysis(self):
        """
        Clear recorded spectral analysis results

        """
        if not self.__SIMULATION:
            command = "CALCulate:SPECtral:DATA:CLEar"
            send(self.__connexion, command)

    def set_conf_temp_strain_analysis(self, center, width, resolution, coef_temp=7.0e-6, coef_strain=0.787, window_type="LENG"):
        """
        Set configuration for temperature and stain analysis

        Parameters
        ----------
        center : float
            Center window (in the unit set by window_type).
        width : float
            Window width (in the unit set by window_type).
        resolution : float
            Desired resolution for the measurement.
        coef_temp : float, optional
            Temperature coeficient. The default is 7.0e-6.
        coef_strain : float, optional
            Strain coefficient. The default is 0.787.
        window_type : str, optional
            Define unit for center and width "LENG" for length unit or "TIME" for time unit.
            The default is "LENG".

        """
        if not isinstance(center, (int, float)):
            raise TypeError("center should be int or float")
        if not isinstance(width, (int, float)):
            raise TypeError("width should be int or float")
        if not isinstance(resolution, (int, float)):
            raise TypeError("resolution should be int or float")
        if not isinstance(window_type, (str)):
            raise TypeError("window_type should be str")

        if window_type not in ("LENG", "TIME"):
            raise ValueError("Argument should be LENG or TIME")

        if not self.__SIMULATION:
            command = "CALCulate:TPSR:WINdow:TYPE " + window_type
            send(self.__connexion, command)

            command = "CALCulate:TPSR:WINdow:CENTer " + str(center).upper()
            send(self.__connexion, command)

            command = "CALCulate:TPSR:WINdow:SPAN " + str(width).upper()
            send(self.__connexion, command)

            command = "CALCulate:TPSR:WINdow:RES " + str(resolution).upper()
            send(self.__connexion, command)

            command = "CALCulate:TPSR:COEFficient:TEMPerature " + str(coef_temp).upper()
            send(self.__connexion, command)

            command = "CALCulate:TPSR:COEFficient:STRAin " + str(coef_strain).upper()
            send(self.__connexion, command)

    def get_conf_temp_strain_analysis(self, display=True):
        """
        Get temperature and strain analysis configuration

        Parameters
        ----------
        display : TYPE, optional
            DESCRIPTION. The default is True.

        Returns
        -------
        center : float
            Center window (in the unit set by window_type).
        width : float
            Window width (in the unit set by window_type).
        resolution : float
            Desired resolution for the measurement.
        coef_temp : float, optional
            Temperature coeficient. The default is 7.0e-6.
        coef_strain : float, optional
            Strain coefficient. The default is 0.787.
        window_type : str, optional
            Define unit for center and width "LENG" for length unit or "TIME" for time unit.
            The default is "LENG".
        """

        if not self.__SIMULATION:
            command = "CALCulate:TPSR:WINdow:TYPE?"
            window_type = query(self.__connexion, command).strip()

            if window_type=="length":
                window_type = "LENG"
            else:
                window_type = "TIME"

            command = "CALCulate:TPSR:WINdow:CENTer?"
            center = query(self.__connexion, command)
            center = float(center)

            command = "CALCulate:TPSR:WINdow:SPAN?"
            width = query(self.__connexion, command)
            width = float(width)

            command = "CALCulate:TPSR:WINdow:RES?"
            resolution = query(self.__connexion, command)
            resolution = float(resolution)

            command = "CALCulate:TPSR:COEFficient:TEMPerature?"
            coef_temp = float(query(self.__connexion, command))

            command = "CALCulate:TPSR:COEFficient:STRAin?"
            coef_strain = float(query(self.__connexion, command))

            if display:
                print("Center = %.6f" % center, 'm')
                print("Width = %.6f" % width, 'm')
                print("Resolution = %.6f" % resolution, 'm')
                print("coef_temp = %.6e" % coef_temp)
                print("coef_strain = %.6e" % coef_strain)

            return center, width, resolution, coef_temp, coef_strain, window_type

    def set_data_ref(self):
        """
        Set the last recorded measurement data as the reference dta for temperature and strain analysis

        """
        if not self.__SIMULATION:
            command = "CALCulate:TPSR:DATA:REF"
            send(self.__connexion, command)

    def execute_temp_strain_analysis(self):
        """
        Execute temperature and strain analysis

        """
        if not self.__SIMULATION:
            command = "CALCulate:TPSR:EXECute"
            send(self.__connexion, command)


    def get_spectral_shift(self):
        """
        Retrieve spectral shift data from analysis results

        Returns
        -------
        data : array
            Spectral shift vector (Hz)

        """
        if not self.__SIMULATION:
            command = "CALCulate:TPSR:DATA:SHIFt?"
            data = query_data_and_decode(self.__connexion, command, dtype=float)
            return data

    def get_temperature(self):
        """
        Retrieve temperature data from analysis results

        Returns
        -------
        data : array
            Temperature vector (s)

        """
        if not self.__SIMULATION:
            command = "CALCulate:TPSR:DATA:TEMPerature?"
            data = query_data_and_decode(self.__connexion, command, dtype=float)
            return data

    def get_strain(self):
        """
        Retrieve strain data from analysis results

        Returns
        -------
        data : array
            strain vector (s)

        """
        if not self.__SIMULATION:
            command = "CALCulate:TPSR:DATA:STRAin?"
            data = query_data_and_decode(self.__connexion, command, dtype=float)

            return data

    def get_quality(self):
        """
        Retrieve quality data from analysis results.
        The closer the values ​​are to 1, the more reliable the measurements are

        Returns
        -------
        data : array
            quality vector

        """
        if not self.__SIMULATION:
            command = "CALCulate:TPSR:DATA:QUALity?"
            data = query_data_and_decode(self.__connexion, command, dtype=float)

            return data

    def get_temp_strain_length_axis(self):
        """
        Retrieve length axis data from analysis results

        Returns
        -------
        data : array
            length vector (m)

        """
        if not self.__SIMULATION:
            command = "CALCulate:TPSR:DATA:LENGth?"
            data = query_data_and_decode(self.__connexion, command, dtype=float)
            return data

    def get_temp_strain_time_axis(self):
        """
        Retrieve time axis data from analysis results

        Returns
        -------
        data : array
            time vector (s)

        """
        if not self.__SIMULATION:
            command = "CALCulate:TPSR:DATA:LENGth?"
            data = query_data_and_decode(self.__connexion, command, dtype=float)
            return data

    def clear_data_temp_strain_analysis(self):
        """
        Clear analysis results

        """
        if not self.__SIMULATION:
            command = "CALCulate:TPSR:DATA:CLEar"
            send(self.__connexion, command)


    def get_laser_platitude(self, mode="reflex"):
        """
        Retrieve laser platitude data for the specified mode
        
        Parameters
        ----------
        mode : str, optional
            OFDR mode. Should be "reflex" or "trans". The default is "reflex".

        Returns
        -------
        wl : array
            Wavelength vector.

        val : array
            Power vector.
        """
        if not self.__SIMULATION:
            if mode=="reflex":
                command = ":CALibration:PLATitude:REFLection?"
                data = query(self.__connexion, command, 0.1)
            else:
                command = ":CALibration:PLATitude:TRANS?"
                data = query(self.__connexion, command, 0.1)
                
            values = [float(x) for x in command[1].strip().split(',')]
            wl, val = values[:len(values)//2], values[len(values)//2:]
            
            return wl, val
        
        
    def set_laser_platitude(self, wavelength, power, mode="reflex"):
        """
        Send laser platitude data for the specified mode to correct the 
        device calibration

        Parameters
        ----------
        wavelength : array
            Wavelength in nm.
        power : array
            Power of the laser for each wavelength in dBm.
        mode : str, optional
            OFDR mode. Should be "reflex" or "trans". The default is "reflex".

        """
        wavelength = np.array(wavelength)
        power = np.array(power)
        
        wl = ",".join(f"{x:.3f}" for x in wavelength)
        amp = ",".join(f"{x:.3f}" for x in power)
        data_to_send = wl + ',' + amp
        
        if mode=="reflex":
            command = ":CALibration:PLATitude:REFLection " + str(data_to_send).upper()
        else:
            command = ":CALibration:PLATitude:TRANS " + str(data_to_send).upper()
        send(self.__connexion, command)
        
        
    def reset_laser_platitude(self, mode="reflex"):
        """
        reset laser platitude data for the specified mode

        Parameters
        ----------
        mode : str, optional
            OFDR mode. Should be "reflex" or "trans". The default is "reflex".

        """
        
        if mode=="reflex":
            command = ":CALibration:CLEar:REFLection"
        else:
            command = ":CALibration:CLEar:TRANS"
        send(self.__connexion, command)

    @property
    def laser_serial_number(self):
        """
        Get laser serial number (Velocity laser)

        Returns
        -------
        serial_number : str
            Actual laser serial number used by the device.

        """

        command = "SYSTem:LASEr:SERialnumber?"
        serial_number = query(self.__connexion, command)
        return serial_number

    @laser_serial_number.setter
    def laser_serial_number(self, serial_number):
        """
        Set the laser serial number (to change the laser on the next start up).
        Works with Velocity version.

        Parameters
        ----------
        serial_number : str
            New serial number to set.

        """

        command = "SYSTem:LASEr:SERialnumber " + str(serial_number)
        send(self.__connexion, command)

    def reset_laser_serial_number(self):
        """
        Reset laser serial to the factory settings

        """
        command = "SYSTem:LASEr:SERialnumber:CLEar"
        send(self.__connexion, command)

    def open_network_configuration(self):
        """
        Opens windows network configuration on the device

        """
        command = "SYSTem:NETwork"
        send(self.__connexion, command)
        
        
