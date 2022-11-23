# pyOptomip
Copyright (c) 2015 Michael Caverley, at The University of British Columbia

Python code for <a href="https://siepic.ubc.ca/silicon-photonics-design-book/automated-probe-station/">Silicon Photonics Automated Probe stations

[PyOptomip User's Guide](https://github.com/SiEPIC/pyOptomip/blob/31f1fc96317e18f707d6d34837686f70abd1098e/PyOptomip%20User's%20Guide.pdf)
  
## Installation instructions:

1. Download Anaconda 64 bit Python 3.9 - *wxpython currently does not work on anything above 3.10*:

    Download from: http://continuum.io/downloads
	
2. In a command prompt, run 
	`python -m pip install -U wxPython`
	`pip install pyvisa=="1.11.3"`
	`pip install comtypes=="1.1.11"`
	`pip install thorlabs_apt_device`
	`pip install matplotlib=="3.4.3"`
	`pip install numpy=="1.20.3"`
	`pip install keithley2600`
	`pip install scipy=="1.9.0"`
	
	**Make sure the correct versions are downloaded and the previous versions have been uninstalled**
        
Instructions for running the GUI software:

Option 1: To run from within Spyder, add the pyOptomip folder to the PYTHONPATH. Then, run the pyOptomip.pyw script.

Option 2: To run as a standalone application, set the file association so that pyOptomip.pyw opens with pythonw.exe (found in C:\Anaconda). This
is the preferred way of running the program.

Instrument connection instructions:

To connect the instruments, first select the instrument you want to connect from the top dropdown menu. Then select the address (GPIP, serial etc.)
and enter the other parameters for the instrument. Press connect to initiate a connection to the instruments. The instruments can be connected in any
order.

Specific instructions for connecting each instrument:

Laser: hp816x
Select the GPIB address for the laser in the "GPIB address" combo box, then press connect.

Laser: hp816x_N77Det
Select the GPIB address for the 816x mainframe in the "Mainframe Address" combo box, then select the USB or GPIB VISA address for the N77xx detector in the
"Detector Address" combo box. Push connect in order to connect to both the mainframe and the detector.

Stage: Corvus Eco
Select the serial port that the stage is connected to using the "Serial Port" combo box. For example, if the stage is connected to serial port COM3, the VISA
address will be "ASRL3::INSTR". Then, enter the number of axes that your setup uses. If your stage uses three axes (i.e. x, y, and z for moving the fiber array
up and down), enter 3 into the "Number of Axis" box. If your setup only uses two axes (i.e., only x ad y), then enter 2. Finally, push connect in order to connect
to the stages.

Stage: Thorlabs BBD203
Enter the serial number for each of the stages, then push connect. A window will pop up with motor controls. Do not close this window.

Known issues:

When using hp816x_N77Det, if there are any detectors plugged into the 8163 or 8164 mainframe, the detectors listed on the Instrument Control 
window will not correspond to the labels on the detectors. This can cause unexpected sweep measurement results. The workaround is to unplug 
all detectors from the mainframe when using the N77xx detectors.

When not using the N77xx detector, if there is a detector plugged into the mainframe which stores less than 20001 datapoints (e.g. 81634A),
then stitching will not work.

# Update Steps:

1. install Anaconda3-2022.05-Windows-x86_64.exe, ensure python version is 3.9.7 by using a virtual environment, wxpython does not work on anything above 3.10
2. install NI max, including all suggested driver downloads on initial install,and NIvisa and NI 488.2 downloaded from NI package manager
3. install keysight 816x Instrument driver version 4.6.3 (has support for 64-bit), use the following link https://www.keysight.com/ca/en/lib/software-detail/driver/816x-vxi-plugplay-driver-112417.html

4.in command prompt run 
	'python -m pip install -U wxPython'
	'pip install pyvisa=="1.11.3"'
	'pip install comtypes=="1.1.11"'
	'pip install thorlabs_apt_device'
	'pip install matplotlib=="3.4.3"'
	'pip install numpy=="1.20.3"'
	'pip install keithley2600'
	'pip install scipy=="1.9.0"'
	
	**Make sure the correct versions are downloaded and the previous versions have been uninstalled**
	
5. check to make sure the pyOPtomip version has the following changes

Open D:\Anaconda3\Library\site-packages\comptypes\_init_.py
	edit lines 375 and 394 to read: 
		except COMError as err:
	edit line 577 to read: 
		except KeyError as err:	
	change all instances of unicode to str
		
Open D:\Anaconda3\Library\site-packages\comptypes\GUID.py
	change all instances of unicode to str

Open D:\Anaconda3\Library\site-packages\comptypes\automation.py
	remove trailing L from line 542
	change line 776 to read:
		except COMError as err:
6. Ensure the following changes have been made in the file hp816x.py

	in line 98 change
	res = self.hp816x_init(visaAddr, queryID, reset, byref(self.hDriver));
	to 
	res = self.hp816x_init(visaAddr.encode('utf-8'), queryID, reset, byref(self.hDriver));
	
	in line 106 change
	deviceIdnStr = self.gpibQueryString('*IDN?').strip().split(',')
	to 
	deviceIdnStr = self.gpibQueryString('*IDN?'.encode('utf-8'))
        deviceIdnStr = deviceIdnStr.strip().decode('utf-8').split(',')

7. Ensure the following changes have been made in the file hp816x_instr.py
	
	edit line 76 to read:
		def __init__(self, libLocation='hp816x_64.dll'):
	edit line 81 to read:
		self.hLib = WinDLL('hp816x_64.dll');
	
Continue adding changes and instructions here when they are done
