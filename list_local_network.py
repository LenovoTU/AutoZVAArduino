import subprocess
import re
def get_devices_on_network():
    output = subprocess.check_output(['arp', '-a']).decode('utf-8')
    devices = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', output)
    ip_list = [ip for ip in devices if ip.startswith('192')]
    return ip_list
if __name__ == '__main__':
    ip_list = get_devices_on_network()
    print(ip_list)