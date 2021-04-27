import json
import socket
import struct
import time


def socket_send(ip, port, origin, name, type, sub_type, data, timeout=None):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        s.connect((ip, port))
        packet = dict()
        packet["origin"] = origin
        packet["name"] = name
        packet["type"] = type
        packet["sub_type"] = sub_type
        packet["data"] = data
        json_packet = json.dumps(packet) + "D3ADB33F"
        send_again = 1
        while send_again == 1:
            try:
                s.sendall(json_packet.encode())
                send_again = 0
            except Exception as e:
                print("Send error " + str(e) + " recevied")
                print(json_packet)
                time.sleep(.5)
        s.close()


def socket_connect(ip, port, timeout=None):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        s.connect((ip, port))
        s.close()


# platform independent way to get active host ip
# open a socket to google's DNS, then get host's ip
# don't actually have to send anything
def get_host_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    return s.getsockname()[0]
