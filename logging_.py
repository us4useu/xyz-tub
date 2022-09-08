import logging


LOGGING_FORMAT = "[%(asctime)s][%(name)s][%(levelname)s] %(message)s"
ERROR_FORMAT = LOGGING_FORMAT + " (%(filename)s:%(lineno)d)"
OUTPUT_FILE = "xyztank.log"
CLOG_LEVEL = logging.INFO
LOG_FILE_LEVEL = logging.DEBUG
LOGGER_LEVEL = logging.DEBUG


class LoggerFactory:

    def __init__(self, output_file):
        self.output_file = output_file

    # Logging
    def get_logger(self, name):
        logger = logging.getLogger(name)
        formatter = logging.Formatter(LOGGING_FORMAT)
        # Log file
        file_handler = logging.FileHandler(self.output_file)
        file_handler.setLevel(LOG_FILE_LEVEL)
        # Clog
        console_handler = logging.StreamHandler()
        console_handler.setLevel(CLOG_LEVEL)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        # add the handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(LOGGER_LEVEL)
        return logger


LOGGER_FACTORY = LoggerFactory(output_file=OUTPUT_FILE)


def get_logger(name: str):
    """
    Creates a new instance of logger with a given name.
    """
    return LOGGER_FACTORY.get_logger(name)

