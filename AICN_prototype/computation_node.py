import threading
import socket
import json
import time
import net_util
import logging
import log_util
import sys
import random
from blockchain import Blockchain
import numpy


# logger setup
logger = log_util.get_logger("node_log.txt")
logger.setLevel(logging.DEBUG)


class Listener(threading.Thread):
    def __init__(self, node):
        # initialization of subscriber thread
        threading.Thread.__init__(self)

        # set up to be a tcp listener
        self.host = net_util.get_host_ip_address()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, 0))
        self.port = self.socket.getsockname()[1]

        # parent thread
        self.parent = node

        # events
        self.received_initial_peerlist = threading.Event()

    # main execution of a listener
    # opens a socket and listens forever
    def run(self):
        # listen for nodes forever
        self.socket.listen(10)
        logger.debug(self.parent.name + " Started Listening @ " +
                     self.host + " Port " + str(self.port))
        while True:
            conn, address = self.socket.accept()
            with conn:
                data = b''
                while True:
                    data = data + conn.recv(int(1e7))
                    if not data:
                        break
                    if data[-8:].decode() == "D3ADB33F":
                        self.handle_message(data[:-8])
                        data = b''

    # got a message
    # determine origin then perform appropriate action
    def handle_message(self, data):
        try:
            json_msg = json.loads(data.decode())
        except Exception as e:
            logger.error(self.name + " JSON decode error: " + str(e) + " dump: " + str(data.decode()))
            return

        if json_msg["origin"] == "aicn_registry":
            if json_msg["type"] == "peer_list":
                self.parent.peers = json_msg["data"]
                if not self.received_initial_peerlist.is_set():
                    self.received_initial_peerlist.set()
                logger.debug(self.parent.name + " received size " + str(len(self.parent.peers)) +
                             " peer_list: " + str(self.parent.peers))

        elif json_msg["origin"] == "publisher":
            if json_msg["type"] == "broadcast":
                if json_msg['sub_type'] == "local_gradient":
                    logger.info(self.parent.name + " received gradient from " + json_msg['name'])
                    for peer in self.parent.peers:
                        if peer['name'] == json_msg['name']:
                            peer['local_weights'] = json_msg['data']['weights']
                            peer['local_bias'] = json_msg['data']['bias']
                            peer['local_count'] = peer['local_count'] + 1
                            break

                    if self.parent.received_all_gradients():
                        logger.info(self.parent.name + " has received all local gradients and started PoW algorithm")
                        self.parent.start_PoW_event.set()

            if json_msg['type'] == 'state':
                if json_msg['data']['state'] == 'inactive':
                    for peer in self.parent.peers:
                        if peer['name'] == json_msg['name']:
                            peer['state'] = 'inactive'
                            logger.info(self.parent.name + " received state " + peer['state'] + " from " + json_msg['name'])
                            if self.parent.received_all_gradients() and not self.parent.start_PoW_event.is_set():
                                logger.info(self.parent.name + " has received all local gradients and started PoW algorithm")
                                self.parent.start_PoW_event.set()

        elif json_msg["origin"] == "node":
            if json_msg["type"] == "broadcast":
                if json_msg['sub_type'] == "blockchain":
                    # got a blockchain from someone else... resolve
                    logger.debug(self.parent.name + " started to resolve blockchain from " + json_msg['name'])
                    if self.parent.blockchain.resolve_conflicts(json_msg['data']):
                        logger.debug(self.parent.name + " resolve accepted incoming blockchain from " +
                                     json_msg['name'])
                        self.parent.abort_PoW_event.set()
                    else:
                        logger.debug(self.parent.name + " resolve discarded incoming blockchain from " +
                                     json_msg['name'])

        else:
            logger.error("Origin: Unknown")


