import socket

def scan_network():
    active_hosts = []
    subnet = '192.168.1'
    timeout = 0.1
    
    for i in range(1, 255):
        host = subnet + '.' + str(i)
        try:
            socket.setdefaulttimeout(timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, 80))
            active_hosts.append(host)
            s.close()
        except:
            pass
    
    return active_hosts


print(scan_network())
