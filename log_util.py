import logging


def get_logger(log_filename):
    logger = logging.getLogger("logger")
    if not logger.handlers:
        # create handlers and set level to debug
        ch = logging.StreamHandler()
        fh = logging.FileHandler(log_filename)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)5.5s - %(message)s')
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        # add to logger
        logger.addHandler(ch)
        logger.addHandler(fh)

    return logger

