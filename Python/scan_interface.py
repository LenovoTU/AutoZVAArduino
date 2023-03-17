import subprocess
import re
import ipaddress
import sys
import glob
import serial

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

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


if __name__ == '__main__':
    print(get_devices_on_network())
    print(serial_ports())