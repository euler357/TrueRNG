#!/usr/bin/python3

# TrueRNG Series Testing
# Chris K Cockrum
# 6/8/2020
#
# Requires Python 3.8, pyserial, matplotlib, numpy, and ent
#
# On Linux - may need to be root or set /dev/tty port permissions to 0666
#
# Python 3.8.xx is available here: https://www.python.org/downloads/
# Install Pyserial package with:   python -m pip install pyserial
# Install Pyserial package with:   python -m pip install pyusb
# Install Matplotlib package with:   python -m pip install matplotlib
# Install Numpy package with:   python -m pip install numpy
# Install Winregistry package with:   python -m pip install winregistry
# Run this Python Script from the Windows command line:  py Truerng_test.py OR Truerng_test.py
#
# You may enter the com port identification as a command line option:  py Truerng_test.py COM1

print('====================================================')
print('= TrueRNG Testing                                  =')
print('= for TrueRNG, TrueRNGV2, TrueRNGpro, TrueRNGproV2 =')
print('= http://ubld.it                                   =')
print('====================================================')

import time
import serial
import sys
import math
import os
import numpy as np
import matplotlib
import subprocess
from matplotlib import pyplot
from serial.tools import list_ports

if os.name == 'posix':
    import usb.core
    import usb.util

# If we're on Windows
if os.name == 'nt':
    from winregistry import WinRegistry as Reg

# Works for TrueRNG V1, V2, and V3
TrueRNG_Min_Rate = .35                      # Mbits/second
TrueRNG_Min_Entropy = 7.999                 # bits/byte
TrueRNG_Max_Pi_Error = 1                    # Maximum PI Error
TrueRNG_Max_Mean_Error = .5                 # Maximum Mean Error
TrueRNG_Normal_Test_Size = 256 * 1024       # .25 Mbyte of data

# Works for TrueRNGpro (V1)
TrueRNGpro_Min_Rate = 3.2                   # Mbits/second
TrueRNGpro_Min_Entropy = 7.9995             # bits/byte
TrueRNGpro_Max_Pi_Error = .5                # Maximum PI Error
TrueRNGpro_Max_Mean_Error = .5              # Maximum Mean Error
TrueRNGpro_Normal_Test_Size = 1*1024*1024   # 1Mbyte of data
TrueRNGpro_Min_PS_Voltage = 7800            # Millivolts
TrueRNGpro_Max_PS_Voltage = 10300           # Millivolts
TrueRNGpro_Mean_Min = 450
TrueRNGpro_Mean_Max = 550
TrueRNGpro_Std_Min = 20
TrueRNGpro_Std_Max = 180

# Works for TrueRNGproV2
TrueRNGproV2_Min_Rate = 3.3                  # Mbits/second
TrueRNGproV2_Min_Entropy = 7.9995            # bits/byte
TrueRNGproV2_Max_Pi_Error = .5               # Maximum PI Error
TrueRNGproV2_Max_Mean_Error = .5             # Maximum Mean Error
TrueRNGproV2_Normal_Test_Size = 1*1024*1024  # 1Mbyte of data
TrueRNGproV2_Min_PS_Voltage = 14500          # Millivolts
TrueRNGproV2_Max_PS_Voltage = 16500          # Millivolts
TrueRNGproV2_Mean_Min = 500
TrueRNGproV2_Mean_Max = 600
TrueRNGproV2_Std_Min = 50
TrueRNGproV2_Std_Max = 200
TrueRNGproV2_W_Mean_Min = 226
TrueRNGproV2_W_Mean_Max = 286
TrueRNGproV2_W_Std_Min = 20
TrueRNGproV2_W_Std_Max = 80

# Create output file
output_file = False

# Define test failed flag
test_failed = False

