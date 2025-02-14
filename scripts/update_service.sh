#!/bin/bash

# Set up basic logging
exec 1> >(logger -s -t $(basename $0)) 2>&1

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Move up one directory to the project root
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Set working directory to project root
cd "$PROJECT_ROOT"

# Clean up old files (older than 7 days)
find ./sessionkeys -name "chirpstack_session_keys_*.json" -mtime +7 -delete
find ./skf-updates -name "update_skfs_*.sh" -mtime +7 -delete

# Extract new keys
python3 src/extract_keys.py

# Get the most recent session keys file
latest_keys=$(ls -t ./sessionkeys/chirpstack_session_keys_*.json | head -n 1)
if [ -z "$latest_keys" ]; then
    echo "ERROR: No session keys file found!"
    exit 1
fi

# Generate and execute SKF update script
python3 src/generate_skfs.py "$latest_keys"

# Get the most recent update script
latest_script=$(ls -t ./skf-updates/update_skfs_*.sh | head -n 1)
if [ -z "$latest_script" ]; then
    echo "ERROR: No update script generated!"
    exit 1
fi

# Execute the update script
bash "$latest_script"

# Create logs directory if it doesn't exist
mkdir -p ./logs

# Log the execution
echo "$(date): Updated SKFs using $latest_keys" >> ./logs/helium-skf-update.log

# Add summary to syslog
total_skfs=$(grep -c "added Skf" ./logs/helium-skf-update.log)
echo "Update completed: Added $total_skfs SKFs"