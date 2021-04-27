import socket

def Main():
    server_host = '10.3.0.91'
    port = 4005
    host = '10.3.1.224'
    server = (server_host, 4000)
    # server = ('172.20.112.184', 4000)
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host,port))
    
    message = input("-> ")
    while message !='q':
        s.sendto(message.encode('utf-8'), server)
        data, addr = s.recvfrom(1024)
        data = data.decode('utf-8')
        print("Received from server: " + data)
        message = input("-> ")
    s.close()

if __name__=='__main__':
    Main()