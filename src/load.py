import logging
import os
from csv import DictReader
from logging import Logger
from typing import Optional

import myNotebook as nb
import tkinter as tk

from config import appname


LOG_LEVEL = logging.INFO


def setup_logging() -> Logger:
    logger = logging.getLogger(f'{appname}.{plugin_name}')
    logger.setLevel(LOG_LEVEL)  # So logger.info(...) is equivalent to print()
    
    if not logger.hasHandlers():
        logger_channel = logging.StreamHandler()
        logger_formatter = logging.Formatter(f'%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d:%('
                                             f'funcName)s: %(message)s')
        logger_formatter.default_time_format = '%Y-%m-%d %H:%M:%S'
        logger_formatter.default_msec_format = '%s.%03d'
        logger_channel.setFormatter(logger_formatter)
        logger.addHandler(logger_channel)
        
    return logger


plugin_name: str = os.path.basename(os.path.dirname(__file__))
log = setup_logging()


def plugin_start3(plugin_dir: str) -> str:
    # TODO: any init required?
    return "EDMC-R2R"


def plugin_prefs(parent: nb.Notebook, cmdr: str, is_beta: bool) -> Optional[tk.Frame]:
    # TODO: plugin preferencees tab in the settings window
    pass


def prefs_changed(cmdr: str, is_beta: bool) -> None:
    # TODO: plugin preferences
    pass


def plugin_app(parent: tk.Frame) -> tk.Frame:
    # TODO: main UI
    pass
