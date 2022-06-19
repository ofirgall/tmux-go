#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
# PYZSHCOMPLETE_OK


# NOTE: sessions window title must have "tmux-go-session:{session}"

from typing import Optional
import pyzshcomplete
import argcomplete
import argparse
import subprocess
import os
import re
from os import path
from taskw import TaskWarrior
import session_history

class TmuxGoMultipleDesktops(Exception):
    def __init__(self, message):
        super().__init__(message)

class TmuxGoSessioNotFound(Exception):
    def __init__(self, message):
        super().__init__(message)

class TmuxGoActiveSessionNotFound(Exception):
    def __init__(self, message):
        super().__init__(message)

def get_last_desktop() -> int:
    return int(subprocess.check_output(['wmctrl', '-d']).splitlines()[-1].split(b' ')[0])

def goto_desktop(desktop_id: int):
    subprocess.check_call(['wmctrl', '-s', str(desktop_id)])

def new_terminal_with_session(session: str, desktop_id: int, go_after_create: bool):
    shell = subprocess.check_output(['echo $SHELL'], shell=True).decode().strip()
    subprocess.Popen(['/usr/bin/x-terminal-emulator', '-t', f'tmux-go-session:{session}', '-e', shell, '-c', f'export OPEN_TMUX_SESSION={session}; export OPEN_AT_DESK={desktop_id}; zsh -i'], preexec_fn=os.setpgrp)

    if go_after_create:
        goto_desktop(desktop_id)

def get_current_desktop() -> int:
    desktops = subprocess.check_output(['wmctrl', '-d']).splitlines()
    for desktop in desktops:
        desktop_parts = desktop.split()
        if desktop_parts[1] == b'*':
            return int(desktop_parts[0])
    raise Exception('Not active desktop found!')

def get_desktop_with_session(session: str) -> int:
    window_title = f'tmux-go-session:{session}'
    windows = subprocess.check_output(['wmctrl', '-l']).decode()

    if window_title not in windows:
        raise TmuxGoSessioNotFound('Active Session Window not Found')

    windows_with_title = [win for win in windows.splitlines() if window_title in win]
    if len(windows_with_title) != 1:
        raise TmuxGoMultipleDesktops('Found multiple windows with the same session title')

    desktop_id = windows_with_title[0].split()[1]
    return int(desktop_id)

def get_active_session_in_desktop(desktop_id: int) -> str:
    windows = subprocess.check_output(['wmctrl', '-l']).splitlines()

    for window in windows:
        parts = window.decode().split()
        desk = parts[1]
        window_title = ' '.join(parts[3:])
        if int(desk) == desktop_id:
            match = re.match(r'.*tmux-go-session:(.+?)($|\s)', window_title, re.DOTALL)
            if match is None:
                continue

            return match.group(1)

    raise TmuxGoActiveSessionNotFound('Active Session Not Found')

def go_to_workspace(session: Optional[str], add_to_hist=True, reset_in_last=True) -> bool:
    # Dont jump
    if session is None:
        return True

    try:
        current_session = get_active_session_in_desktop(get_current_desktop())
        if session == current_session: # Don't jump if target session is the active
            return True

        if add_to_hist:
            session_history.add(current_session, reset_in_last)
    except TmuxGoActiveSessionNotFound:
        pass

    subprocess.check_call(['wmctrl', '-s', str(get_desktop_with_session(session))])
    return True

def go_to_session(session: str):
    try:
        go_to_workspace(session)
    except TmuxGoSessioNotFound:
        new_terminal_with_session(session, get_last_desktop(), True)

def go_to_session_in_task(task_id: str):
    warrior = TaskWarrior()
    task = warrior.get_task(uuid=task_id)[1]

    for annotation in task['annotations']:
        desc = annotation['description']
        if desc.startswith('tmux:'):
            go_to_session(desc[len('tmux:'):])
            break

def main():
    sessions = subprocess.check_output(['tmux', 'list-sessions', '-F', '#S']).decode().splitlines()
    # import IPython
    # IPython.embed()

    parser = argparse.ArgumentParser('Go to Tmux Session')

    parser.add_argument('-s', '--session', choices=sessions, default=None)
    parser.add_argument('-t', '--task', type=str)
    parser.add_argument('--last', action='store_true')
    parser.add_argument('--prev', action='store_true')
    parser.add_argument('--next', action='store_true')

    argcomplete.autocomplete(parser)
    pyzshcomplete.autocomplete(parser)

    args = parser.parse_args()

    if args.last:
        go_to_workspace(session_history.last(), add_to_hist=True)
    elif args.prev:
        go_to_workspace(session_history.prev(), add_to_hist=False)
    elif args.next:
        go_to_workspace(session_history.next(), add_to_hist=False)
    elif args.session:
        go_to_session(args.session)
    elif args.task:
        go_to_session_in_task(args.task)


if __name__ == '__main__':
    main()
