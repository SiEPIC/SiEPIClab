##Test Parameters Introduction

This software has been created to allow the user to easily input and format their test parameters such that pyOptomip can perform automated mesaurements. 
Please find a detailed explanation of how to use the software below

#How to use the testing Parameters file

1. Export your autoumated test coordinate file from Klayout
2. Open the testing parameter either through pyoptomip or as a standalone software by clicking on the testing parameters python file located within the pyOptomip folder
3. At the top of the frame there is a file upload box, please upload your automated test coodinate file
4. Once this file has been uploaded the devices in the coordinate file should now appear on the left in a checklist style
5. To begin setting the device testing parameters first select which device/devices you would like to set a routine for in the checklist (it is possible to select all and filter by keyword)
6. Next select how many of each type of routine this device will have in the menu below the checklist. There are 4 different types of routine electrical, optical, set wavelength voltage sweep and set voltage wavelength sweep 

Electrical
- this routine performs only a voltage or current sweep using the SMU, no optical function

Optical
- this routine performs only a wavelength sweep using the fibre array, no electrical function

Set voltage, wavelength sweep
- this routine uses the SMU to set a voltage or a range of voltages and then performs a wavelength sweep using the fibre array for each specified voltage

Set Wavelength, voltage sweep
- this routine uses the fibre array to set a wavelength or range of wavelengths anf then performs a voltage sweep using the SMU for each specifed wavelength

7. Now input the test parameters for each routine using the parameter panels, on completion of a routine select the save button to temporarily save the inputted test parameters
8. Once the all the test parameters have been inputted and saved select the set button in the lower right corner, this should reset the software and the devices that were set should now be greyed out in the checklist  
9. Continue to set the routines for various devices by following and repeating steps 5 through 8
10. Once the all the device routines have been set, if you would like a personal copy of the parameters in csv format use the save location box to select a save location for the file export
11. To finish and save your parameters press the export & save button in the lower righthand corner
12. There should now be a copy of the routines saved as a csv file to both your chosen save location and to the pyOptomip folder, pyOptomip should automatically use the csv file located in the pyOptomip file for all automated testing


#Retrieve data function

If you would like to modify an existing routine the retrieve data function allows you to do this. Just select the retreive data button near the top of the frame and then select the device whose routine you would to see, this will populate the parameter panels with the routines of that device (you can select multiple devices but can only select mutliple device with the same routine, on selection of a device all other devices with the same routine will be highlighted). To exit retrieve data mode once again press the retreive data button. You should now be able to set any device you want with the paramters of this device. 

