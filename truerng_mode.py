#!/usr/bin/python3

# TrueRNG Mode Change
# Chris K Cockrum
# 6/5/2020
#
# Requires Python 3.8, pyserial
# On Linux - may need to be root or set /dev/tty port permissions to 666
#
# Python 3.8.xx is available here: https://www.python.org/downloads/
# Install Pyserial package with:   python -m pip install pyserial
# Run this Python Script from the Windows command line:  py truerng_mode.py OR truerng_mode.py
# truerng_mode.py PORTNAME MODE
# Windows example:  py truerng_mode.py COM1 MODE_NORMAL
# Linux example:  python3 truerng_mode.py /dev/ttyACM0 MODE_NORMAL

import serial
import time
import sys
import math
import os
from serial.tools import list_ports

# Set Default Operating Mode to Normal
OPERATING_MODE='MODE_PSDEBUG'

# Set block size to read to get sample
sample_block_size=100 * 1024

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
# MODE_UNWHITENED  57600      /* Unwhitened RNG1-RNG2 (TrueRNGproV2 Only) */
# MODE_NORMAL_ASC   115200    /* Normal in Ascii Mode (TrueRNGproV2 Only) */
def modeChange(MODE, PORT):
    mode_match=0

    # "Knock" Sequence to activate mode change
    ser = serial.Serial(port=PORT,baudrate=110,timeout=1)
    ser.close()
    ser = serial.Serial(port=PORT,baudrate=300,timeout=1)
    ser.close()
    ser = serial.Serial(port=PORT,baudrate=110,timeout=1)
    ser.close()
    if MODE=='MODE_NORMAL':
        ser = serial.Serial(port=PORT,baudrate=300,timeout=1)
        print('Switched to ' + MODE)
        mode_match=1
    if MODE=='MODE_PSDEBUG':
        ser = serial.Serial(port=PORT,baudrate=1200,timeout=1)
        print('Switched to ' + MODE)
        mode_match=1
    if MODE=='MODE_RNGDEBUG':
        ser = serial.Serial(port=PORT,baudrate=2400,timeout=1)
        print('Switched to ' + MODE)
        mode_match=1
    if MODE=='MODE_RNG1WHITE':
        ser = serial.Serial(port=PORT,baudrate=4800,timeout=1)
        print('Switched to ' + MODE)
        mode_match=1
    if MODE=='MODE_RNG2WHITE':
        ser = serial.Serial(port=PORT,baudrate=9600,timeout=1)
        print('Switched to ' + MODE)
        mode_match=1
    if MODE=='MODE_RAW_BIN':
        ser = serial.Serial(port=PORT,baudrate=19200,timeout=1)
        print('Switched to ' + MODE)
        mode_match=1
    if MODE=='MODE_RAW_ASC':
        ser = serial.Serial(port=PORT,baudrate=38400,timeout=1)
        print('Switched to ' + MODE)
        mode_match=1
    if MODE=='MODE_UNWHITENED':
        ser = serial.Serial(port=PORT,baudrate=57600,timeout=1)
        print('Switched to ' + MODE)
        mode_match=1
    if MODE=='MODE_NORMAL_ASC':
        ser = serial.Serial(port=PORT,baudrate=115200,timeout=1)
        print('Switched to ' + MODE)
        mode_match=1
    ser.close()
    if mode_match==0:
        print('Mode not Recognized')

try:
    # Set com port to default None
    rng_com_port = None

    # Set mode to default None
    mode = None

    print('==============================================')
    print('= TrueRNG Mode Change                        =')
    print('= for TrueRNGpro and TrueRNGproV2            =')
    print('= http://ubld.it                             =')
    print('==============================================')

    #########################
    # Get list of Com ports #
    #########################

    # Call list_ports to get com port info
    ports_avaiable = list_ports.comports()

    # Loop on all available ports to find TrueRNG
    # Uses the first TrueRNG, TrueRNGpro, or TrueRNGproV2 found
    for temp in ports_avaiable:
     #   print(temp[1] + ' : ' + temp[2])
        if '04D8:F5FE' in temp[2]:
            print(temp[0] + ' : TrueRNG - Mode Changes Not Supported')
            if rng_com_port==None:
                rng_com_port=temp[0];
                mode='TrueRNG'
            else:
                if len(sys.argv)>=2:
                    if temp[0]==str(sys.argv[1]):
                        rng_com_port=temp[0];
                        mode='TrueRNG'
        if '16D0:0AA0' in temp[2]:
            print(temp[0] + ' : TrueRNGpro')
            if rng_com_port==None:
                rng_com_port=temp[0];
                mode='TrueRNGpro'
            else:
                if len(sys.argv)>=2:
                    if temp[0]==str(sys.argv[1]):
                        rng_com_port=temp[0];
                        mode='TrueRNGpro'
        if '04D8:EBB5' in temp[2]:
            print(temp[0] + ' : TrueRNGpro V2')
            if rng_com_port==None:
                rng_com_port=temp[0];
                mode='TrueRNGproV2'
            else:
                if len(sys.argv)>=2:
                    if temp[0]==str(sys.argv[1]):
                        rng_com_port=temp[0];
                        mode='TrueRNGproV2'

    # Print if we detect no compatible devices
    if rng_com_port==None:
        print('No TrueRNG devices detected!')

    print('==============================================')
    # Print out which port we are using
    if len(sys.argv) >= 2:
        print('Using ' + mode + ' on ' + rng_com_port)
    else:
        print('Using ' + mode + ' on ' + rng_com_port)

    if len(sys.argv) == 3:
        OPERATING_MODE=str(sys.argv[2])
    if mode=='TrueRNG':
        print('Mode Changes Not Supported')
    else:
        modeChange(OPERATING_MODE, rng_com_port)

    ser = serial.Serial(port=rng_com_port,timeout=10)  # timeout set at 10 seconds in case the read fails

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
        x=ser.read(sample_block_size)   # read bytes from serial port
        after = time.time()     # in microseconds
    except:
        print('Read Failed!!!')

    # Calculate the rate
    rate=float(sample_block_size) / ((after-before)*1000000.0) *8

    print(str(sample_block_size) + ' Bytes Read at ' + '{:2.3f}'.format(rate) + ' Mbits/s')

    print('Output Sample:')
    print(x[0:80:1])

    # Close the serial port
    ser.close()


except:
    print('Port Not Usable!')
    print('Do you have permissions set to read ' + rng_com_port + ' ?')

# If we're on Linux set min on com port back to 1
# Pyserial screws this up
if os.name == 'posix':
    os.system('stty -F '+rng_com_port+' min 1')
