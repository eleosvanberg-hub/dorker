"""Logging configuration with rotating file handler and console output."""

import logging
import sys
from logging.handlers import RotatingFileHandler


def setup_logger(name: str = "cern", log_file: str = "cern.log") -> logging.Logger:
    # Only attach handlers to the root "cern" logger once.
    # Child loggers (cern.search, cern.notifier, …) propagate up to it naturally.
    # Adding handlers to both parent and child causes every message to print twice.
    root = logging.getLogger("cern")
    if not root.handlers:
        root.setLevel(logging.INFO)
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(fmt)
        root.addHandler(ch)

        fh = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
        fh.setFormatter(fmt)
        root.addHandler(fh)

    return logging.getLogger(name)
