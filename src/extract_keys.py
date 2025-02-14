#!/usr/bin/env python3

import grpc
from chirpstack_api import api
from google.protobuf.json_format import MessageToDict
import json
from datetime import datetime
import logging
import os
from utils.config import Config

# Initialize config
config = Config()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(config.logs_dir, 'migration_key_extraction.log')),
        logging.StreamHandler()
    ]
)

def main():
    logging.info("Starting ChirpStack migration key extraction")

    # Connect to the gRPC port using configuration
    channel = grpc.insecure_channel(f'{config.cs_host}:{config.cs_port}')
    device_service = api.DeviceServiceStub(channel)
    app_service = api.ApplicationServiceStub(channel)
    device_profile_service = api.DeviceProfileServiceStub(channel)
    
    # Use API token from config
    metadata = [
        ('authorization', f'Bearer {config.cs_token}')
    ]
    
    try:
        # List all applications
        app_list_request = api.ListApplicationsRequest()
        app_list_request.limit = 999
        app_response = app_service.List(app_list_request, metadata=metadata)
        
        session_keys = []
        for app in app_response.result:
            app_id = app.id
            app_name = app.name
            
            logging.info(f"Processing application: {app_name} ({app_id})")
            
            # List devices for this application
            request = api.ListDevicesRequest()
            request.application_id = app_id
            request.limit = 999

            response = device_service.List(request, metadata=metadata)
            
            for device in response.result:
                logging.info(f"Getting activation for device: {device.name} ({device.dev_eui})")
                
                # Get device profile name
                dp_resp = device_profile_service.Get(
                    api.GetDeviceProfileRequest(id=device.device_profile_id), 
                    metadata=metadata
                )
                dp_name = dp_resp.device_profile.name
                
                activation_request = api.GetDeviceActivationRequest(dev_eui=device.dev_eui)
                try:
                    activation = device_service.GetActivation(activation_request, metadata=metadata)
                    if activation.device_activation:
                        session_keys.append({
                            'deviceName': device.name,
                            'devEUI': device.dev_eui,
                            'devAddr': activation.device_activation.dev_addr,  
                            'applicationID': app_id,
                            'applicationName': app_name,
                            'deviceProfileName': dp_name,
                            'fNwkSIntKey': activation.device_activation.f_nwk_s_int_key,
                            'sNwkSIntKey': activation.device_activation.s_nwk_s_int_key,
                            'nwkSEncKey': activation.device_activation.nwk_s_enc_key,
                            'appSKey': activation.device_activation.app_s_key
                        })
                        logging.info(f"Successfully extracted keys for device: {device.name}")
                    else:
                        logging.warning(f"No active session found for device: {device.name}")
                except Exception as e:
                    logging.error(f"Failed to get activation for device {device.name}: {str(e)}")
        
        # Save to configured session keys directory
        if session_keys:
            os.makedirs(config.session_keys_dir, exist_ok=True)
            
            # Generate timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(config.session_keys_dir, f'chirpstack_session_keys_{timestamp}.json')
            
            with open(filename, 'w') as f:
                json.dump(session_keys, f, indent=2)
            logging.info(f"Successfully exported {len(session_keys)} device keys to {filename}")

            print("\n=== Next Steps ===")
            print("Run the following command to generate Helium SKF commands:")
            print(f"    python3 generate_skfs.py {filename}")
        else:
            logging.warning("No session keys found")
            
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()