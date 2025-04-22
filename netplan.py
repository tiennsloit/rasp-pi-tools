import yaml
import os
import sys

def update_netplan_config(file_path):
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist.")
            sys.exit(1)

        # Read the existing YAML file
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)

        # Check if the configuration is valid
        if not config or 'network' not in config:
            print("Error: Invalid or empty Netplan configuration.")
            sys.exit(1)

        # Ensure 'ethernets' and 'eth0' sections exist
        if 'ethernets' not in config['network']:
            config['network']['ethernets'] = {}
        if 'eth0' not in config['network']['ethernets']:
            config['network']['ethernets']['eth0'] = {}

        # Update eth0 configuration
        eth0_config = config['network']['ethernets']['eth0']
        eth0_config.update({
            'dhcp4': False,
            'addresses': ['192.168.1.55/24'],
            'nameservers': {'addresses': ['8.8.8.8', '8.8.4.4']},
            'optional': True
        })

        # Write the updated configuration back to the file
        with open(file_path, 'w') as file:
            yaml.safe_dump(config, file, default_flow_style=False, sort_keys=False)
        print(f"Successfully updated {file_path}")

    except PermissionError:
        print(f"Error: Permission denied. Run this script with sudo to modify {file_path}.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error: Failed to parse or write YAML file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    netplan_file = "/etc/netplan/50-cloud-init.yaml"
    update_netplan_config(netplan_file)