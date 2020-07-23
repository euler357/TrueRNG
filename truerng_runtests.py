#!/usr/bin/python3

# TrueRNG Run Tests
# Chris K Cockrum
# 6/14/2020
#
# Requires Python 3.8, dieharder, ent, rng-tools
#
# On Linux - may need to be root or set /dev/tty port permissions to 666
#
# Python 3.8.xx is available here: https://www.python.org/downloads/
#
# Note: Dieharder needs 14GiB of data to not re-use (rewind) input data
#       If you run this with 14GiB, many of the dieharder results may be invalid

import time
import sys
import os

if len(sys.argv)==2:
	FILENAME = str(sys.argv[1])
else:
	print('Usage: truerng_runtests.py FILENAME')
	exit()


if os.path.isfile(FILENAME):
	# Print Header
	print('==================================================')
	print('TrueRNGpro Running Full Tests on ' + FILENAME)
	print('http://ubld.it')
	print('==================================================')	
else:
	print(FILENAME + ' Not Found')
	exit()


# dieharder options
DIEHARDER_OPTIONS = '-a -g 201 -s 1 -k 2 -Y 1'

print('\n *** Running ent *** \n')

# Run ENT
try:
    os.system('ent ' + FILENAME + ' > ' + FILENAME + '.ent.txt')
except:
    print('Can\'t run ent')

# Run rngtest
print('\n *** Running rngtest *** \n')
try:
    os.system('./run_rngtest ' + FILENAME)
except:
    print('Can\'t run rngtest')

# Run Dieharder
print('\n *** Running dieharder *** \n')
try:
    os.system('dieharder ' + DIEHARDER_OPTIONS + ' -f ' + FILENAME + ' > ' + FILENAME + '.dieharder.txt')
except:
    print('Can\'t run dieharder')
