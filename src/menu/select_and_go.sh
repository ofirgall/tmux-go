#!/usr/bin/env bash

BG="#2f302a"
FG="#f8f8f0"
ACTIVE_FG="#e878d2"
ACTIVE_BG="#1d2026"
MATCH_FG="#f92672"
session=$(tmux ls -F '#S' | fzf --reverse --color="bg:$BG,fg:$FG,bg+:$ACTIVE_BG,fg+:$ACTIVE_FG,hl:$MATCH_FG")

# ctrl-c
if [ -z $session ]; then
	exit
fi

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
$CURRENT_DIR/../tmux_go.py --session $session &
# TODO: more resilient
sleep 1 # keep terminal alive for a sec to let tmux_go complete
