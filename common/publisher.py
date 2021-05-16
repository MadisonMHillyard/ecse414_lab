import threading
import socket
import random
import time
import json
from common import net_util
import logging
from common import log_util
from common.blockchain import Blockchain
import numpy
import copy

# logger setup
logger = log_util.get_logger("publisher_log.txt")
logger.setLevel(logging.INFO)


class Listener(threading.Thread):
    def __init__(self, publisher):
        # initialization of subscriber thread
        threading.Thread.__init__(self)

        # set up to be a tcp listener
        self.host = net_util.get_host_ip_address()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, 0))
        self.port = self.socket.getsockname()[1]

        # parent thread
        self.parent = publisher

        # publisher won't have a chain until someone broadcasts (needs critical section)
        self.blockchain = Blockchain()

        # events
        self.received_initial_peerlist = threading.Event()
        self.received_blockchain = threading.Event()

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

    def handle_message(self, data):
        #logger.debug(data)
        try:
            json_msg = json.loads(data.decode())
        except Exception as e:
            logger.error(self.name + " JSON decode error: " + str(e) + " dump: " + str(data.decode()))
            return

        if json_msg["origin"] == "aicn_registry":
            if json_msg["type"] == "peer_list":
                new_peers = json_msg['data']
                for new_peer in new_peers:
                    if new_peer not in self.parent.peers:
                        self.parent.peers.append(new_peer)

                for peer in self.parent.peers:
                    if peer not in new_peers:
                        self.parent.peers.remove(peer)
                #self.parent.peers = json_msg["data"]
                if not self.received_initial_peerlist.is_set() and len(self.parent.peers) > 0:
                    self.received_initial_peerlist.set()
                logger.debug(self.parent.name + " received size " + str(len(self.parent.peers)) +
                             " peer_list: " + str(self.parent.peers))

        elif json_msg["origin"] == "node":
            if json_msg["type"] == "broadcast":
                if json_msg['sub_type'] == "blockchain":
                    # got a blockchain from someone ... resolve
                    logger.debug(self.parent.name + " started to resolve blockchain from " + json_msg['name'])
                    if self.blockchain.resolve_conflicts(json_msg['data']):
                        self.parent.blockchain_lock.acquire()
                        self.parent.weights = numpy.asarray(self.blockchain.last_block['transactions'][-1]['weights'])
                        self.parent.bias = self.blockchain.last_block['transactions'][-1]['bias']
                        self.parent.blockchain_lock.release()
                        self.received_blockchain.set()
                        logger.info(self.parent.name + " resolve accepted incoming blockchain with length " +
                                    str(len(self.blockchain.chain)) + " from " + json_msg['name'] +
                                    " with most recent bias " + str(self.parent.bias) +
                                    " and weights " + str(self.parent.weights))
                    else:
                        logger.info(self.parent.name + " resolve discarded incoming blockchain from " + json_msg['name'])

                else:
                    logger.error("Sub-type: Unknown")
            else:
                logger.error("Type: Unknown")
        else:
            logger.error("Origin: Unknown")


