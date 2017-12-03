# hab.py
#
# by Danae Moss
#
# This script runs indefinitely, serving as the main control hub for the other modules.
# It sets up queues to handle communications between concurrently running modules, then boots up
# all modules. Upon keyboard interrupt or system exit, it shuts down all modules.
#

import position
import pos_logger
import aprs
import cutter
import sensors
import Queue


if __name__ == '__main__':

    # Sets up Communication Queues
    aprs_queue = Queue.Queue()
    log_queue = Queue.Queue()
    cutter_queue = Queue.Queue()

    # Initializes modules
    pos = position.Position()
    pos_helper = position.PositionHelper(log_queue, aprs_queue, cutter_queue)
    logger = pos_logger.PosLogger(log_queue)
    aprs = aprs.Aprs(aprs_queue)
    cutter = cutter.Cutter(cutter_queue)
    sensors = sensors.Sensors()

    try:
        # Starts module threads
        pos.start()
        pos_helper.start()
        logger.start()
        aprs.start()
        cutter.start()
        sensors.start()
        while True:
            pass  # Do nothing

    except (KeyboardInterrupt, SystemExit):  # when you press ctrl+c
        # Put poison pills in each Queue as a signal to shut down
        log_queue.put(None)
        aprs_queue.put(None)
        cutter_queue.put(None)

        # Shut down threads we have direct control over
        pos.running = False
        pos.join()
        print "\nKilling Position Thread..."
        sensors.running = False
        sensors.join()
        print "\nKilling Sensors Thread..."
        pos_helper.running = False
        pos_helper.join()

        # Shut down threads once they have completed all actions
        logger.join()
        print "\nKilling Log Thread..."
        aprs.join()
        print "\nKilling APRS Thread..."
        cutter.join()
        print "\nKilling Cutter Thread..."

        print "Done.\nExiting."
