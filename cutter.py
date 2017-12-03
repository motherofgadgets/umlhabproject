# cutter.py
#
# by Danae Moss
#
# This script runs indefinitely, receiving GPS coordinates through a queue from the position script
# It then checks to see if the position is still within boundaries set in the configurations
# If not, it sends a signal through serial to the cutter circuit to sever ties to the balloon
#

import ConfigParser
import threading
import serial

# Obtains user-defined boundaries through config file
Config = ConfigParser.ConfigParser()
Config.read("./config.ini")
MAX_ALTITUDE = Config.getfloat('PositionBoundaries', 'Altitude')
MAX_LATITUDE = Config.getfloat('PositionBoundaries', 'MaxLatitude')
MIN_LATITUDE = Config.getfloat('PositionBoundaries', 'MinLatitude')
MAX_LONGITUDE = Config.getfloat('PositionBoundaries', 'MaxLongitude')
MIN_LONGITUDE = Config.getfloat('PositionBoundaries', 'MinLongitude')


class Cutter(threading.Thread):
    # Initiates an instance of itself as a thread, sets to running
    def __init__(self, cutter_queue):
        threading.Thread.__init__(self)
        self.ser = serial.Serial('/dev/ttyUSB0', 9600)
        self.cutter_queue = cutter_queue
        self.running = True

    # Defines run sequence
    def run(self):
        while self.running:
            self.checkPosition()

    # Obtains Latitude, Longitude, and altitude from position module
    # Activates Cutter circuit if coordinates fall outside boundaries
    def checkPosition(self):
        out_of_bounds = False
        fix = self.cutter_queue.get()
        if fix:  # If value in queue is anything other than "None" Poison Pill
            altitude = fix["altitude"]
            latitude = fix["latitude"]
            longitude = abs(fix["longitude"])

            # Check if coordinates fall outside boundaries
            if altitude < MAX_ALTITUDE:
                if MIN_LATITUDE <= latitude <= MAX_LATITUDE:
                    if MIN_LONGITUDE <= longitude <= MAX_LONGITUDE:
                        pass
                    else:
                        print 'LONGITUDE OUT OF BOUNDS'
                        out_of_bounds = True
                else:
                    print 'LATITUDE OUT OF BOUNDS'
                    out_of_bounds = True
            else:
                print 'ALTITUDE OUT OF BOUNDS'
                out_of_bounds = True

            if out_of_bounds:
                print 'Out of bounds. Cutting balloon.'
                self.cut()
            else:
                print 'In bounds.'

            self.cutter_queue.task_done()  # Mark position item in queue as done
        else:  # Poison pill detected
            self.running = False
            self.cutter_queue.task_done()

    # Sends a hex signal of '1' to Cutter circuit to initiate cutting
    def cut(self):
        print 'Cutting!!!'
        command = '1'
        self.ser.write(command.encode('hex'))
