from multiprocessing import Process
from datetime import datetime
import logging
import logging.handlers
import pytz
import sys, os, signal
import json


class CustomLogger(Process):
    """
    A multiprocessing logger that listens to a message queue and writes logs to different files (app.log and error.log).
    Runs in a separate process to handle logging asynchronously.
    """
    def __init__(self):
        """
        Initializes the CustomLogger process.
        """
        Process.__init__(self)

    @staticmethod
    def process(messageQueue, evt, debugLogLevel):
        """
        Main logging loop that receives log messages from a multiprocessing queue and writes them
        to appropriate log files.

        Args:
            messageQueue (multiprocessing.Queue): The queue where log messages are sent as dictionaries.
            evt (multiprocessing.Event): An event to signal when the process should stop.
            debugLogLevel (bool): Whether to use DEBUG level logging (True) or INFO (False).

        Expected message format in the queue:
        {
            "type": "INFO" | "DEBUG" | "ERROR" | etc.,
            "log": "app" | "error",
            "message": "The message to log"
        }

        Returns:
            None
        """
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        logLevel = logging.INFO
        if debugLogLevel == True:
            logLevel = logging.DEBUG
        formatter = Formatter(fmt="%(asctime)s [%(name)s] %(levelname)s %(message)s")


        app_logger = logging.getLogger("APP")
        hdlr_app = logging.handlers.WatchedFileHandler("logs/app.log")
        hdlr_app.setFormatter(formatter)
        app_logger.setLevel(logLevel)
        app_logger.addHandler(hdlr_app)
        app_logger.log(
            logging.INFO,
            f"+++++++++++++++++ STARTING APP - log Level: {logLevel} +++++++++++++++++",
        )
        app_logger.log(
            logging.INFO,
            f"[LOGGER] Process: {os.getpid()}",
        )


        error_logger = logging.getLogger("ERROR")
        hdlr_error = logging.handlers.WatchedFileHandler("logs/error.log")
        hdlr_error.setFormatter(formatter)
        error_logger.setLevel(logLevel)
        error_logger.addHandler(hdlr_error)
        error_logger.log(
            logging.INFO,
            f"+++++++++++++++++ STARTING APP - log Level: {logLevel} +++++++++++++++++",
        )

        try:
            while not evt.is_set():
                payload = messageQueue.get()  # type: ignore
                level = eval(f"logging.{payload['type'].upper()}")
                fichierLog = payload["log"].lower()
                exec(f'{fichierLog}_logger.log({level}, payload["message"])')
            app_logger.log(
                logging.INFO,
                "+++++++++++++++++ STOPPING APP FROM LOGGER +++++++++++++++++",
            )
        except Exception as ex:
            app_logger.log(logging.ERROR, ex)


class Formatter(logging.Formatter):
    """
    Custom logging formatter that uses a timezone-aware datetime (Europe/Paris) in log timestamps.
    """

    def converter(self, timestamp):
        """
        Converts a UNIX timestamp into a timezone-aware datetime.

        Args:
            timestamp (float): The UNIX timestamp.

        Returns:
            datetime: A timezone-aware datetime object.
        """
        dt = datetime.fromtimestamp(timestamp, tz=pytz.timezone("Europe/Paris"))
        return dt

    def formatTime(self, record, datefmt=None):
        """
        Formats the log record's creation time using the custom timezone-aware converter.

        Args:
            record (logging.LogRecord): The log record.
            datefmt (str, optional): A custom format string.

        Returns:
            str: A formatted time string.
        """
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            try:
                s = dt.isoformat(timespec="milliseconds")
            except TypeError:
                s = dt.isoformat()
        return s