class ComputationNode(threading.Thread):
    def __init__(self, index, aicn_registry_ip, aicn_registry_port):
        # initialization of node thread
        threading.Thread.__init__(self)

        # store index by order created
        self.index = index
        self.origin = "node"
        self.name = self.origin + " " + str(random.randint(1, 1e6))
        self.aicn_registry_ip = aicn_registry_ip
        self.aicn_registry_port = aicn_registry_port

        # computation node won't have a chain until someone broadcasts
        # self.blockchain = 0
        self.gradient = sys.maxsize
        self.global_gradient = sys.maxsize
        self.global_weights = numpy.zeros((256*256, 1))
        self.global_bias = 0

        # peer list (publishers/nodes/nodepubs)
        self.peers = []

        # Instantiate the Blockchain
        self.blockchain = Blockchain()
        self.proof = 0

        # create a listener so can hear the latest blockchain
        self.listener = Listener(self)
        self.listener.start()

        self.start_PoW_event = threading.Event()
        self.abort_PoW_event = threading.Event()

    # main execution of a computation node
    # waits for a message from a publisher forever
    def run(self):
        # learn other devices network info (populates self.peers)
        if self.learn_peer_info() == 0:
            # wait until we receive a response from server before proceeding
            self.listener.received_initial_peerlist.wait()
            time.sleep(3)

            while True:
                # wait for a message to start PoW
                self.start_PoW_event.wait()
                self.start_PoW_event.clear()
                if self.calc_PoW():
                    if self.abort_PoW_event.is_set():
                        logger.info(self.name + " aborted PoW because new chain verified with length " +
                                    str(len(self.blockchain.chain)))
                    else:
                        logger.info(self.name + " completed PoW with value " + str(self.proof))
                        self.average_gradients()
                        self.blockchain.new_transaction(origin=self.origin,
                                                        weights=self.global_weights.tolist(),
                                                        bias=self.global_bias)

                        # Forge the new Block by adding it to the chain
                        previous_hash = self.blockchain.hash(self.blockchain.last_block)
                        self.blockchain.new_block(self.proof, previous_hash)

                        # broadcast new gradient to all peers
                        for peer in self.peers:
                            try:
                                net_util.socket_send(peer['ip'], peer['port'], self.origin, self.name,
                                                     type='broadcast', sub_type='blockchain',
                                                     data=self.blockchain.chain,
                                                     timeout=10)
                            except (ConnectionRefusedError, TimeoutError, socket.timeout) as e:
                                logger.error(self.name + " removing peer due to " + str(e) + ": " + str(peer))
                                self.peers.remove(peer)

    def average_gradients(self):
        count = 0
        average = 0
        bias = 0
        for peer in self.peers:
            if peer['origin'] == 'publisher':
                average = numpy.add(peer['local_weights'], average)
                bias = numpy.add(peer['local_bias'], bias)
                count = count + 1

        if count != 0:
            self.global_weights = numpy.divide(average, count)
            self.global_bias = numpy.divide(bias, count)

    # send the aicn registry our info and wait to receive info from them
    def learn_peer_info(self):
        info = dict()
        info['ip'] = self.listener.host
        info['port'] = self.listener.port
        info['name'] = self.name
        try:
            net_util.socket_send(self.aicn_registry_ip, self.aicn_registry_port, self.origin, self.name,
                                 type='subscribe', sub_type=None, data=info, timeout=5)
        except (ConnectionRefusedError, TimeoutError, socket.timeout, socket.gaierror) as e:
            logger.error(self.name + " could not connect to AICN registry: " + str(e))
            return 1

        return 0

    def get_num_publishers(self):
        num = 0
        for peer in self.peers:
            if peer['origin'] == 'publisher':
                num = num + 1
        return num

    def get_num_active_publishers(self):
        num = 0
        for peer in self.peers:
            if peer['origin'] == 'publisher' and peer['state'] != 'inactive':
                num = num + 1
        return num

    def get_num_nodes(self):
        num = 0
        for peer in self.peers:
            if peer['origin'] == 'node':
                num = num + 1
        return num

    def get_max_count(self):
        count = 0
        for publisher in self.peers:
            if publisher['origin'] == 'publisher' and publisher['state'] != 'inactive':
                if publisher['local_count'] > count:
                    count = publisher['local_count']

        return count

    def received_all_gradients(self):
        if self.get_num_active_publishers() == 0:
            return False

        max_count = self.get_max_count()
        for peer in self.peers:
            if peer['origin'] == 'publisher' and peer['state'] == 'active':
                if peer['local_count'] != max_count or peer['local_count'] == 0:
                    return False

        return True

    def calc_PoW(self):
        proof = self.blockchain.proof_of_work(self.blockchain.last_block)
        if proof == -1:
            return False
        else:
            self.proof = proof
            return True