########################
# Function: modeChange #
########################
# Supported Modes
# MODE_NORMAL       300       /* Streams combined + Mersenne Twister */
# MODE_PSDEBUG      1200      /* PS Voltage in mV in ASCII */
# MODE_RNGDEBUG     2400      /* RNG Debug 0x0RRR 0x0RRR in ASCII */
# MODE_RNG1WHITE    4800      /* RNG1 + Mersenne Twister */
# MODE_RNG2WHITE    9600      /* RNG2 + Mersenns Twister*/
# MODE_RAW_BIN      19200     /* Raw ADC Samples in Binary Mode */
# MODE_RAW_ASC      38400     /* Raw ADC Samples in Ascii Mode */
# MODE_UNWHITENED  57600     /* Unwhitened RNG1-RNG2 */
# MODE_NORMAL_ASC   115200    /* Normal in Ascii Mode */
def modeChange(MODE, PORT):
    # "Knock" Sequence to activate mode change
    ser = serial.Serial(port=PORT,baudrate=110,timeout=1)
    time.sleep(0.5)
    ser.close()
    ser = serial.Serial(port=PORT,baudrate=300,timeout=1)
    ser.close()
    ser = serial.Serial(port=PORT,baudrate=110,timeout=1)
    ser.close()
    if MODE=='MODE_NORMAL':
        ser = serial.Serial(port=PORT,baudrate=300,timeout=1)
    if MODE=='MODE_PSDEBUG':
        ser = serial.Serial(port=PORT,baudrate=1200,timeout=1)
    if MODE=='MODE_RNGDEBUG':
        ser = serial.Serial(port=PORT,baudrate=2400,timeout=1)
    if MODE=='MODE_RNG1WHITE':
        ser = serial.Serial(port=PORT,baudrate=4800,timeout=1)
    if MODE=='MODE_RNG2WHITE':
        ser = serial.Serial(port=PORT,baudrate=9600,timeout=1)
    if MODE=='MODE_RAW_BIN':
        ser = serial.Serial(port=PORT,baudrate=19200,timeout=1)
    if MODE=='MODE_RAW_ASC':
        ser = serial.Serial(port=PORT,baudrate=38400,timeout=1)
    if MODE=='MODE_UNWHITENED':
        ser = serial.Serial(port=PORT,baudrate=57600,timeout=1)
    if MODE=='MODE_NORMAL_ASC':
        ser = serial.Serial(port=PORT,baudrate=115200,timeout=1)
    ser.close()

# Tests the power supply voltage on TrueRNGpro V1 and V2
def ps_voltage_test(comport):
    global test_failed
    modeChange('MODE_PSDEBUG', comport)

    # Try to setup and open the comport
    try:
        ser = serial.Serial(port=comport,timeout=10)  # timeout set at 10 seconds in case the read fails
    except:
        print('*** Port Not Usable!')
        print('*** Do you have permissions set to read ' + rng_com_port + ' ?')

    # Open the serial port if it isn't open
    if(ser.isOpen() == False):
        ser.open()
    ser.setDTR(True)
    ser.flushInput()

    try:
        x=ser.read(6*256)
    except:
        print('*** Read Failed!!!')
    voltage_list=x.decode("utf-8").split('\n')
    for i in range(0, len(voltage_list)):
        try:
            voltage_list[i] = int(voltage_list[i])
            if voltage_list[i]<1000 or voltage_list[i]>30000:
                del voltage_list[i]
        except:
            del voltage_list[i]
    average_voltage=sum(voltage_list) / len(voltage_list)
    if average_voltage>Min_PS_Voltage and average_voltage<Max_PS_Voltage:
        print('*** PASSED *** Power Supply Voltage = ' + '{:2.2f}'.format(average_voltage/1000) + ' Volts')
    else:
        print('*** FAILED *** Power Supply Voltage = ' + '{:2.2f}'.format(average_voltage/1000) + ' Volts')
        test_failed=True
    ser.close()

    return voltage_list

