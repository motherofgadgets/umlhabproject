# position.py
#
# This script runs indefinitely, pulling the GPS coordinates from the local gps daemon server
# It then converts the data to APRS format, creates an APRS soundfile and broadcasts
#
# This script is adapted from Super Simple APRS Position Reporter by Midnight Cheese
# http://midnightcheese.com/2015/12/super-simple-aprs-position-beacon/
#
# This script assumes there is a gpsd daemon running. Before running this script, enter
#    sudo gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock
# in the console


import ConfigParser
import json
import requests
import time
from subprocess import call


Config = ConfigParser.ConfigParser()
Config.read("../config.ini")
GPS_SLEEPTIME = Config.getfloat('TimingIntervals', 'Position')

# Global variables for this module only
CALLSIGN = "KC1HZL-7"
COMMENT = "Testing RaspPi + UV-5R"
SOUNDFILE = "packet.wav"


def get_data():
    local_url = requests.get("http://localhost/gpsd.php?op=json")  # get text from gpsd server
    data = json.loads(local_url.text)
    return data


def get_aprs_string(data, comment):
    # Time
    new_time = data['tpv'][0]['time']  # read time from JSON
    time_day = new_time[8:10]
    time_hour = new_time[11:13]
    time_minute = new_time[14:16]

    # Latitude
    latitude = str(data['tpv'][0]['lat'])  # read latitude from JSON
    latitude_degrees = latitude[0:2]
    latitude_minutes = round(float(latitude[2:]) * 60, 2)  # convert from decimal to minutes

    # Longitude
    longitude = str(data['tpv'][0]['lon'])  # read longitude from JSON
    lonbits = longitude.split('.')
    longitude_degrees = lonbits[0]
    lonmin = '.' + lonbits[1]
    longitude_minutes = round(float(lonmin) * 60, 2)  # convert from decimal to minutes

    # Course
    course = round(data['tpv'][0]['track'])  # read course from JSON

    # Speed
    speed = round(data['tpv'][0]['speed'] * 1.9438444924574)  # read speed from JSON

    # Altitude
    altitude = round(data['tpv'][0]['alt'] * 3.2808)  # read altitude from JSON, convert to meter

    time_str = time_day + time_hour + time_minute

    latmin_str = str(latitude_minutes).zfill(5)
    lat_str = str(latitude_degrees) + latmin_str

    londay_str = str(int(longitude_degrees)).zfill(3)
    lonmin = "{0:.2f}".format(longitude_minutes)
    lonmin_str = str(lonmin).zfill(5)
    lon_str = londay_str + lonmin_str

    course_str = str(course).zfill(3)

    speed_str = str(speed).zfill(3)

    alt_str = str(int(altitude)).zfill(6)

    aprs_string = '"/{}z{}N/{}W>{}/{}{}/A={}"'.format(time_str, lat_str, lon_str, course_str, speed_str,
                                                      comment, alt_str)

    print('Time: {}'.format(time_str))
    print('Latitude: {}'.format(lat_str))
    print('Longitude: {}'.format(lon_str))
    print('Course: {}'.format(course_str))
    print('Speed: {}'.format(speed_str))
    print('Altitude: {}'.format(alt_str))

    return aprs_string


def transmit(aprs_string):
    print('Transmitting beacon.')
    call(['aprs', '-c', CALLSIGN, '-o', SOUNDFILE, aprs_string])  # creates packet.wav
    time.sleep(2)
    call(['aplay', SOUNDFILE])  # broadcasts packet.wav


while True:
    try:
        new_data = get_data()
        new_aprs_string = get_aprs_string(new_data, COMMENT)
    except (KeyError, IndexError):
        print('No GPS data available.')
    else:
        print('Read GPS')
        transmit(new_aprs_string)
    time.sleep(GPS_SLEEPTIME)
