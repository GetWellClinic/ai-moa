#!/usr/bin/env bash

# Prompts the user to enter a value for the PIF_SECRET_KEY environment variable.
# Creates the directory ~/.config/aimoa/ if it doesn’t already exist.
# Writes the variable into a systemd-compatible EnvironmentFile (KEY=VALUE format).
# Always overwrites the existing env file to ensure the latest value is used.
# Sets secure file permissions (600) so only the owner can read it.
# Prints the file path and reminds the user how to reference it in a systemd service.

ENV_FILE="$HOME/.config/aimoa/aimoa_service_pif_env_keys"
VAR="PIF_SECRET_KEY"

read -rsp "Enter value for $VAR: " VALUE

mkdir -p "$(dirname "$ENV_FILE")"

# ALWAYS overwrite file
echo "$VAR=$VALUE" > "$ENV_FILE"

chmod 600 "$ENV_FILE"

echo "Saved to $ENV_FILE"
echo "Use in systemd: EnvironmentFile=$ENV_FILE"