def normal_mode_test(comport):
    global test_failed
    if mode!= 'TrueRNG':
        modeChange('MODE_NORMAL', comport)

    if output_file==1:
        # Open/create the file random.bin in the current directory with 'write binary'
        fp=open('random.bin','wb')
        if fp==None:
            print('Error Opening File!')

    # Try to setup and open the comport
    try:
        ser = serial.Serial(port=comport,timeout=10)  # timeout set at 10 seconds in case the read fails
    except:
        print('*** Port Not Usable!')
        print('*** Do you have permissions set to read ' + comport + ' ?')

    # Open the serial port if it isn't open
    if(ser.isOpen() == False):
        ser.open()

    # Set Data Terminal Ready to start flow
    ser.setDTR(True)

    # This clears the receive buffer so we aren't using buffered data
    ser.flushInput()

    # Try to read the port and record the time before and after
    try:
        before = time.time()    # in microseconds
        x=ser.read(Normal_Test_Size)   # read bytes from serial port
        after = time.time()     # in microseconds
    except:
        print('*** Read Failed!!!')

    samples=x


    if output_file==1:
        # If we were able to open the file, write to disk
        if fp !=0:
            fp.write(x)

        # If the file is open then close it
        if fp != 0:
            fp.close()

    # Calculate the rate
    rate=float(Normal_Test_Size) / ((after-before)*1000000.0) *8

    # Check to see if the rate is fast enough
    if rate >= 1.0:
        if rate > Min_Rate:
            print('*** PASSED *** NORMAL Mode '+ str(len(x)) + ' Bytes Read at ' + '{:2.3f}'.format(rate) + ' Mbits/s')
        else:
            print('*** FAILED *** NORMAL Mode '+ str(len(x)) + ' Bytes Read at ' + '{:2.3f}'.format(rate) + ' Mbits/s')
            test_failed=True
    else:
        if rate > Min_Rate:
            print('*** PASSED *** NORMAL Mode '+ str(len(x)) + ' Bytes Read at ' + '{:2.3f}'.format(rate*1000) + ' Kbits/s')
        else:
            print('*** FAILED *** NORMAL Mode '+ str(len(x)) + ' Bytes Read at ' + '{:2.3f}'.format(rate*1000) + ' Kbits/s')
            test_failed=True

    # Close the serial port
    ser.close()

    # Count Frequency of each value
    freqList = [0] * 256 # Create Array of Zeros

    # Loop on all bytes in captured data array
    for byte in x:
        freqList[byte]=freqList[byte]+1;    # Increment frequency for each byte found

    # Calculate shannon entropy
    ent = 0.0
    for b in range(256):
        freqList[b]=freqList[b]/Normal_Test_Size
        if freqList[b] > 0:
            ent = ent + freqList[b] * math.log(freqList[b], 2)

    if (-ent) > 7.99:
        print('*** PASSED *** NORMAL Mode Entropy: ' + '{:2.6f}'.format(-ent) + ' bits/byte')
    else:
        print('*** FAILED *** NORMAL Mode Entropy: ' +str(-ent) + ' bits/byte')
        test_failed=True

    # Do ent functions here on x

    ################################
    ## MONTE CARLO ESTIMATE OF PI ##
    ################################
    circle_points=0
    square_points=0
    incirc= (2.0**48-1)**2
    sumx=0
    j=0.0
    k=0.0

    # x is a byte of 0-255 in value
    for i in range(0,(len(x)-24),12):
        j=(samples[i]) \
         +(samples[i+1]<<8) \
         +(samples[i+2]<<16) \
         +(samples[i+3]<<24) \
         +(samples[i+4]<<32) \
         +(samples[i+5]<<40)
        k=(samples[i+6]) \
         +(samples[i+7]<<8) \
         +(samples[i+8]<<16) \
         +(samples[i+9]<<24) \
         +(samples[i+10]<<32) \
         +(samples[i+11]<<40)
        square_points=square_points+1
        sumx=samples[i]+samples[i+1] +\
             samples[i+2]+samples[i+3] +\
             samples[i+4]+samples[i+5] +\
             samples[i+6]+samples[i+7] +\
             samples[i+8]+samples[i+9] +\
             samples[i+10]+samples[i+11]+sumx
        if((j*j) + (k*k)) < incirc:
            circle_points=circle_points+1
    calcpi=4.0 * float(circle_points)/float(square_points)
    pierror= 100.0 * math.fabs(calcpi - math.pi) / math.pi

    meanvalue=sumx/square_points/12
    if math.fabs(meanvalue-127.5) < Max_Mean_Error:
        print('*** PASSED *** Mean is ' + '{:1.3f}'.format(meanvalue) + '(127.500 = random)')
    else:
        print('*** FAILED *** Mean is ' + '{:1.3f}'.format(meanvalue)  + '(127.500 = random)')
        test_failed=True


    if pierror < Max_Pi_Error:
        print('*** PASSED *** Monte Carlo estimate of pi is ' + '{:1.6f}'.format(calcpi) + \
            ' (' + '{:1.6f}'.format(pierror)  + '% Error)')
    else:
        print('*** FAILED *** Monte Carlo estimate of pi is ' + '{:1.6f}'.format(calcpi) + \
            ' (' + '{:1.6f}'.format(pierror)  + '% Error)')
        test_failed=True

    return freqList

