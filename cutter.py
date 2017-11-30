import ConfigParser
import threading
import serial

Config = ConfigParser.ConfigParser()
Config.read("./config.ini")
MAX_ALTITUDE = Config.getfloat('PositionBoundaries', 'Altitude')
MAX_LATITUDE = Config.getfloat('PositionBoundaries', 'MaxLatitude')
MIN_LATITUDE = Config.getfloat('PositionBoundaries', 'MinLatitude')
MAX_LONGITUDE = Config.getfloat('PositionBoundaries', 'MaxLongitude')
MIN_LONGITUDE = Config.getfloat('PositionBoundaries', 'MinLongitude')


class Cutter(threading.Thread):
    def __init__(self, cutter_queue):
        threading.Thread.__init__(self)
        self.ser = serial.Serial('/dev/ttyUSB0', 9600)
        self.cutter_queue = cutter_queue
        self.running = True


    def run(self):
        while self.running:
            self.checkPosition()

    def checkPosition(self):
        out_of_bounds = False
        fix = self.cutter_queue.get()
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

            self.cutter_queue.task_done()
        else:
            self.running = False
            self.cutter_queue.task_done()

    def cut(self):
        print 'Cutting!!!'
        command = '1'
        self.ser.write(command.encode('hex'))
