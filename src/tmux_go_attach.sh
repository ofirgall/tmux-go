#!/usr/bin/env sh

if ! [ -z "$OPEN_TMUX_SESSION" ]; then # tmux-go
	echo "Opening $OPEN_TMUX_SESSION at desk $OPEN_AT_DESK"
	TMUX_SESSION_TITLE="tmux-go-session:$OPEN_TMUX_SESSION"
	wmctrl -r "$TMUX_SESSION_TITLE" -t $OPEN_AT_DESK; sleep 0.1; wmctrl -a "$TMUX_SESSION_TITLE"
    tmux attach -t "$OPEN_TMUX_SESSION"
fi
