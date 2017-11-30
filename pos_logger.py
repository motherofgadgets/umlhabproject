import ConfigParser
from gps import *
import threading
import os

Config = ConfigParser.ConfigParser()
Config.read("./config.ini")
FILEPATH = 'position_logs/'
FILENAME = time.strftime('%Y-%m-%d_%H%M%S')
LOG_FREQUENCY = Config.getfloat('TimingIntervals', 'PositionLogging')


class PosLogger(threading.Thread):
    def __init__(self, log_queue):
        threading.Thread.__init__(self)
        self.log_queue = log_queue
        self.batch_data = []

        if not os.path.exists(FILEPATH):
            os.makedirs(FILEPATH)

        if FILENAME == "":
            self.filename = "{}testLog.csv".format(FILEPATH)
        else:
            self.filename = '{}{}.csv'.format(FILEPATH, FILENAME)

        file_setup(self.filename)
        self.running = True

    def run(self):
        while self.running:
            self.log_data()
            if len(self.batch_data) >= LOG_FREQUENCY:
                print("Writing to file..")
                with open(self.filename, "a") as f:
                    for line in self.batch_data:
                        f.write(line + "\n")
                    self.batch_data = []

    def log_data(self):
        log_fix = self.log_queue.get()
        if log_fix:
            if isinstance(log_fix["time"], float):
                log_time = time.strftime('%Y-%m-%dT%H:%M:%S.%000Z', time.gmtime(log_fix["time"]))
                print('fixing time')
            else:
                log_time = log_fix["time"]
            # print('Logging time: {}'.format(log_time))
            pos_data = [log_time,
                        log_fix["latitude"],
                        log_fix["longitude"],
                        log_fix["course"],
                        log_fix["speed"],
                        log_fix["altitude"]]
            output_string = ",".join(str(value) for value in pos_data)
            print 'Logging line: {}'.format(output_string)
            self.batch_data.append(output_string)
            self.log_queue.task_done()
        else:
            self.running = False
            self.log_queue.task_done()

def file_setup(filename):
    header = ["timestamp", "Latitude", "Longitude", "Course", "Speed", "Altitude"]

    with open(filename, "w") as f:
        f.write(",".join(str(value) for value in header) + "\n")