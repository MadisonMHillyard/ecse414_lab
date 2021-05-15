from AICN_Registry import AICN_Registry

# clean up and kill set up
import signal
import sys

global registry
# class Sys_Exit(Exception):
#     pass
# def sig_handler(_signo, _stack_frame):
#     print('sigterm func')
#     raise Sys_Exit

def main():
    # register signal handler
    # signal.signal(signal.SIGTERM, sig_handler)
    # signal.signal(signal.SIGINT, sig_handler)

    # try:

    # instantiate registry
    registry = AICN_Registry()

    # start registry thread
    registry.start()

    # except Sys_Exit:
    #     registry.sys_exit.set()

        # wait for registry thread to end (never)
    registry.join()


if __name__ == '__main__':
    main()

# class AICN_Registry(threading.Thread):
#     def __init__(self):
#         # initialization of subscriber thread
#         threading.Thread.__init__(self)
        
#         # handle kill signals
#         signal.signal(signal.SIGTERM, self.sigterm_handler)
#         signal.signal(signal.SIGINT, self.sigterm_handler)

#         # set up to be a tcp listener
#         self.host = net_util.get_host_ip_address()
#         self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.socket.bind((self.host, 8001))
#         self.port = self.socket.getsockname()[1]
#         self.origin = 'aicn_registry'
#         self.killed = flase
#         self.peerlist = []

#     def export_registry_net_info(self):
#         json_object = dict()
#         json_object['aicn_registry'] = []
#         with open(aicn_registry_filename, "w") as file:
#             json_object['aicn_registry'].append({
#                 'ip': self.host,
#                 'port': self.port
#             })
#             json.dump(json_object, file, indent=4)

#     # main execution of registry
#     # opens a socket and listens forever
#     def run(self):
#         # write net info to file
#         sys.settrace(self.globaltrace)
#         self.export_registry_net_info()

#         # listen for nodes forever
#         self.socket.listen(10)
#         logger.info("AICN Registry Started Listening @ " +
#                      self.host + " Port " + str(self.port))
#         while True:
#             conn, address = self.socket.accept()
#             with conn:
#                 data = b''
#                 while True:
#                     data = data + conn.recv(int(1e7))
#                     if not data:
#                         break
#                     if data[-8:].decode() == "D3ADB33F":
#                         test = data[:-1].decode()
#                         self.handle_message(data[:-8])
#                         data = b''

#     def handle_message(self, data):
#         json_msg = json.loads(data.decode())

#         if json_msg["type"] == 'subscribe':
#             # add this peer's info to the  list
#             new_peer = {'origin': json_msg['origin'],
#                         'ip': json_msg['data']['ip'],
#                         'port': json_msg['data']['port'],
#                         'name': json_msg['data']['name'],
#                         'local_count': 0,
#                         'state' : 'active'}
#             self.peerlist.append(new_peer)
#             logger.info("adding peer: " + str(new_peer))

#             # purge any dead peers before sharing them with publishers and nodes
#             for peer_i in self.peerlist:
#                 try:
#                     net_util.socket_connect(peer_i['ip'], peer_i['port'], timeout=.3)
#                 except (ConnectionRefusedError, TimeoutError, socket.timeout) as e:
#                     logger.error("removing peer due to " + str(e) + ": " + str(peer_i))
#                     self.peerlist.remove(peer_i)

#             # update all peers with all other peer's information
#             for peer_i in self.peerlist:
#                 try:
#                     net_util.socket_send(peer_i['ip'], peer_i['port'], self.origin, self.name,
#                                           type='peer_list', sub_type=None,
#                                           data=[peer for peer in self.peerlist if peer['name'] is not peer_i['name']],
#                                           timeout=1)
#                 except (ConnectionRefusedError, TimeoutError, socket.timeout) as e:
#                     logger.error("removing peer due to " + str(e) + ": " + str(peer_i))
#                     self.peerlist.remove(peer_i)

#         else:
#             logger.error("Type: Unknown")
#     def kill(self):
#         self.killed = True

#     # def globaltrace(self, frame, event, arg):
#     #     if event == 'call':
#     #         return self.localtrace
#     #     else:
#     #         return None
    
#     # def localtrace(self, frame, event, arg):
#     #     if self.killed:

#     # def sigterm_handler(self, _signo, _stack_frame):
#     #     self.kill(self)
#     #     sys.exit(0)



