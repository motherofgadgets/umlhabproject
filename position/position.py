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

# TODO: Move this global variable outside this file?
gpsd = None
Config = ConfigParser.ConfigParser()
Config.read("../config.ini")
GPS_SLEEPTIME = Config.getfloat('TimingIntervals', 'Position')

# Global variables for this module only
CALLSIGN = "KC1HZL-7"
COMMENT = "Testing RaspPi + UV-5R"
SOUNDFILE = "packet.wav"


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
        while position.running:
            gpsd.next()


def get_fix():
    global gpsd
    while True:
        if isnan(gpsd.fix.time):
            print('No GPS data available.')
            time.sleep(1)
        else:
            fix = gpsd.fix
            fix.time = gpsd.utc
            break
    print('**********FIX***************')
    print('Time: {}'.format(fix.time))
    print('Latitude: {}'.format(fix.latitude))
    print('Longitude: {}'.format(fix.longitude))
    print('Course: {}'.format(fix.track))
    print('Speed: {}'.format(fix.speed))
    print('Altitude: {}'.format(fix.altitude))
    print('****************************')
    return fix


def format_string(fix, comment):
    # Time
    new_time = str(fix.time)
    time_day = new_time[8:10]
    time_hour = new_time[11:13]
    time_minute = new_time[14:16]
    time_str = "{}{}{}".format(time_day, time_hour, time_minute)

    # Latitude
    latitude = fix.latitude
    lat_str = str(latitude)
    latitude_degrees = int(lat_str[0:2])
    latitude_minutes = round(float(lat_str[2:]) * 60, 2)  # convert from decimal to minutes
    latmin_str = str(latitude_minutes).zfill(5)
    lat_str = str(latitude_degrees) + latmin_str

    # Longitude
    longitude = fix.longitude
    lon_str = str(longitude)
    lonbits = lon_str.split('.')
    longitude_degrees = abs(int(lonbits[0]))
    lonmin = '.' + lonbits[1]
    longitude_minutes = round(float(lonmin) * 60, 2)  # convert from decimal to minutes
    londay_str = str(int(longitude_degrees)).zfill(3)
    lonmin = "{0:.2f}".format(longitude_minutes)
    lonmin_str = str(lonmin).zfill(5)
    lon_str = londay_str + lonmin_str

    # Course
    course = round(fix.track)
    course_str = str(course).zfill(3)

    # Speed
    speed = round(fix.speed * 1.9438444924574)
    speed_str = str(speed).zfill(3)

    # Altitude
    altitude = round(fix.altitude * 3.2808)  # read altitude, convert to meters
    alt_str = str(int(altitude)).zfill(6)

    aprs_string = '/{}z{}N/{}W>{}/{}{}/A={}'.format(time_str, lat_str, lon_str, course_str, speed_str,
                                                    comment, alt_str)

    print('TimeDay: {}'.format(time_day))
    print('TimeHour: {}'.format(time_hour))
    print('TimeMinute: {}'.format(time_minute))

    print('Time: {}'.format(time_str))
    print('Latitude: {}'.format(lat_str))
    print('Longitude: {}'.format(lon_str))
    print('Course: {}'.format(course_str))
    print('Speed: {}'.format(speed_str))
    print('Altitude: {}'.format(alt_str))

    return aprs_string


def transmit(transmit_string):
    print('Transmitting beacon.')
    print(transmit_string)
    call(['aprs', '-c', CALLSIGN, '-o', SOUNDFILE, transmit_string])  # creates packet.wav
    call(['aplay', SOUNDFILE])  # broadcasts packet.wav


if __name__ == '__main__':
    position = Position()
    try:
        position.start()
        while True:
            new_fix = get_fix()
            new_string = format_string(new_fix, COMMENT)
            transmit(new_string)
            time.sleep(5)

    except (KeyboardInterrupt, SystemExit):  # when you press ctrl+c
        print "\nKilling Thread..."
        position.running = False
        position.join()  # wait for the thread to finish what it's doing
    print "Done.\nExiting."
