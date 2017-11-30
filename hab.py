import position
import pos_logger
import aprs
import cutter
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

    try:
        pos.start()
        pos_helper.start()
        logger.start()
        aprs.start()
        cutter.start()
        while pos.running:
            pass

    except (KeyboardInterrupt, SystemExit):  # when you press ctrl+c
        log_queue.put(None)
        aprs_queue.put(None)
        cutter_queue.put(None)

        pos.running = False
        pos.join()
        print "\nKilling Position Thread..."
        pos_helper.running = False
        pos_helper.join()

        logger.join()
        print "\nKilling Log Thread..."
        aprs.join()
        print "\nKilling APRS Thread..."
        cutter.join()
        print "\nKilling Cutter Thread..."

        print "Done.\nExiting."
