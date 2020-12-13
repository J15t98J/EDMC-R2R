import logging
import os

from csv import DictReader
from logging import Logger
from tkinter import *
from tkinter import filedialog
from typing import Optional, Dict, Any

import myNotebook as nb
from config import appname
from theme import theme
import timeout_session

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
current_r2r: list = []
index: int = 0
root: Frame
current_window: Frame = None
checkboxes = {}


def goto_screen(screen: Frame):
    global current_window
    if current_window is not None:
        current_window.destroy()
    screen.grid(sticky=E+W)
    theme.update(screen)
    current_window = screen


def screen_init() -> Frame:
    init = Frame(root)
    init.grid_columnconfigure(0, weight=1)
    Button(init, text="Load R2R file", command=load_csv).grid(sticky=E+W)
    return init


def screen_progress() -> Frame:
    global index, checkboxes
    progress = Frame(root)
    progress.grid_columnconfigure(1, weight=1)
    checkboxes = {}

    # functions for prev/next buttons
    def prog_prev():
        global index
        index -= 1
        goto_screen(screen_progress())
    
    def prog_next():
        global index
        index += 1
        goto_screen(screen_progress())
    
    def mark_complete(body_name: str):
        checkboxes[body_name]['label']['foreground'] = 'green'
        
        # if all the checkboxes are checked, move to the next page
        bools = map(lambda x: x['state'].get(), checkboxes.values())
        if all(bools): prog_next()

    if current_r2r:
        system = current_r2r[index]
        root.clipboard_clear()
        root.clipboard_append(system['name'])

        r = timeout_session.new_session().get("https://www.edsm.net/api-system-v1/bodies",
                                              params={'systemName': system['name']})
        edsm_data = r.json()["bodies"]
        body_types = {}
        if edsm_data:
            for edsm_body in edsm_data:
                body_types[edsm_body["name"]] = edsm_body["subType"].lower()
    
        # system page header ([<] curr/total [>] \nSystem Name)
        b_prev = Button(progress, text="<", width=8, command=prog_prev)
        b_prev.grid(row=0, column=0)
        b_next = Button(progress, text=">", width=8, command=prog_next)
        b_next.grid(row=0, column=2)
        Label(progress, text=f"{index+1}/{len(current_r2r)}").grid(row=0, column=1)
        Label(progress, text=system["name"]).grid(row=1, columnspan=3)
    
        # prevent cycling round off the end of the list
        if index == 0:
            b_prev['state'] = DISABLED
        if index == len(current_r2r)-1:
            b_next['state'] = DISABLED
    
        # a checkbox and label for each system body
        bodies_container = Frame(progress)
        bodies_container.grid(row=2, columnspan=3)
        current_row = 0
        for body in system["bodies"]:
            fullname = f"{system['name']} {body}"
            
            body_frame = Frame(bodies_container)
            body_frame.grid(row=current_row, sticky="W")

            if fullname in body_types:
                labeltext = f"{body} ({body_types[fullname]})"
            else:
                labeltext = body

            state = BooleanVar()
            state.trace_add("write", lambda *unused, x=body: mark_complete(x))
            Checkbutton(body_frame, variable=state, command=lambda x=body: mark_complete(x)).pack(side="left")
            label = Label(body_frame, text=labeltext)
            label.pack(side="left")

            checkboxes[body] = {'state': state, 'label': label}
            current_row = current_row + 1
            theme.update(body_frame)

    return progress


def screen_complete() -> Frame:
    complete = Frame(root)
    # TODO: put something on this page
    return complete


def load_csv():
    global current_r2r
    current_r2r = []
    
    log.debug("Loading new CSV...")
    
    with filedialog.askopenfile(filetypes=[('CSV files', '*.csv')]) as csvfile:
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


def plugin_prefs(parent: nb.Notebook, cmdr: str, is_beta: bool) -> Optional[Frame]:
    # TODO: plugin preferencees tab in the settings window
    pass


def prefs_changed(cmdr: str, is_beta: bool) -> None:
    # TODO: plugin preferences
    pass


def plugin_app(parent: Frame) -> Frame:
    global root
    root = Frame(parent)
    root.grid_columnconfigure(0, weight=1)

    Label(root, text="Road 2 Riches", anchor=CENTER).grid(sticky=E+W)
    goto_screen(screen_init())
    return root


def journal_entry(cmdr: str, is_beta: bool, system: str, station: str, entry: Dict[str, Any],
                  state: Dict[str, Any]) -> None:
    if entry['event'] == 'SAAScanComplete':
        log.info(entry)
        if current_r2r:
            current_target_system = current_r2r[index]['name']
            for (k, v) in checkboxes.items():
                log.info(f"lookingfor: {current_target_system} {k}")
                if entry['BodyName'] == f"{current_target_system} {k}":
                    v['state'].set(True)
                    break