class Publisher(threading.Thread):
    def __init__(self, index, aicn_registry_ip, aicn_registry_port):
        # initialization of publisher thread
        threading.Thread.__init__(self)

        # used to ensure critical section around filesystem read/write
        #self.filesystem_lock = filesystem_lock

        # used to ensure critical section around blockchain read/write
        self.blockchain_lock = threading.Lock()

        # store index by order created
        self.index = index
        self.origin = "publisher"
        self.name = self.origin + " " + str(random.randint(1, 1e6))
        self.aicn_registry_ip = aicn_registry_ip
        self.aicn_registry_port = aicn_registry_port

        # peer list (publishers/nodes)
        self.peers = []

        # used to prove out platform (needs critical section)
        self.dummy_gradient = 100000

        # initialize gradient variables to 0
        self.weights = numpy.zeros((1, 256*256))
        self.bias = 0
        self.alpha = 0.00001

        self.images = list()
        self.original_images = list()

        # create a listener so can hear the latest blockchain
        self.listener = Listener(self)
        self.listener.start()

    # main execution of a publisher
    # waits some time, then performs gradient descent
    # and sends to computation node(s)
    def run(self):
        # subscribe to known computation nodes
        if self.learn_peer_info() == 0:
            # wait until we receive a response from server before proceeding
            self.listener.received_initial_peerlist.wait()
            self.original_images = copy.deepcopy(self.images)
            time.sleep(2)
            logger.info(self.name + " sleeping for 15 seconds before starting, allow other publishers to join AICN")
            time.sleep(15)

            while True:
                #max_delay = 3
                #sleep_time = random.randint(3, max_delay)
                #logger.info(self.name + " sleeping for " + str(sleep_time) + " seconds " +
                #            "before performing gradient and sending to computation node(s)")
                #time.sleep(sleep_time)

                if len(self.images) > 1:
                    image = self.images.pop(random.randint(0, len(self.images)-1))
                    # perform gradient descent (critical section)
                    self.blockchain_lock.acquire()

                    # df/dw
                    par_deriv_weights = self.partial_derivative_weights(image)
                    # df/db
                    par_deriv_bias = self.partial_derivative_bias(image)


                    self.weights = numpy.subtract(self.weights, numpy.multiply(self.alpha, par_deriv_weights))
                    self.bias = self.bias - self.alpha * numpy.asscalar(par_deriv_bias)

                    self.blockchain_lock.release()

                    # for each node known, open a socket and send new gradient!
                    for peer in self.peers:
                        if peer['origin'] == 'node':
                            try:
                                info = dict()
                                info['weights'] = self.weights.tolist()
                                info['bias'] = self.bias
                                net_util.socket_send(peer['ip'], peer['port'], self.origin, self.name,
                                                     type='broadcast', sub_type='local_gradient',
                                                     data=info,
                                                     timeout=10)
                            except (ConnectionRefusedError, TimeoutError, socket.timeout) as e:
                                logger.error(self.name + " removing peer due to " + str(e) + ": " + str(peer))
                                self.peers.remove(peer)

                    # wait for a new blockchain before proceeding
                    logger.info(self.name + " sent its gradient and is waiting for a blockchain response")
                    self.listener.received_blockchain.wait()
                    self.listener.received_blockchain.clear()
                    logger.info(self.name + " recieved a blockchain and has " + str(len(self.images)-1) + " image gradients left to send")

                # we have one last image, how did our model do?
                elif len(self.images) == 1:
                    time.sleep(3)
                    image = self.images.pop()
                    x = image[1]
                    y = numpy.dot(self.weights, x) + self.bias
                    y_expected = image[0]
                    logger.info("************************")
                    logger.info(self.name + " has last image " + image[2] + " with known y = " + str(y_expected))
                    logger.info(self.name + " model predicts y = " + str(y))
                    logger.info("************************")
                    if (y_expected < 0 and y <= -0.7) or (y_expected > 0 and y >= 0.7):
                        logger.info(self.name + " model was SUCCESSFUL at classifying its last image correctly!")
                        # send message to everyone that we're exiting and remove us from their peerlist
                        info = dict()
                        info['state'] = "inactive"
                        for peer in self.peers:
                            if peer['origin'] == 'node':
                                try:
                                    net_util.socket_send(peer['ip'], peer['port'], self.origin, self.name,
                                                         type='state', sub_type=None, data=info, timeout=10)
                                except (ConnectionRefusedError, TimeoutError, socket.timeout, socket.gaierror) as e:
                                    logger.error(self.name + " could not send unsubscribe: " + str(e))

                        logger.info(self.name + " DONE PUBLISHING but listening for blockchain updates")
                        exit()
                    else:
                        self.images = copy.deepcopy(self.original_images)
                        logger.info(self.name + " model FAILED at classifying its last image correctly, iterating again!")





        # self.listener.kill()

    # send the aicn registry our info and wait to receive info from them
    def learn_peer_info(self):
        info = dict()
        info['ip'] = self.listener.host
        info['port'] = self.listener.port
        info['name'] = self.name
        try:
            net_util.socket_send(self.aicn_registry_ip, self.aicn_registry_port, self.origin, self.name,
                                  type='subscribe', sub_type=None, data=info)
        except (ConnectionRefusedError, TimeoutError, socket.timeout, socket.gaierror) as e:
            logger.error(self.name + " could not connect to AICN registry: " + str(e))
            return 1

        return 0

    def add_image(self, y, pixel_array, img_name):
        self.images.append([y, pixel_array, img_name])

    def partial_derivative_weights(self, image):
        y = image[0]
        x = image[1]
        mean = x.mean()
        test_t = numpy.dot(self.weights, x)
        test = -2 * (y - numpy.dot(self.weights, x) - self.bias)
        test2 = numpy.multiply(numpy.asscalar(-2 * (y - numpy.dot(self.weights, x) - self.bias)), x)
        test3  = numpy.add(test2, self.weights)
        return numpy.add(numpy.multiply(numpy.asscalar(-2 * (y - numpy.dot(self.weights, x) - self.bias)), x), self.weights)
        #return numpy.multiply(numpy.asscalar(2 * (y - numpy.dot(self.weights, x) - self.bias)), -x)

    def partial_derivative_bias(self, image):
        y = image[0]
        x = image[1]
        test1 = numpy.dot(self.weights, x)
        test2 = (-2 * (y - numpy.dot(self.weights, x) - self.bias))
        return (-2 * (y - numpy.dot(self.weights, x) - self.bias)) + (2 * self.bias)

