
PyApex
======

Python3 Library for controlling APEX Technologies products

***
**Installation**<br><br>
1. Locate the 'Code' button on the right-hand side of the page.
2. Click on it to access the drop down menu.
3. Click on the Download ZIP option.
4. Unzip it and move it in the "Lib" directory of your Python 3.x distribution or put it in the same folder as your python project. 
***
**Using**<br><br>
1. To access the help and see all possibilities of PyApex, import the module :<br> 
`import PyApex`<br>
`help(PyApex)`<br>
With PyApex, you can communicate with APEX Technologies products:<br>
– AP1000 Optical Multitest Platform mainframe (Ethernet)<br>
– AP2XXX legacy OSA & OCSA analyzers (Ethernet)<br>
– OSA-APx Series & OCSA-APx Series (Ethernet)<br>
– OFDR-APx Series & OCSA-APx Series (Ethernet)<br>
– AB3510 (USB) and XU Thermal Etuve (RS232)<br>
Upcoming: OFDR and TLS<br><br>
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

Here is a very simple example for controlling your AP1000:<br>
```python
# Import the AP1000 class from the Apex Driver
from PyApex import AP1000

# Connection to your AP1000 *** SET THE GOOD IP ADDRESS ***
MyAP1000 = AP1000("192.168.0.0")

# Display the modules of the AP1000
for i in range(1, 9):
	print("Slot", i, "->", MyAP1000.SlotType(i))

# Say a TLS is in slot 1 and a power meter in slot 2
MyTLS = MyAP1000.TunableLaser(1)
MyOPM = MyAP1000.PowerMeter(2)

# Initialize the TLS and the power meter
MyTLS.SetWavelength(1550.0)
MyTLS.SetUnit("dBm")
MyTLS.SetPower(10.0)
MyOPM.SetWavelength(1550.0)
MyOPM.SetAverageTime(200.0)
MyOPM.SetUnit("dBm")

# Switch on the TLS output
MyTLS.On()

# Do some measurement
PowerValue = MyOPM.GetPower(1)

# Switch off the TLS output
MyTLS.Off()

# The connection with the AP1000 is closed
MyAP1000.Close()
```
**AP2XXX // OSA/OCSA**<br><br>
The AP2XXX class allows you to control (via Ethernet) any OSA and OCSA equipment (OSA-APx Series, OCSA-APx Series, AP2040, AP2050, AP2060, AP2443,...)<br><br>
1. In your Python 3.x script, import the PyApex module. For exemple, if you want to remote control an OCSA-AP6-CLO equipment, import the AP2XXX sub-module of PyApex as below<br>
`import PyApex.AP2XXX as OCSA_AP6_CLO`<br><br>
2. Connect to the equipment:<br>
`OCSA_CLO = OCSA_AP6_CLO("192.168.0.10", Simulation=False)`<br>
where `192.168.0.10` is the IP address of the equipment<br>
and `Simulation` argument is a boolean to simulate the equipment<br><br>
3. To see the methods and attributs of the AP2XXX class, do:<br>
`help(OCSA_CLO)`<br>
All functions of your AP2XXX are in sub-classes :<br>
`MyOCSA = OCSA_CLO.OCSA()` for the Heterodyne OCSA<br>
`MyPowerMeter = OCSA_CLO.Powermeter()` for the powermeter, ...<br>
And, to see the methods and attributs of these sub-classes :<br>
`help(MyOCSA)`<br>
`help(MyPowerMeter)`<br>
4. Finally, to close the connection to the equipment, use the Close function:<br>
`OCSA_CLO.Close()`<br><br>

Here is a very simple example for controlling your OSA:<br>
```python
# Import the AP2XXX class from the Apex Driver
from PyApex import AP2XXX
# Import pyplot for displaying the data
from matplotlib import pyplot as plt

# Connection to your OSA *** SET THE GOOD IP ADDRESS ***
MyAP2XXX = AP2XXX("192.168.0.0")
MyOSA = MyAP2XXX.OSA()

# Set the parameters of your OSA
# Here, we use wavelength X-Axis and set the span from 1532 to 1563 nm
# We also set the number of points to 2000
MyOSA.SetScaleXUnit("nm")
MyOSA.SetStartWavelength(1532.0)
MyOSA.SetStopWavelength(1563.0)
MyOSA.DeactivateAutoNPoints()
MyOSA.SetNPoints(2000)

# We run a single
Trace = MyOSA.Run()
# If the single is good (Trace > 0), we get the data in a list Data = [[Power Data], [Wavelength Data]]
bASCII_data = True
if Trace > 0:
	if bASCII_data = True:
		 Data = MyOSA.GetData("nm","log",1)
	else:
		Data = MyOSA.GetDataBin("nm","log",1)

# The connection with the OSA is closed
MyAP2XXX.Close()

# The spectrum is displayed
if Trace > 0:
	plt.grid(True)
	plt.plot(Data[1], Data[0])
	plt.xlabel("Wavelength (nm)")
	plt.ylabel("Power (dBm)")
	plt.show()
else:
	print("No spectrum acquired")
```