def raw_asc_mode_test(comport):
    global test_failed
    modeChange('MODE_RAW_ASC', comport)

    # Try to setup and open the comport
    try:
        ser = serial.Serial(port=comport,timeout=10)  # timeout set at 10 seconds in case the read fails
    except:
        print('*** Port Not Usable!')
        print('*** Do you have permissions set to read ' + comport + ' ?')

    # Open the serial port if it isn't open
    if(ser.isOpen() == False):
        ser.open()

    # Set Data Terminal Ready to start flow
    ser.setDTR(True)

    # This clears the receive buffer so we aren't using buffered data
    ser.flushInput()

    # Try to read the port and record the time before and after
    try:
        before = time.time()    # in microseconds
        x=ser.read(Normal_Test_Size)   # read bytes from serial port
        after = time.time()     # in microseconds
    except:
        print('*** Read Failed!!!')


    # Calculate the rate
    rate=float(Normal_Test_Size) / ((after-before)*1000000.0) *8

    # Check to see if the rate is fast enough
    print('*** PASSED *** RAW ASCII Mode '+ str(len(x)) + ' Bytes Read at ' + '{:2.3f}'.format(rate) + ' Mbits/s')

    # Close the serial port
    ser.close()


    raw_asc_list=x.decode("utf-8").split('\n')

    freqList = [0] * 2048 # Create Array of Zeros
    gen1=0
    gen2=0
    sum_gen1=0.0
    sum_gen2=0.0
    gen1samples=[0]*len(raw_asc_list)
    gen2samples=[0]*len(raw_asc_list)
    # Count Frequency of each value
    for i in range(0, len(raw_asc_list)):
        try:
            temp=raw_asc_list[i].split(',')
            gen1=int(temp[0])
            gen2=int(temp[1])
            gen1samples[i]=gen1
            gen2samples[i]=gen2
            sum_gen1=sum_gen1+gen1
            sum_gen2=sum_gen2+gen2
            if gen1 < 0 or gen1 > 1023:
                break
            if gen2 < 0 or gen2 > 1023:
                break
            freqList[gen1]=freqList[gen1]+1
            freqList[gen2+1024]=freqList[gen2+1024]+1
        except:
            break

    # Print out the mean of each generator
    gen1_mean=sum_gen1/len(raw_asc_list)
    gen2_mean=sum_gen2/len(raw_asc_list)

    if gen1_mean > Min_Mean and gen1_mean < Max_Mean:
        print('*** PASSED *** Gen1 Mean = '+ '{:3.2f}'.format(gen1_mean))
    else:
        print('*** FAILED *** Gen1 Mean = '+ '{:3.2f}'.format(gen1_mean))
        test_failed=True
    if gen2_mean > Min_Mean and gen2_mean < Max_Mean:
        print('*** PASSED *** Gen2 Mean = '+ '{:3.2f}'.format(gen2_mean))
    else:
        print('*** FAILED *** Gen2 Mean = '+ '{:3.2f}'.format(gen2_mean))
        test_failed=True

    gen1std=np.std(gen1samples)
    gen2std=np.std(gen2samples)
    if gen1std > Min_Std and gen1std < Max_Std:
        print('*** PASSED *** Gen1 Standard Deviation = '+ '{:3.2f}'.format(gen1std))
    else:
        print('*** FAILED *** Gen1 Standard Deviation = '+ '{:3.2f}'.format(gen1std))
        test_failed=True
    if gen2std > Min_Std and gen2std < Max_Std:
        print('*** PASSED *** Gen2 Standard Deviation = '+ '{:3.2f}'.format(gen2std))
    else:
        print('*** FAILED *** Gen2 Standard Deviation = '+ '{:3.2f}'.format(gen2std))
        test_failed=True

    return freqList

def unwhitened_mode_test(comport):
    global test_failed
    modeChange('MODE_UNWHITENED', comport)

    # Try to setup and open the comport
    try:
        ser = serial.Serial(port=comport,timeout=10)  # timeout set at 10 seconds in case the read fails
    except:
        print('*** Port Not Usable!')
        print('*** Do you have permissions set to read ' + comport + ' ?')

    # Open the serial port if it isn't open
    if(ser.isOpen() == False):
        ser.open()

    # Set Data Terminal Ready to start flow
    ser.setDTR(True)

    # This clears the receive buffer so we aren't using buffered data
    ser.flushInput()

    # Try to read the port and record the time before and after
    try:
        before = time.time()    # in microseconds
        k=ser.read(Normal_Test_Size)   # read bytes from serial port
        after = time.time()     # in microseconds
    except:
        print('*** Read Failed!!!')

    # Calculate the rate
    rate=float(Normal_Test_Size) / ((after-before)*1000000.0) *8

    # Check to see if the rate is fast enough
    print('*** PASSED *** UNWHITENED Mode '+ str(len(k)) + ' Bytes Read at ' + '{:2.3f}'.format(rate) + ' Mbits/s')

    # Close the serial port
    ser.close()
    whitened_list=k.decode("utf-8").split(',')

    freqList = [0] * 512 # Create Array of Zeros
    whitened_samples = [0] * len(whitened_list)
    whitened_sum=0

    # Count Frequency of each value
    for i in range(0, len(whitened_list)):
        try:
            temp=int(whitened_list[i])
            whitened_samples[i]=temp
            whitened_sum=whitened_sum+temp
            if temp < 0 or temp > 511:
                break
            freqList[temp]=freqList[temp]+1
        except:
            break

    # Print out the mean of each generator
    whitened_mean=whitened_sum/len(whitened_list)

    if whitened_mean > TrueRNGproV2_W_Mean_Min and whitened_mean < TrueRNGproV2_W_Mean_Max:
        print('*** PASSED *** Whitened Mean = '+ '{:3.2f}'.format(whitened_mean))
    else:
        print('*** FAILED *** Whitened Mean = '+ '{:3.2f}'.format(whitened_mean))
        test_failed=True

    whitenedstd=np.std(whitened_samples)
    if whitenedstd > TrueRNGproV2_W_Std_Min and whitenedstd < TrueRNGproV2_W_Std_Max:
        print('*** PASSED *** Whitened Standard Deviation = '+ '{:3.2f}'.format(whitenedstd))
    else:
        print('*** FAILED *** Whitened Standard Deviation = '+ '{:3.2f}'.format(whitenedstd))
        test_failed=True

    return freqList

