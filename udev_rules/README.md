For Ubuntu/Debian-based:
1. Put 99-TrueRNG.rules in /etc/dev/rules.d
   sudo cp LOCATION/99-TrueRNG.rules /etc/dev/rules.d 
2. Change permissions to 0644
   sudo chmod 0644 /etc/dev/rules.d
3. Reboot or reload udev rules
   sudo reboot
       or
   sudo udevadm control --reload-rules && sudo udevadm trigger
   
Your TrueRNG devices should now show up as:

/dev/TrueRNG0
/dev/TrueRNG1
etc. 
