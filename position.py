# position.py
#
# This script runs indefinitely, pulling the GPS coordinates from the local gps daemon server
# It then converts the data to APRS format, creates an APRS soundfile and broadcasts
#
# This script is adapted from Super Simple APRS Position Reporter by Midnight Cheese
# http://midnightcheese.com/2015/12/super-simple-aprs-position-beacon/
# Position poller class is adapted from script by Dan Mandle http://dan.mandle.me
# http://www.danmandle.com/blog/getting-gpsd-to-work-with-python/
#

import ConfigParser
from gps import *
from subprocess import call
import threading

gpsd = None
Config = ConfigParser.ConfigParser()
Config.read("./config.ini")
GPS_SLEEPTIME = Config.getfloat('TimingIntervals', 'Position')


class Position(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        call(['sudo', 'gpsd', '/dev/ttyAMA0', '-F', '/var/run/gpsd.sock'])
        global gpsd
        gpsd = gps(mode=WATCH_ENABLE)
        self.current = None
        self.running = True

    def run(self):
        global gpsd
        while self.running:
            gpsd.next()


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

    def get_fix(self):
        global gpsd
        while True:
            if isnan(gpsd.fix.time) or gpsd.fix.latitude == 0:
                print('No GPS data available.')
                time.sleep(1)
            else:
                fix = {"time": gpsd.utc,
                       "latitude": gpsd.fix.latitude,
                       "longitude": gpsd.fix.longitude,
                       "course": gpsd.fix.track,
                       "speed": gpsd.fix.speed,
                       "altitude": gpsd.fix.altitude,
                       }
                print('**********FIX***************')
                print('Time: {}'.format(fix["time"]))
                print('Latitude: {}'.format(fix["latitude"]))
                print('Longitude: {}'.format(fix["longitude"]))
                print('Course: {}'.format(fix["course"]))
                print('Speed: {}'.format(fix["speed"]))
                print('Altitude: {}'.format(fix["altitude"]))
                print('****************************')
                self.log_queue.put(fix)
                self.aprs_queue.put(fix)
                self.cutter_queue.put(fix)
                break