import position
import pos_logger
import aprs
import cutter
import sensors
import Queue


if __name__ == '__main__':

    aprs_queue = Queue.Queue()
    log_queue = Queue.Queue()
    cutter_queue = Queue.Queue()

    pos = position.Position()
    pos_helper = position.PositionHelper(log_queue, aprs_queue, cutter_queue)
    logger = pos_logger.PosLogger(log_queue)
    aprs = aprs.Aprs(aprs_queue)
    cutter = cutter.Cutter(cutter_queue)
    sensors = sensors.Sensors()

    try:
        pos.start()
        pos_helper.start()
        logger.start()
        aprs.start()
        cutter.start()
        sensors.start()
        while True:
            pass

    except (KeyboardInterrupt, SystemExit):  # when you press ctrl+c
        log_queue.put(None)
        aprs_queue.put(None)
        cutter_queue.put(None)

        pos.running = False
        pos.join()
        print "\nKilling Position Thread..."
        sensors.running = False
        sensors.join()
        print "\nKilling Sensors Thread..."
        pos_helper.running = False
        pos_helper.join()

        logger.join()
        print "\nKilling Log Thread..."
        aprs.join()
        print "\nKilling APRS Thread..."
        cutter.join()
        print "\nKilling Cutter Thread..."

        print "Done.\nExiting."
