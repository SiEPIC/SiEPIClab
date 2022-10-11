Installation instructions:

1. Download Anaconda 32 bit (Python 2.7):

    Download from: http://continuum.io/downloads

2. Install pyvisa:

    In a command prompt, run
        pip install pyvisa

3. Install wxpython 32 bit for Python 2.7:

    Download from: http://www.wxpython.org/download.php

4. Install comtypes

    In a command prompt, run
        pip install comtypes
       
 5. Install pylablib
 pip install pylablib
        
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
