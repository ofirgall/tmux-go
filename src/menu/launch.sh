#!/usr/bin/env bash
CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# TODO: center
/usr/bin/x-terminal-emulator --option window.startup_mode=Windowed \
				--option window.decorations=full \
				--option window.title="Select Session" \
				--option window.position.x=1050 \
				--option window.position.y=400 \
				-e "$CURRENT_DIR/select_and_go.sh"
