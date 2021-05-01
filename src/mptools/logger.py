# -*- coding: utf-8 -*-

import logging
import sys
import tqdm

DEFAUT_LOGGERS = [
    "info:stdout"
]

class TqdmLoggingHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.tqdm.write(msg)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

def package_logger(PACKAGENAME, LOGGERS=DEFAUT_LOGGERS):
    """
    PACKAGENAME @string :
    LOGGERS @string[] :
    Returns: The configured logger
    """
    logger = logging.getLogger(PACKAGENAME)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    for item in LOGGERS:
        level, filename = item.split(":", 1)
        nlevel = getattr(logging, level.upper(), "DEBUG")
        if filename in ("stdout", "stderr"):
            handler = logging.StreamHandler(getattr(sys, filename))
        elif filename == 'progress':
            handler = TqdmLoggingHandler(level=nlevel)
        else:
            handler = logging.FileHandler(filename)
        handler.setFormatter(formatter)
        logger.setLevel(nlevel)
        logger.addHandler(handler)
    return logger
