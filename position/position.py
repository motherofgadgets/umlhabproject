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
import Queue
import serial

gpsd = None
Config = ConfigParser.ConfigParser()
Config.read("../config.ini")
GPS_SLEEPTIME = Config.getfloat('TimingIntervals', 'Position')
MAX_ALTITUDE = Config.getfloat('PositionBoundaries', 'Altitude')
MAX_LATITUDE = Config.getfloat('PositionBoundaries', 'MaxLatitude')
MIN_LATITUDE = Config.getfloat('PositionBoundaries', 'MinLatitude')
MAX_LONGITUDE = Config.getfloat('PositionBoundaries', 'MaxLongitude')
MIN_LONGITUDE = Config.getfloat('PositionBoundaries', 'MinLongitude')

# Global variables for this module only
CALLSIGN = "KC1HZL-7"
COMMENT = "Testing RaspPi + UV-5R"
SOUNDFILE = "packet.wav"
FILENAME = time.strftime('%Y-%m-%d_%H%M%S')
LOG_FREQUENCY = Config.get('TimingIntervals', 'PositionLogging')


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


class PositionHelper(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True

    def run(self):
        global gpsd
        while pos_helper.running:
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
                log_queue.put(fix)
                aprs_queue.put(fix)
                cutter_queue.put(fix)
                break


class Aprs(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True

    def run(self):
        while self.running:
            self.format_string(COMMENT)

    def format_string(self, comment):
        fix = aprs_queue.get()

        if fix:
            # Time
            new_time = str(fix["time"])
            time_day = new_time[8:10]
            time_hour = new_time[11:13]
            time_minute = new_time[14:16]
            time_str = "{}{}{}".format(time_day, time_hour, time_minute)

            # Latitude
            latitude = fix["latitude"]
            lat_str = str(latitude)
            latitude_degrees = int(lat_str[0:2])
            latitude_minutes = round(float(lat_str[2:]) * 60, 2)  # convert from decimal to minutes
            latmin_str = str(latitude_minutes).zfill(5)
            lat_str = str(latitude_degrees) + latmin_str

            # Longitude
            longitude = fix["longitude"]
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
            course = round(fix["course"])
            course_str = str(course).zfill(3)

            # Speed
            speed = round(fix["speed"] * 1.9438444924574)
            speed_str = str(speed).zfill(3)

            # Altitude
            altitude = round(fix["altitude"] * 3.2808)  # read altitude, convert to meters
            alt_str = str(int(altitude)).zfill(6)

            aprs_string = '/{}z{}N/{}W>{}/{}{}/A={}'.format(time_str, lat_str, lon_str, course_str, speed_str,
                                                            comment, alt_str)
            #
            # print('TimeDay: {}'.format(time_day))
            # print('TimeHour: {}'.format(time_hour))
            # print('TimeMinute: {}'.format(time_minute))

            # print('Time: {}'.format(time_str))
            # print('Latitude: {}'.format(lat_str))
            # print('Longitude: {}'.format(lon_str))
            # print('Course: {}'.format(course_str))
            # print('Speed: {}'.format(speed_str))
            # print('Altitude: {}'.format(alt_str))

            aprs_queue.task_done()

            self.transmit(aprs_string)
        else:
            self.running = False
            print('APRS running = False')
            aprs_queue.task_done()

    def transmit(self, transmit_string):
        print('Transmitting beacon.')
        print(transmit_string)
        call(['aprs', '-c', CALLSIGN, '-o', SOUNDFILE, transmit_string])  # creates packet.wav
        call(['aplay', SOUNDFILE])  # broadcasts packet.wav


class PosLogger(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True

    def run(self):
        while self.running:
            self.log_data()

    def log_data(self):
        log_fix = log_queue.get()
        if log_fix:
            if isinstance(log_fix["time"], float):
                log_time = time.strftime('%Y-%m-%dT%H:%M:%S.%000Z', time.gmtime(log_fix["time"]))
                print('fixing time')
            else:
                log_time = log_fix["time"]
            print('Logging time: {}'.format(log_time))
            pos_data = [log_time,
                        log_fix["latitude"],
                        log_fix["longitude"],
                        log_fix["course"],
                        log_fix["speed"],
                        log_fix["altitude"]]
            output_string = ",".join(str(value) for value in pos_data)
            batch_data.append(output_string)
            log_queue.task_done()
        else:
            self.running = False
            log_queue.task_done()


class Cutter(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True
        self.ser = serial.Serial('/dev/ttyUSB0', 9600)

    def run(self):
        while self.running:
            self.checkPosition()

    def checkPosition(self):
        out_of_bounds = False
        fix = cutter_queue.get()
        if fix:
            altitude = fix["altitude"]
            latitude = fix["latitude"]
            longitude = abs(fix["longitude"])
            # print 'CUTTER: Max Altitude is {}'.format(MAX_ALTITUDE)
            # print 'CUTTER: Altitude = {}, type {}'.format(altitude, type(altitude))
            # print 'CUTTER: Max Latitude is {}, Min Latitude is {}'.format(MAX_LATITUDE, MIN_LATITUDE)
            # print 'CUTTER: Longitude = {}, type {}'.format(latitude, type(latitude))
            # print 'CUTTER: Max Longitude is {}, Min Longitude is {}'.format(MAX_LONGITUDE, MIN_LONGITUDE)
            # print 'CUTTER: Longitude = {}, type {}'.format(longitude, type(longitude))

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

            cutter_queue.task_done()
        else:
            self.running = False
            cutter_queue.task_done()

    def cut(self):
        print 'Cutting!!!'
        command = '1'
        self.ser.write(command.encode('hex'))


def file_setup(filename):
    header = ["timestamp", "Latitude", "Longitude", "Course", "Speed", "Altitude"]

    with open(filename, "w") as f:
        f.write(",".join(str(value) for value in header) + "\n")


if __name__ == '__main__':
    batch_data = []

    if FILENAME == "":
        filename = "logs/testLog.csv"
    else:
        filename = 'logs/{}.csv'.format(FILENAME)

    file_setup(filename)
    position = Position()
    pos_helper = PositionHelper()
    logger = PosLogger()
    aprs = Aprs()
    cutter = Cutter()

    aprs_queue = Queue.Queue()
    log_queue = Queue.Queue()
    cutter_queue = Queue.Queue()
    try:
        position.start()
        pos_helper.start()
        logger.start()
        aprs.start()
        cutter.start()
        while True:
            if len(batch_data) >= LOG_FREQUENCY:
                print("Writing to file..")
                with open(filename, "a") as f:
                    for line in batch_data:
                        f.write(line + "\n")
                    batch_data = []
    except (KeyboardInterrupt, SystemExit):  # when you press ctrl+c
        pos_helper.running = False
        position.running = False
        pos_helper.join()
        print "\nKilling Position Helper Thread..."
        position.join()
        print "\nKilling Position Thread..."
        log_queue.put(None)
        aprs_queue.put(None)
        cutter_queue.put(None)
        logger.join()
        print "\nKilling Log Thread..."
        aprs.join()
        print "\nKilling APRS Thread..."
        cutter.join()
        print "\nKilling Cutter Thread..."

    print "Done.\nExiting."
