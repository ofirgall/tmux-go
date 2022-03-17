#!/usr/bin/env bash

BACKGROUND="#2b1c07"
session=$(tmux ls -F '#S' | fzf --reverse --header="Select Tmux Session. Ctrl-C to exit." --color="bg:$BACKGROUND")

# ctrl-c
if [ -z $session ]; then
	exit
fi

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
$CURRENT_DIR/../tmux_go.py --session $session &
# TODO: more resilient
sleep 1 # keep terminal alive for a sec to let tmux_go complete
