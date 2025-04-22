import yaml
import os
import sys
import re
import stat

def validate_ip(ip_input):
    """
    Validate the IP address input and append /24 if not provided.
    Returns the IP in the format 'x.x.x.x/24' or raises an error.
    """
    # Regular expression for IP (with optional /24)
    ip_pattern = r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(/24)?$"
    match = re.match(ip_pattern, ip_input)
    
    if not match:
        raise ValueError("Invalid IP address format. Use 'x.x.x.x' or 'x.x.x.x/24' (e.g., 192.168.1.55)")
    
    ip = match.group(1)
    # Split IP into octets and validate each is 0-255
    octets = ip.split('.')
    if len(octets) != 4 or not all(0 <= int(octet) <= 255 for octet in octets):
        raise ValueError("Each octet in the IP address must be between 0 and 255.")
    
    # Return IP with /24
    return f"{ip}/24"

def update_netplan_config(file_path, ip_address):
    try:
        # Validate and format the IP address
        formatted_ip = validate_ip(ip_address)
        
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
            'addresses': [formatted_ip],
            'nameservers': {'addresses': ['8.8.8.8', '8.8.4.4']},
            'optional': True
        })

        # Write the updated configuration back to the file
        with open(file_path, 'w') as file:
            yaml.safe_dump(config, file, default_flow_style=False, sort_keys=False)
        
        # Set file permissions to 600 (root read/write only)
        os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)
        
        print(f"Successfully updated {file_path} with IP {formatted_ip}")
        print(f"File permissions set to 600")

    except PermissionError:
        print(f"Error: Permission denied. Run this script with sudo to modify {file_path}.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error: Failed to parse or write YAML file: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    netplan_file = "/etc/netplan/50-cloud-init.yaml"
    try:
        # Prompt user for IP address
        ip_input = input("Enter the IP address for eth0 (e.g., 192.168.1.55 or 192.168.1.55/24): ").strip()
        update_netplan_config(netplan_file, ip_input)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)