#!/bin/sh
# habLauncher.sh

# Put this file on the Desktop
# Add a folder to the desktop called Logs
# In chrontab, the command to run at startup is:
# @reboot sh /home/pi/Desktop/habLauncher.sh >/home/pi/Desktop/logs/chronlog 2>&1

cd /
cd home/pi/Desktop/hab
sudo python hab.py