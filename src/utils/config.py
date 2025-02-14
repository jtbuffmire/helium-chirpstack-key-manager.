from dotenv import load_dotenv
import os

class Config:
    def __init__(self):
        load_dotenv()
        
        # ChirpStack settings
        self.cs_host = os.getenv('CHIRPSTACK_API_HOST', 'localhost')
        self.cs_port = os.getenv('CHIRPSTACK_API_PORT', '8080')
        self.cs_token = os.getenv('CHIRPSTACK_API_TOKEN')
        
        # Helium settings
        self.helium_route_id = os.getenv('HELIUM_ROUTE_ID')
        
        # Directory settings
        self.session_keys_dir = os.getenv('SESSION_KEYS_DIR', './sessionkeys')
        self.logs_dir = os.getenv('LOGS_DIR', './logs')
        self.skf_updates_dir = os.getenv('SKF_UPDATES_DIR', './skf-updates')  # Changed from scripts_dir
        
        # Retention settings
        self.retention_days = int(os.getenv('FILE_RETENTION_DAYS', '7'))
        
        self.validate()
        self.create_directories()
    
    def validate(self):
        if not self.cs_token:
            raise ValueError("CHIRPSTACK_API_TOKEN must be set")
        if not self.helium_route_id:
            raise ValueError("HELIUM_ROUTE_ID must be set")
    
    def create_directories(self):
        for directory in [self.session_keys_dir, self.logs_dir, self.scripts_dir]:
            os.makedirs(directory, exist_ok=True) 