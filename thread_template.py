import threading
import signal
import time
import logging

logging.basicConfig(level=logging.INFO)

def background_thread(exit_event):
    while not exit_event.is_set():
        # do something here, like counting
        logging.info("Counting...")
        time.sleep(1)  # sleep for 1 second
    logging.info("Background thread received exit signal. Exiting...")

def signal_handler(sig, frame):
    logging.info("Signal received. Sending exit signal to background thread...")
    exit_event.set()
    raise KeyboardInterrupt

def create_thread():
    # create an exit event shared between the two threads
    global exit_event
    exit_event = threading.Event()

    # create a background thread
    bg_thread = threading.Thread(target=background_thread, args=(exit_event,))
    bg_thread.start()

    # register a signal handler for SIGINT (Ctrl-C) and SIGTERM (kill)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # do some work in the main thread
    try:
        while True:
            logging.info("Main thread is running...")
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Exiting program due to user interrupt...")
        exit_event.set()

    # wait for the background thread to exit
    bg_thread.join()
    logging.info("Background thread has exited. Exiting create_thread()...")

if __name__ == '__main__':
    create_thread()
    logging.info("Exiting main thread...")