def move_figure(f, x, y):
    """Move figure's upper left corner to pixel (x, y)"""
    backend = matplotlib.get_backend()
    if backend == 'TkAgg':
        f.canvas.manager.window.wm_geometry("+%d+%d" % (x, y))
    elif backend == 'WXAgg':
        f.canvas.manager.window.SetPosition((x, y))
    else:
        # This works for QT and GTK
        # You can also use window.setGeometry
        f.canvas.manager.window.move(x, y)


if os.name == 'nt':
    def get_Truerngs_from_registry():
        reg=Reg()

        usb_serial_devices=reg.read_key(r'HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\usbser\Enum')

        devices_values=usb_serial_devices["values"]


        serialNumber='None'

        index=0
        devicesFound=[]

        # Loop through
        for x in devices_values:
            try:
                serialNumber='None'
                # TrueRNG V1/V2/V3
                if 'VID_04D8&PID_F5FE' in x["data"]:
                    temp=x["data"].split('\\')
                    vidpid=temp[1]
                    keyid=temp[2]
                    newkey= 'HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Enum\\USB\\'+str(vidpid) + '\\' + str(keyid)
                    device_info=reg.read_key(newkey)["values"]
                    deviceType='TrueRNG V1/V2/V3'
                    for k in device_info:
                        if k['value']=="FriendlyName":
                            FriendlyName=k['data']
                        if k['value']=="HardwareID":
                            vidpidrev=k['data'][0].split('\\')[1].split('&')
                    devicesFound.append(deviceType + ' : ' + \
                        vidpidrev[2] + ' : No SN : ' + FriendlyName)

                # TrueRNGpro (FW > 1.39)
                # USB Class 0A
                if 'VID_16D0&PID_0AA0\\' in x["data"]:
                    temp=x["data"].split('\\')
                    vidpid=temp[1]
                    keyid=temp[2]
                    newkey= 'HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Enum\\USB\\'+str(vidpid) + '\\' + str(keyid)
                    device_info=reg.read_key(newkey)["values"]
                    deviceType='TrueRNGpro (V1) '
                    for k in device_info:
                        if k['value']=="FriendlyName":
                            FriendlyName=k['data']
                        if k['value']=="HardwareID":
                            vidpidrev=k['data'][0].split('\\')[1].split('&')
                    devicesFound.append(deviceType + ' : ' + \
                        vidpidrev[2] + ' : ' + keyid + ' : ' + FriendlyName)

                # TrueRNGpro (FW <= 1.39)
                # USB Class 02
                if 'VID_16D0&PID_0AA0&MI_00\\' in x["data"]:
                    temp=x["data"].split('\\')
                    vidpid=temp[1]
                    keyid=temp[2]
                    newkey= 'HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Enum\\USB\\'+str(vidpid) + '\\' + str(keyid)
                    device_info=reg.read_key(newkey)["values"]
                    deviceType='TrueRNGpro (V1) '
                    for k in device_info:
                        if k['value']=="FriendlyName":
                            FriendlyName=k['data']
                        if k['value']=="HardwareID":
                            vidpidrev=k['data'][0].split('\\')[1].split('&')

                    # Find the info of the parent device since Windows doesn't populate the serial number into the child
                    newkey= 'HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Enum\\USB\\VID_16D0&PID_0AA0'
                    device_keys=reg.read_key(newkey)['keys']
                    # Iterate through the keys to find our device by it's key id
                    for j in device_keys:
                        newkey= 'HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Enum\\USB\\VID_16D0&PID_0AA0\\' + j
                        temp_device=reg.read_key(newkey)['values']
                        for a in temp_device:
                            if 'ParentIdPrefix' in a['value']:
                                # If we have the right key entry
                                if a['data'] in keyid:
                                    serialNumber=j
                    if serialNumber != 'None':
                        devicesFound.append(deviceType + ' : ' + \
                            vidpidrev[2] + ' : ' + serialNumber + ' : ' + FriendlyName)
                    else:
                        devicesFound.append(deviceType + ' : ' + \
                            vidpidrev[2] + ' : ' + keyid + ' : ' + FriendlyName)

                # TrueRNGpro V2 (FW > 1.39)
                # USB Class 0A
                if 'VID_04D8&PID_EBB5' in x["data"]:
                    temp=x["data"].split('\\')
                    vidpid=temp[1]
                    keyid=temp[2]
                    newkey= 'HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Enum\\USB\\'+str(vidpid) + '\\' + str(keyid)
                    device_info=reg.read_key(newkey)["values"]
                    deviceType='TrueRNGpro (V2) '
                    for k in device_info:
                        if k['value']=="FriendlyName":
                            FriendlyName=k['data']
                        if k['value']=="HardwareID":
                            vidpidrev=k['data'][0].split('\\')[1].split('&')
                    devicesFound.append(deviceType + ' : ' + \
                        vidpidrev[2] + ' : ' + keyid + ' : ' + FriendlyName)

            except:
                i=1;
        return devicesFound


