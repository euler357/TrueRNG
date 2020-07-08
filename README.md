TrueRNG Utilities
=================
Scrips and Utilities for the TrueRNG and TrueRNGpro Random Number Generators

Tools (Windows and Linux)
-------------------------
* **truerng_find.py**:	Scans COM ports and identifies all connected TrueRNG devices
* **truerng_mode.py**: Example of how to change modes on TrueRNGpro and TrueRNGproV2 devices
* **truerng_read_example.py**: Example of how to read from a TrueRNG device
* **truerng_test.py**: Finds and performs testing on connected TrueRNG devices

Tools (Linux Only)
------------------
* **truerng_fulltest.py**:	Reads a large block of data (14GB) and runs ent, rngtest, and dieharder (takes ~9 hours on the TrueRNGpro / TrueRNGproV2)
* **run_rngtest**:					Linux script to run rngtest since it doensn't like to be called directly from Python - this is a "helper" for truerng_fulltest.py and isn't meant to be used directly

Windows INSTRUCTIONS
--------------------

1. Install Python 64-bit for Windows from:
https://www.python.org/ftp/python/3.8.3/python-3.8.3-amd64.exe

2. Put all files in the same directory - recommend c:\users\YOUR_USERNAME\TrueRNGutils or similar that you can remember

3. Open a command prompt (run the cmd command in Windows)

4. Change to the directory you created above and run: 

`install_python_libs.bat`

5. Plug in a single TrueRNG V1, V2, V3, Pro, or ProV2

6. Run the python TrueRNG test app

`py truerng_test.py`

OR

`truerng_test.py` (if .py is associated with python3)

This app should detect the device, run tests, and display results both in text and a graph of the performance.

Linux Instructions (Ubuntu / Debian-based)
------------------------------------------

1. Install Python3

`sudo apt install python3`

2. Put all of the TrueRNGutils files in one directory (recommend /home/USERNAME/TrueRNGutils)

3. Install the required Python libraries

`python3 -m pip install pyserial pyusb matplotlib numpy`

4. Run the python TrueRNG test app

`python3 truerng_test.py`

OR

`./truerng_test.py` (if your file permissions will allow execution)
 
This app should detect the device, run tests, and display results both in text and a graph of the performance.

More Python Tools and info at:  https://cockrum.net

What the Results of truerng_test.py should look like
====================================================

TrueRNGv1/v2/v3
---------------

![TrueRNGv3_Test](https://cockrum.net/images/TrueRNGv3_Test.jpg)
![TrueRNGv3_Test](https://cockrum.net/images/TrueRNGv3_Graph.jpg)

TrueRNGpro
---------------

![TrueRNGproV1_Test](https://cockrum.net/images/TrueRNGproV1_Test.jpg)
![TrueRNGproV1_Test](https://cockrum.net/images/TrueRNGproV1_Graph.jpg)

TrueRNGproV2 (Not yet released - undergoing testing)
---------------

![TrueRNGproV2_Test](https://cockrum.net/images/TrueRNGproV2_Test.jpg)
![TrueRNGproV2_Graph](https://cockrum.net/images/TrueRNGproV2_Graph.jpg)

