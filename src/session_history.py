#!/usr/bin/env python3

import json
from os import path
from typing import Iterator, List, Optional
from dataclasses import dataclass, field
from contextlib import contextmanager
from dataclasses_json import dataclass_json

HISTORY_FILE = path.expandvars(path.join('$HOME', '.tmux_go_history'))
HISTORY_SIZE = 100

def add(session: str):
    with _hist_ctx() as hist:
        if hist.index > 0: # dump old history
            hist.sessions = hist.sessions[hist.index:]
            hist.index = 0

        hist.sessions.insert(0, session) # First is Last
        hist.is_in_last = False

def last() -> Optional[str]:
    with _hist_ctx() as hist:
        if len(hist.sessions) < 2:
            return None

        if hist.is_in_last:
            hist.is_in_last = False
            return hist.sessions[hist.index]

        hist.is_in_last = True
        return hist.sessions[hist.index + 1]

def prev() -> Optional[str]:
    with _hist_ctx() as hist:

        if hist.index + 1 >= len(hist.sessions):
            return None # Index is already last, dont move

        hist.index += 1
        hist.is_in_last = False
        return hist.sessions[hist.index]

def next() -> Optional[str]:
    with _hist_ctx() as hist:
        if hist.index == 0:
            return None # Index is already first, dont move

        hist.index -= 1
        hist.is_in_last = False
        return hist.sessions[hist.index]

@dataclass_json
@dataclass
class History:
    sessions: List[str] = field(default_factory=lambda: [])
    index: int = 0 # 0 = last
    is_in_last: bool = False

@contextmanager
def _hist_ctx() -> Iterator[History]:
    hist = _read_history()
    try:
        yield hist
    finally:
        _write_history(hist)

def _read_history() -> History:
    try:
        with open(HISTORY_FILE, 'r') as f:
            return History.schema().loads(f.read())
    except (KeyError, FileNotFoundError):
        return History()

def _write_history(history: History):
    with open(HISTORY_FILE, 'w') as f:
        f.write(history.to_json())

if __name__ == '__main__':
    import IPython
    IPython.embed()
