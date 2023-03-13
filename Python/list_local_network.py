import subprocess
import re
import ipaddress
def get_devices_on_network():
    """
    Scans the local network and returns a list of IP addresses of devices that are currently connected.

    Returns:
        list: A list of IP addresses (as strings) of devices on the network.
    """
    try:
        output = subprocess.run(['arp', '-a'], capture_output=True, text=True, check=True).stdout
    except FileNotFoundError:
        print("arp command not found")
        return []
    # Extract IP addresses from the output using a regular expression.
    # Filter out non-private IP addresses and those that don't start with '192'.
    return [ip for ip in re.findall(r'\d+\.\d+\.\d+\.\d+', output) if ipaddress.ip_address(ip).is_private and ip.startswith('192')]
if __name__ == '__main__':
    print(get_devices_on_network())
