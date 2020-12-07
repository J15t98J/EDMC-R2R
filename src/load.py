import logging
import os
from csv import DictReader
from logging import Logger
from typing import Optional

import myNotebook as nb

import tkinter as tk
import tkinter.filedialog
from tkinter import ttk

from config import appname
from theme import theme


LOG_LEVEL = logging.INFO

# TODO: FSDJump & SAAScanComplete


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
current_r2r: list = []
index: int = 0
root: tk.Frame
current_window: tk.Frame = None


def goto_screen(screen: tk.Frame):
    global current_window
    if current_window is not None:
        current_window.destroy()
    screen.grid(sticky=tk.E+tk.W)
    theme.update(screen)
    current_window = screen


def screen_init() -> tk.Frame:
    init = ttk.Frame(root)
    init.grid_columnconfigure(0, weight=1)
    ttk.Button(init, text="Load R2R file", command=load_csv).grid(sticky=tk.E+tk.W)
    return init


def screen_progress() -> tk.Frame:
    global index
    progress = ttk.Frame(root)
    progress.grid_columnconfigure(1, weight=1)

    # functions for prev/next buttons
    def prog_prev():
        global index
        index -= 1
        goto_screen(screen_progress())

    def prog_next():
        global index
        index += 1
        goto_screen(screen_progress())
    
    if current_r2r:
        system = current_r2r[index]
    
        # system page header ([<] curr/total [>] \nSystem Name)
        b_prev = ttk.Button(progress, text="<", command=prog_prev)
        b_prev.grid(row=0, column=0)
        b_next = ttk.Button(progress, text=">", command=prog_next)
        b_next.grid(row=0, column=2)
        ttk.Label(progress, text=f"{index+1}/{len(current_r2r)}").grid(row=0, column=1)
        ttk.Label(progress, text=system["name"]).grid(row=1, columnspan=3)
    
        # prevent cycling round off the end of the list
        if index == 0:
            b_prev.state(['disabled'])
        if index == len(current_r2r)-1:
            b_next.state(['disabled'])
    
        # a checkbox and label for each system body
        bodies_container = ttk.Frame(progress)
        bodies_container.grid(row=2, columnspan=3)
        current_row = 0
        for body in system["bodies"]:
            body_frame = ttk.Frame(bodies_container)
            body_frame.grid(row=current_row, sticky="W")
            ttk.Checkbutton(body_frame).pack(side="left")
            ttk.Label(body_frame, text=body).pack(side="left")
            current_row = current_row + 1

    return progress


def screen_complete() -> tk.Frame:
    complete = ttk.Frame(root)
    # TODO: put something on this page
    return complete


def load_csv():
    global current_r2r
    current_r2r = []
    
    log.debug("Loading new CSV...")
    
    with tk.filedialog.askopenfile(filetypes=[('CSV files', '*.csv')]) as csvfile:
        # convert (system -> body) into (UNIQ system -> [body])
        for row in DictReader(csvfile):
            system = row['System Name']
            # remove the system name from the body name
            # TODO: replace .replace with .removesuffix when on py3.9
            body = row['Body Name'].replace(system, "").lstrip()
            
            if current_r2r and system == current_r2r[-1]['name']:
                # same system as the last row; add to previous entry
                current_r2r[-1]['bodies'].append(body)
            else:
                # different system; start a new entry
                current_r2r.append({'name': system, 'bodies': [body]})

    log.debug("CSV load complete.")
    goto_screen(screen_progress())


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
    global root
    root = ttk.Frame(parent)
    root.grid_columnconfigure(0, weight=1)

    ttk.Label(root, text="Road 2 Riches", anchor=tk.CENTER,).grid(sticky=tk.E+tk.W)
    goto_screen(screen_init())
    return root