try:
    while True:
        fig=0
        # Reset test failed
        test_failed = False

        # Set com port to default None
        rng_com_port = None

        # Set mode to default None
        mode = None

        # Set serial number to None
        serial_number = 'None'

        #########################
        # Get list of Com ports #
        #########################

        # Call list_ports to get com port info
        ports_available = list_ports.comports()

        # Loop on all available ports to find TrueRNG
        # Uses the first TrueRNG, TrueRNGpro, or TrueRNGproV2 found
        for temp in ports_available:
         #   print(temp[1] + ' : ' + temp[2])
            if '04D8:F5FE' in temp[2]:
                print(temp[0] + ' : TrueRNG')
                if rng_com_port==None:
                    rng_com_port=temp[0];
                    serial_number=temp.serial_number
                    mode='TrueRNG'
                else:
                    if len(sys.argv)==2:
                        if temp[0]==str(sys.argv[1]):
                            rng_com_port=temp[0];
                            serial_number=temp.serial_number
                            mode='TrueRNG'
            if '16D0:0AA0' in temp[2]:
                print(temp[0] + ' : TrueRNGpro')
                if rng_com_port==None:
                    rng_com_port=temp[0];
                    serial_number=temp.serial_number
                    mode='TrueRNGpro'
                else:
                    if len(sys.argv)==2:
                        if temp[0]==str(sys.argv[1]):
                            rng_com_port=temp[0];
                            serial_number=temp.serial_number
                            mode='TrueRNGpro'
            if '04D8:EBB5' in temp[2]:
                print(temp[0] + ' : TrueRNGpro V2')

                if rng_com_port==None:
                    rng_com_port=temp[0];
                    serial_number=temp.serial_number
                    mode='TrueRNGproV2'
                else:
                    if len(sys.argv)==2:
                        if temp[0]==str(sys.argv[1]):
                            rng_com_port=temp[0];
                            serial_number=temp.serial_number
                            mode='TrueRNGproV2'

        # Print if we detect no compatible devices
        if rng_com_port==None:
            print('No TrueRNG devices detected!')

        print('====================================================')

        # Print out which port we are using
        if len(sys.argv) == 2:
            rng_com_port = str(sys.argv[1])
            print('Using ' + mode + ' on ' + rng_com_port + ' (from command line)')
        else:
            print('Using ' + mode + ' on ' + rng_com_port + ' (first detected)')

        # If we're on Windows
        if os.name == 'nt':
            devices=get_Truerngs_from_registry()
            tempportname='(' + rng_com_port + ')'
            for n in devices:
                if tempportname in n:
                    print(n)
        else:
            print('Serial Number: ' + str(serial_number))

        # If we're on Linux
        if os.name == 'posix':
            if mode=='TrueRNG':
                command='lsusb -d 04d8:f5fe -v 2> /dev/null | grep bcdDevice'
            if mode=='TrueRNGpro':
                command='lsusb -d 16d0:0aa0 -v 2> /dev/null | grep bcdDevice'
            if mode=='TrueRNGproV2':
                command='lsusb -d 04d8:ebb5 -v 2> /dev/null | grep bcdDevice'
            result=subprocess.check_output(command, shell=True)
            print('Firmware Rev : ' + str(result).split('  ')[-1].split('\\')[0])

        # Set Defaults for the Current Mode / Device
        if mode=='TrueRNG':
            Min_Rate = TrueRNG_Min_Rate
            Min_Entropy = TrueRNG_Min_Entropy
            Max_Pi_Error = TrueRNG_Max_Pi_Error
            Max_Mean_Error = TrueRNG_Max_Mean_Error
            Normal_Test_Size = TrueRNG_Normal_Test_Size
        if mode=='TrueRNGpro':
            Min_Rate = TrueRNGpro_Min_Rate
            Min_Entropy = TrueRNGpro_Min_Entropy
            Max_Pi_Error = TrueRNGpro_Max_Pi_Error
            Max_Mean_Error = TrueRNGpro_Max_Mean_Error
            Normal_Test_Size = TrueRNGpro_Normal_Test_Size
            Min_PS_Voltage = TrueRNGpro_Min_PS_Voltage
            Max_PS_Voltage = TrueRNGpro_Max_PS_Voltage
            Min_Mean = TrueRNGpro_Mean_Min
            Max_Mean = TrueRNGpro_Mean_Max
            Min_Std = TrueRNGpro_Std_Min
            Max_Std = TrueRNGpro_Std_Max
        if mode=='TrueRNGproV2':
            Min_Rate = TrueRNGproV2_Min_Rate
            Min_Entropy = TrueRNGproV2_Min_Entropy
            Max_Pi_Error = TrueRNGproV2_Max_Pi_Error
            Max_Mean_Error = TrueRNG_Max_Mean_Error
            Normal_Test_Size = TrueRNGproV2_Normal_Test_Size
            Min_PS_Voltage = TrueRNGproV2_Min_PS_Voltage
            Max_PS_Voltage = TrueRNGproV2_Max_PS_Voltage
            Min_Mean = TrueRNGproV2_Mean_Min
            Max_Mean = TrueRNGproV2_Mean_Max
            Min_Std = TrueRNGproV2_Std_Min
            Max_Std = TrueRNGproV2_Std_Max

        if rng_com_port==None:
            print('No TrueRNG devices detected')
        else:
            print('====================================================')

            # Do tests for TrueRNG V1/V2/V3
            if mode=='TrueRNG':
                normal_freq_list = normal_mode_test(rng_com_port)

                ###########################
                # This is the figure size #
                ###########################
                fig = pyplot.figure(figsize=(8,4),dpi=100)
                fig.suptitle('TrueRNG V1/V2/V3 Performance Plots ('+rng_com_port+')', fontsize=16)
                plt1 = fig.add_subplot(111)
                plt1.bar(np.arange(len(normal_freq_list)), normal_freq_list, 1)
                plt1.set_xlim([0,len(normal_freq_list)])
                plt1.set_title('Normal Mode Frequency Distribution')

                if test_failed:
                    plt1.set_facecolor((1.0,0.0,0.0))
                else:
                    plt1.set_facecolor((1.0,1.0,1.0))

                move_figure(fig, 0, 0)
                pyplot.draw()
                pyplot.pause(1)
                input("Press enter for another test or Ctrl-C to end.")
                pyplot.close(fig)

            # Do tests for TrueRNGpro (V1)
            if mode=='TrueRNGpro':
                ps_voltage_list = ps_voltage_test(rng_com_port)
                normal_freq_list = normal_mode_test(rng_com_port)
                raw_asc_freq_list = raw_asc_mode_test(rng_com_port)

                #############
                # Plot Data #
                #############

                ###########################
                # This is the figure size #
                ###########################
                fig = pyplot.figure(figsize=(11,7),dpi=100)

                fig.suptitle('TrueRNGpro (V1) Performance Plots ('+rng_com_port+')', fontsize=16)
                plt1 = fig.add_subplot(221)
                plt1.plot(np.arange(len(ps_voltage_list)), ps_voltage_list, '-')
                plt1.set_xlim(0,len(ps_voltage_list))
                plt1.set_ylim(Min_PS_Voltage, Max_PS_Voltage)
                plt1.set_title('Power Supply Voltage')
                plt1.set_facecolor((1.0,0.0,0.0))

                plt2 = fig.add_subplot(222)
                plt2.bar(np.arange(len(normal_freq_list)), normal_freq_list, 1)
                plt2.set_xlim([0,len(normal_freq_list)])
                plt2.set_title('Normal Mode Frequency Distribution')

                plt3 = fig.add_subplot(223)
                plt3.bar(np.arange(1023), raw_asc_freq_list[0:1023:1], 1)
                plt3.set_xlim([0,len(raw_asc_freq_list)/2])
                plt3.set_ylim(0,Normal_Test_Size/768)
                plt3.set_title('Generator 1 Raw ASCII Mode Frequency Distribution')

                plt4 = fig.add_subplot(224)
                plt4.bar(np.arange(1023), raw_asc_freq_list[1024:2047:1], 1)
                plt4.set_xlim([0,len(raw_asc_freq_list)/2])
                plt4.set_ylim(0,Normal_Test_Size/768)
                plt4.set_title('Generator 2 Raw ASCII Mode Frequency Distribution')


                if test_failed:
                    plt1.set_facecolor((1.0,0.0,0.0))
                    plt2.set_facecolor((1.0,0.0,0.0))
                    plt3.set_facecolor((1.0,0.0,0.0))
                    plt4.set_facecolor((1.0,0.0,0.0))
                else:
                    plt1.set_facecolor((1.0,1.0,1.0))
                    plt2.set_facecolor((1.0,1.0,1.0))
                    plt3.set_facecolor((1.0,1.0,1.0))
                    plt4.set_facecolor((1.0,1.0,1.0))

                ###############################
                # This is the figure location #
                # 0,0 = upper left            #
                ###############################
                move_figure(fig, 0, 0)

                pyplot.draw()
                pyplot.pause(1)
                input("Press enter for another test or Ctrl-C to end.")
                pyplot.close(fig)

            # Do tests for TrueRNGproV2
            if mode=='TrueRNGproV2':
                ps_voltage_list = ps_voltage_test(rng_com_port)
                normal_freq_list = normal_mode_test(rng_com_port)
                raw_asc_freq_list = raw_asc_mode_test(rng_com_port)
                unwhitened_freq_list = unwhitened_mode_test(rng_com_port)

                #############
                # Plot Data #
                #############

                ###########################
                # This is the figure size #
                ###########################
                fig = pyplot.figure(figsize=(11,9),dpi=100)

                fig.suptitle('TrueRNGproV2 Performance Plots ('+rng_com_port+')', fontsize=16)
                plt1 = fig.add_subplot(321)
                plt1.plot(np.arange(len(ps_voltage_list)), ps_voltage_list, '-')
                plt1.set_xlim(0,len(ps_voltage_list))
                plt1.set_ylim(Min_PS_Voltage, Max_PS_Voltage)
                plt1.set_title('Power Supply Voltage')

                plt2 = fig.add_subplot(322)
                plt2.bar(np.arange(len(normal_freq_list)), normal_freq_list, 1)
                plt2.set_xlim([0,len(normal_freq_list)])
                plt2.set_title('Normal Mode Frequency Distribution')

                plt3 = fig.add_subplot(323)
                plt3.bar(np.arange(1023), raw_asc_freq_list[0:1023:1], 1)
                plt3.set_xlim([0,len(raw_asc_freq_list)/2])
                plt3.set_ylim(0,Normal_Test_Size/1024)
                plt3.set_title('Generator 1 Raw ASCII Mode Frequency Distribution')

                plt4 = fig.add_subplot(324)
                plt4.bar(np.arange(1023), raw_asc_freq_list[1024:2047:1], 1)
                plt4.set_xlim([0,len(raw_asc_freq_list)/2])
                plt4.set_ylim(0,Normal_Test_Size/1024)
                plt4.set_title('Generator 2 Raw ASCII Mode Frequency Distribution')

                plt5 = fig.add_subplot(3,2,(5,6))
                plt5.bar(np.arange(len(unwhitened_freq_list)), unwhitened_freq_list, 1)
                plt5.set_xlim([0,len(unwhitened_freq_list)])
                plt5.set_ylim(0,Normal_Test_Size/256)
                plt5.set_title('Unwhitened Mode Frequency Distribution')

                if test_failed:
                    plt1.set_facecolor((1.0,0.0,0.0))
                    plt2.set_facecolor((1.0,0.0,0.0))
                    plt3.set_facecolor((1.0,0.0,0.0))
                    plt4.set_facecolor((1.0,0.0,0.0))
                    plt5.set_facecolor((1.0,0.0,0.0))
                else:
                    plt1.set_facecolor((1.0,1.0,1.0))
                    plt2.set_facecolor((1.0,1.0,1.0))
                    plt3.set_facecolor((1.0,1.0,1.0))
                    plt4.set_facecolor((1.0,1.0,1.0))
                    plt5.set_facecolor((1.0,1.0,1.0))

                ###############################
                # This is the figure location #
                # 0,0 = upper left            #
                ###############################
                move_figure(fig, 0, 0)

                pyplot.draw()
                pyplot.pause(1)
                input("Press enter for another test or Ctrl-C to end.")
                pyplot.close(fig)

            print('====================================================')
            print('================= NEW TEST =========================')
            print('====================================================')

except:
    if fig:
        pyplot.close(fig)
    print('Exiting now!')

# If we're on Linux set min on com port back to 1
# Pyserial screws this up
if os.name == 'posix':
    os.system('stty -F '+rng_com_port+' min 1')
