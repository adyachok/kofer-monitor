import logging


def get_logger(name):
    logger = logging.getLogger(name)
    FORMAT = '%(asctime)s.%(msecs)03d %(levelname)s ' \
             '%(module)s - %(funcName)s: %(message)s'
    DATEFMT = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(fmt=FORMAT, datefmt=DATEFMT)
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)
    logger.setLevel(logging.INFO)
    return logger
