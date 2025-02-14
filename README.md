# Helium ChirpStack Key Manager

This service facilitates the automatic synchronization of session keys between ChirpStack and Helium routes. It extracts device session keys from a local ChirpStack instance and updates the corresponding Helium route with the session key information.

## Prerequisites

- Python 3.7+
- Local ChirpStack instance
- Helium CLI Config Service
- Access to ChirpStack gRPC API
- Valid Helium Route ID

## Installation

1. Clone this repository:
```bash
git clone https://github.com/jtbuffmire/helium-chirpstack-key-manager.git
cd helium-chirpstack-key-manager
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Copy the environment template and configure your settings:
```bash
cp .env.template .env
```
4. Edit the `.env` file with your specific configuration.

## Configuration

The following environment variables need to be set in your `.env` file:

- `CHIRPSTACK_API_TOKEN`: <Your ChirpStack API token> (Obtained from ChirpStack GUI)
- `HELIUM_ROUTE_ID`: <Your Helium route ID> (Obtained from Helium CLI Config Service)
- `CHIRPSTACK_API_HOST`: <ChirpStack API host> (default: localhost)
- `CHIRPSTACK_API_PORT`: <ChirpStack API port> (default: 8080)

## Usage

### Manual Execution & Update

1. Extract keys from ChirpStack:
```bash
python3 src/extract_keys.py
```
2. Generate and execute SKF updates:
```bash
python3 src/generate_skfs.py
```
3. Update Helium Route SKFs:
```bash
./scripts/update_service.sh
```

### Automated Services can be more tricky depending on your user privileges and system configuration, but here are the steps to create a systemd service:
#### Update Service:

1. Use nano or your preferred text editor to create a systemd service file. 
The default path for this in ubuntu is `/etc/systemd/system/`.
You can create this file in this location with:
```bash
sudo nano /etc/systemd/system/helium-skf-update.service
```

2. Enter the contents of the service file and configure them to your local environment. 
You can find a template in this repo at `./helium-skf-update.service`.

3. Enable and start the service. If you are logged in as ubuntu:
```bash
sudo systemctl daemon-reload
sudo systemctl enable helium-skf-update.service
sudo systemctl start helium-skf-update.service
```

#### Update Timer:

1. Use nano or your preferred text editor to create a systemd timer file. 
The default path for this in ubuntu is `/etc/systemd/system/`.
You can create this file in this location with:
```bash
sudo nano /etc/systemd/system/helium-skf-update.timer
```

2. Enter the contents of the timer file and configure them to your local environment. 
You can find a template in this repo at `./helium-skf-update.timer`.

3. Enable and start the timer:
```bash
sudo systemctl daemon-reload
sudo systemctl enable helium-skf-update.timer
sudo systemctl start helium-skf-update.timer
```

## Logs

Logs are stored in the `logs` directory. You can monitor the service using:
```bash
tail -f logs/helium-skf-update.log
```


## Security Considerations

- Keep your `.env` file secure and never commit it to version control
- Regularly rotate your ChirpStack API token
- Monitor the logs for any unauthorized access attempts
- Ensure proper file permissions on the session keys directory

Additional Files
# Environment variables
.env

# Generated files
sessionkeys/
logs/
scripts/

# Python
__pycache__/
*.py[cod]
*$py.class
grpcio==1.54.0
protobuf==4.22.3
python-dotenv==1.0.0
google-api-python-client==2.86.0
chirpstack-api==4.5.0

# directory structure
helium-chirpstack-key-manager/
├── .env.template
├── .env
├── .gitignore
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── extract_keys.py
│   ├── generate_skfs.py
│   └── utils/
│       ├── __init__.py
│       └── config.py
├── scripts/
│   └── update_service.sh
├── sessionkeys/
├── skf-updates/
├── logs/
└── systemd/
    └── helium-skf-update.service