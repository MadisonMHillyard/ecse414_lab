import socket

def Main():
   
    host = '10.3.1.224'
    # host = '172.20.112.184' #Server ip
    port = 4000

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))

    print("Server Started")
    while True:
        data, addr = s.recvfrom(1024)
        data = data.decode('utf-8')
        print("Message from: " + str(addr))
        print("received user local information: " + data)
        # data = data.upper()
        alpha = 0.001
        data = alpha * int(data)
        data = str(data)
        print("Sending: " + data)
        s.sendto(data.encode('utf-8'), addr)
    c.close()

if __name__=='__main__':
    Main()