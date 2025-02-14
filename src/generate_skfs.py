#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime
from utils.config import Config

def generate_skfs(input_file):
    # Initialize config
    config = Config()
    
    # Read session keys
    with open(input_file, 'r') as f:
        devices = json.load(f)
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    script_file = os.path.join(config.scripts_dir, f'update_skfs_{timestamp}.sh')
    
    with open(script_file, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# Commands to add session keys for each device\n\n")
        
        for device in devices:
            f.write(f"# {device['deviceName']} ({device['devEUI']})\n")
            f.write(f"helium-config-service-cli route skfs add \\\n")
            f.write(f"  --route-id {config.helium_route_id} \\\n")
            f.write(f"  --devaddr {device['devAddr']} \\\n")
            f.write(f"  --session-key {device['nwkSEncKey']} \\\n")
            f.write(f"  --max-copies 99 \\\n")
            f.write(f"  --commit\n\n")
    
    os.chmod(script_file, 0o755)  # Make executable
    
    print(f"\n=== Next Steps ===")
    print(f"Run the generated script to update Helium route SKFs:")
    print(f"    {script_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 generate_skfs.py <session_keys_file>")
        sys.exit(1)
    
    generate_skfs(sys.argv[1]) 