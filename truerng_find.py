#!/usr/bin/python3

# TrueRNG Finder
# Chris K Cockrum
# 6/8/2020
#
# Requires Python 3.8, pyserial
# On Linux - may need to be root or set /dev/tty port permissions to 666
#
# Python 3.8.xx is available here: https://www.python.org/downloads/
# Install Pyserial package with:   python -m pip install pyserial
# Install Pyusb package with:   python -m pip install pyusb
# Run this Python Script from the Windows command line:  py truerng_find.py OR truerng_find.py

import serial
import time
import sys
import math
import os
import platform
import usb
import subprocess
from serial.tools import list_ports

if os.name == 'nt':
    from winregistry import WinRegistry as Reg
    def get_truerngs_from_registry():
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
                    devicesFound.append(deviceType + ' : '  + \
                        vidpidrev[2] + ' : No SN    : ' + FriendlyName)

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
                    devicesFound.append(deviceType + ' : ' +  \
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
                        devicesFound.append(deviceType + ' : '  + \
                            vidpidrev[2] + ' : ' + serialNumber + ' : ' + FriendlyName)
                    else:
                        devicesFound.append(deviceType + ' : '  + \
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
    # Set com port to default None
    rng_com_port = None

    # Set mode to default None
    mode = None

    print('====================================================')
    print('= TrueRNG Finder                                   =')
    print('= for TrueRNG, TrueRNGV2, TrueRNGpro, TrueRNGproV2 =')
    print('= http://ubld.it                                   =')
    print('====================================================')

    ########################
    # Get list of TrueRNGs #
    ########################


    # If we're on Windows
    if os.name == 'nt':
        devices=get_truerngs_from_registry()
        for n in devices:
            print(n)

    # If we're on Linux
    if os.name == 'posix':

        # Call list_ports to get com port info
        ports_avaiable = list_ports.comports()

        # Loop on all available ports to find TrueRNG
        # Uses the first TrueRNG, TrueRNGpro, or TrueRNGproV2 found
        for temp in ports_avaiable:
         #   print(temp[1] + ' : ' + temp[2])
            if '04D8:F5FE' in temp[2]:
                command='lsusb -d 04d8:f5fe -v 2> /dev/null | grep bcdDevice'
                result=subprocess.check_output(command, shell=True)
                print(temp[0] + ' : TrueRNG       : No SN      ' + ' : Rev ' + str(result).split('  ')[-1].split('\\')[0])
            if '16D0:0AA0' in temp[2]:
                command='lsusb -d 16d0:0aa0 -v 2> /dev/null | grep bcdDevice'
                result=subprocess.check_output(command, shell=True)
                print(temp[0] + ' : TrueRNGpro    : SN ' + temp.serial_number + ' : Rev ' + str(result).split('  ')[-1].split('\\')[0])
            if '04D8:EBB5' in temp[2]:
                command='lsusb -d 04d8:ebb5 -v 2> /dev/null | grep bcdDevice'
                result=subprocess.check_output(command, shell=True)
                print(temp[0] + ' : TrueRNGpro V2 : SN ' + temp.serial_number + ' : Rev ' + str(result).split('  ')[-1].split('\\')[0])


    print('====================================================')

except:
    print('Exiting now!')

