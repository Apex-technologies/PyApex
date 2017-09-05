
PyApex
======

Python3 Library for controlling Apex equipments

***
**Installation**<br><br>
1. Download the package PyApex<br><br>
2. Unzip it and move it in the "Lib" directory of your Python 3.x distribution
***
**Using**<br><br>
1. To access to the help and see all possibilities of PyApex, import the module :<br> 
`import PyApex`<br>
`help(PyApex)`<br>
With PyApex, you can communicate with AP1000 (Ethernet), AP2XXX (Ethernet), AB3510 (USB) and XU Thermal Etuve (RS232).<br><br>
**AP1000**<br><br>
The AP1000 class allows you to control (via Ethernet) any AP1000 equipment (AP1000-2, AP1000-5 and AP1000-8)<br><br>
1. In your Python 3.x script, import the PyApex module. For exemple, if you want to remote control an AP1000 equipment, import the AP1000 sub-module of PyApex as below<br>
`import PyApex.AP1000 as AP1000`<br><br>
2. Connect to the equipment. For an AP1000, you can use<br>
`MyAP1000 = AP1000("192.168.0.10", Simulation=False)`<br>
where `192.168.0.10` is the IP address of the equipment<br>
and `Simulation` argument is a boolean to simulate the equipment<br><br>
3. To see the methods and attributs of the AP1000 class, do:<br>
`help(MyAP1000)`<br><br>
4. To initiate a module of an AP1000 equipement, use the corresponding class and give the slot number in parameter. For exemple, to control an AP1000 power meter module (AP3314), you can use<br>
`MyPowerMeter = MyAP1000.PowerMeter(1)`<br>
where `1` is the slot number of the module<br>
and for seeing the different methods and attributs associated to this module, do:<br>
`help(MyPowerMeter)`<br><br>
5. To close the connection to the equipment, use the Close function. For exemple<br>
`MyAP1000.Close()`<br><br>
**AP2XXX**<br><br>
The AP2XXX class allows you to control (via Ethernet) any OSA and OCSA equipment (AP2040, AP2050, AP2060, AP2443,...)<br><br>
1. In your Python 3.x script, import the PyApex module. For exemple, if you want to remote control an AP2040 equipment, import the AP2XXX sub-module of PyApex as below<br>
`import PyApex.AP2XXX as AP2040`<br><br>
2. Connect to the equipment:<br>
`MyOSA = AP2040("192.168.0.10", Simulation=False)`<br>
where `192.168.0.10` is the IP address of the equipment<br>
and `Simulation` argument is a boolean to simulate the equipment<br><br>
3. To see the methods and attributs of the AP2XXX class, do:<br>
`help(MyOSA)`<br><br>
4. Here is a very simple example for controlling your OSA:<br>
`# Import the AP2XXX class from the Apex Driver`<br>
`from PyApex import AP2XXX`<br>
`# Import pyplot for displaying the data`<br>
`from matplotlib import pyplot as plt`<br>
``<br>
`# Connection to your OSA *** SET THE GOOD IP ADDRESS ***`<br>
`MyAP2XXX = AP2XXX("192.168.0.119")`<br>
`MyOSA = MyAP2XXX.OSA()`<br>
``<br>
`# Set the parameters of your OSA`<br>
`# Here, we use wavelength X-Axis and set the span from 1532 to 1563 nm`<br>
`# We also set the number of points to 2000`<br>
`MyOSA.SetScaleXUnit("nm")`<br>
`MyOSA.SetStartWavelength(1532.0)`<br>
`MyOSA.SetStopWavelength(1563.0)`<br>
`MyOSA.DeactivateAutoNPoints()`<br>
`MyOSA.SetNPoints(2000)`<br>
``<br>
`# We run a single`<br>
`Status = MyOSA.Run()`<br>
`# If the single is good (Status = 1), we get the data in a list Data = [[Power Data], [Wavelength Data]]`<br>
`if Status:`<br>
`    Data = MyOSA.GetData()`<br>
``<br>
`# The connection with the OSA is closed`<br>
`MyOSA.Close()`<br>
``<br>
`# The spectrum is displayed`<br>
`if Status:`<br>
`    plt.grid(True)`<br>
`    plt.plot(Data[1], Data[0])`<br>
`    plt.xlabel("Wavelength (nm)")`<br>
`    plt.ylabel("Power (dBm)")`<br>
`    plt.show()`<br>
`else:`<br>
`    print("No spectrum acquired")`<br>

4. To close the connection to the equipment, use the Close function:<br>
`MyOSA.Close()`<br><br>
