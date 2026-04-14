#!/usr/bin/env bash

# Prompts the user to enter a value for the PIF_SECRET_KEY environment variable.
# Creates the directory ~/.config/aimoa/ if it doesn’t already exist.
# Saves the variable as an exported environment variable inside env.sh.
# Ensures .bashrc sources this env.sh file (adds the line only if missing).
# Confirms the variable was set and reminds the user to reload .bashrc.

ENV_FILE="$HOME/.config/aimoa/env_pif_key.sh"
BASHRC="$HOME/.bashrc"
LINE='[ -f ~/.config/aimoa/env_pif_key.sh ] && source ~/.config/aimoa/env_pif_key.sh'

VAR="PIF_SECRET_KEY"

# Prompt for value
read -rp "Enter value for $VAR: " VALUE

# Ensure directory exists
mkdir -p "$(dirname "$ENV_FILE")"

echo "export $VAR=\"$VALUE\"" > "$ENV_FILE"

# Add source line to .bashrc if missing
grep -Fqx "$LINE" "$BASHRC" || echo "$LINE" >> "$BASHRC"

echo "$VAR set successfully."

echo "Use 'source $BASHRC' to reload .bashrc file."