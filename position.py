# position.py
#
# by Danae Moss
#
# This script runs indefinitely, pulling the GPS coordinates from the local gps daemon server
# It then converts the data to a dictionary and passes it to other modules through queues
#
# Position poller/helper classes are adapted from script by Dan Mandle http://dan.mandle.me
# License: GPL 2.0
# http://www.danmandle.com/blog/getting-gpsd-to-work-with-python/
#

import ConfigParser
from gps import *  # Using GPSD library from http://catb.org/gpsd/
from subprocess import call
import threading

gpsd = None  # setting the global variable
Config = ConfigParser.ConfigParser()
Config.read("./config.ini")
# Obtains user-defined position frequency through config file
GPS_SLEEPTIME = Config.getfloat('TimingIntervals', 'Position')


class Position(threading.Thread):

    def __init__(self):
        # Initiates an instance of itself as a thread, sets to running
        threading.Thread.__init__(self)
        call(['sudo', 'gpsd', '/dev/ttyAMA0', '-F', '/var/run/gpsd.sock'])  # Initiates gpsd server
        global gpsd  # bring it in scope
        gpsd = gps(mode=WATCH_ENABLE)  # starting the stream of info
        self.current = None
        self.running = True

    def run(self):
        # Defines run sequence
        global gpsd
        while self.running:
            gpsd.next()  # this will continue to loop and grab EACH set of gpsd info


class PositionHelper(threading.Thread):
    def __init__(self, log_queue, aprs_queue, cutter_queue):
        threading.Thread.__init__(self)
        self.log_queue = log_queue
        self.aprs_queue = aprs_queue
        self.cutter_queue = cutter_queue
        self.running = True

    def run(self):
        global gpsd
        while self.running:
            self.get_fix()
            time.sleep(GPS_SLEEPTIME)

    @staticmethod
    def verify(gpsd):
        if isnan(gpsd.fix.time) \
                or isnan(gpsd.fix.latitude) \
                or isnan(gpsd.fix.longitude) \
                or isnan(gpsd.fix.altitude):
            return False
        elif gpsd.fix.latitude == 0 \
                or gpsd.fix.longitude == 0 \
                or gpsd.fix.longitude == 0:
            return False
        else:
            return True

    def get_fix(self):
        global gpsd
        while True:
            # It may take a second or two to get good data
            if not self.verify(gpsd):
                print('No GPS data available.')
                time.sleep(1)
            else:
                # Place coordinates into dictionary object
                fix = {"time": gpsd.utc,  # Time is in UTC format
                       "latitude": gpsd.fix.latitude,  # Latitude is in degrees decimal format
                       "longitude": gpsd.fix.longitude,  # Longitude is in degrees decimal format
                       "course": gpsd.fix.track,  # course is in degrees true format
                       "speed": gpsd.fix.speed,  # TODO: Get units for speed
                       "altitude": gpsd.fix.altitude,  # Altitude is in meters
                       }
                # Uncomment in order to see values
                # print('**********FIX***************')
                # print('Time: {}'.format(fix["time"]))
                # print('Latitude: {}'.format(fix["latitude"]))
                # print('Longitude: {}'.format(fix["longitude"]))
                # print('Course: {}'.format(fix["course"]))
                # print('Speed: {}'.format(fix["speed"]))
                # print('Altitude: {}'.format(fix["altitude"]))
                # print('****************************')

                # Pass dictionary object to other modules
                self.log_queue.put(fix)
                self.aprs_queue.put(fix)
                self.cutter_queue.put(fix)
                break

