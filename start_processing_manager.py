import sys
import os
import logging
from common import log_util
import json
from pathlib import Path
# pip install Pillow
# or easy install : easy_install Pillow
from PIL import Image
import numpy
import random

# logger setup
logger = log_util.get_logger("logs/aicn_log.txt")
logger.setLevel(logging.DEBUG)

from common.publisher import Publisher
from processing_node import ComputationNode

# Globals
aicn_registry_filename = "logs/registry_info.txt"

# gather aicn ip and port
if len(sys.argv) == 3:
    if os.path.exists(aicn_registry_filename):
        with open(aicn_registry_filename, "r") as file:
            json_object = json.load(file)
            aicn_registry_ip = json_object['aicn_registry'][0]['ip']
            aicn_registry_port = json_object['aicn_registry'][0]['port']

    else:
        logger.error("Failed --  No " + aicn_registry_filename + " found to replace optional parameter 4 (IP address) & 5 (Port)")
        exit()
elif len(sys.argv) == 5:
    aicn_registry_ip = sys.argv[3]
    aicn_registry_port = int(sys.argv[4])


# start publisher, node, and nodepub threads
if len(sys.argv) == 5 or len(sys.argv) == 3:
    # Empty thread
    ThreadList = []

    # Gather number of publishers to create
    num_pubs = int(sys.argv[2])

    # Gather number of y = 1 images that exist
    if num_pubs > 0:
        plus1_list = list()
        neg1_list = list()

        for i in range(0, 1, 1):
            file_list = Path('faces/1').glob('**/*.bmp')
            for file in file_list:
                # because path is object not string
                img_str = str(file)
                img = Image.open(img_str)

                # ensure bitmap is 256 x 256, with grayscale pixels and get raw pixel array
                img = img.resize((256, 256))
                img = img.convert(mode='L')
                img_pixel_array = numpy.asarray(img.getdata())

                # normalize to zero-mean and unit variance
                #img_pixel_array = numpy.interp(img_pixel_array, (img_pixel_array.min(), img_pixel_array.max()), (-1, +1))
                img_pixel_array = (img_pixel_array - numpy.mean(img_pixel_array)) / numpy.std(img_pixel_array)
                plus1_list.append([random.randint(1, num_pubs), img_pixel_array, img_str])

            # Gather number of y = -1 images that exist
            file_list = Path('faces/-1').glob('**/*.bmp')
            for file in file_list:
                # because path is object not string
                img_str = str(file)
                img = Image.open(img_str)

                # ensure bitmap is 256 x 256, with grayscale pixels and get raw pixel array
                img = img.resize((256, 256))
                img = img.convert(mode='L')
                img_pixel_array = numpy.asarray(img.getdata(), order='C')

                # normalize to zero-mean and unit variance
                #img_pixel_array = numpy.interp(img_pixel_array, (img_pixel_array.min(), img_pixel_array.max()), (-1, +1))
                img_pixel_array = (img_pixel_array - numpy.mean(img_pixel_array)) / numpy.std(img_pixel_array)
                neg1_list.append([random.randint(1, num_pubs), img_pixel_array, img_str])

    # Gather number of computation nodes to create
    num_nodes = int(sys.argv[1])
    for i in range(0, num_nodes):
        node = ComputationNode(i+1, aicn_registry_ip, aicn_registry_port)
        ThreadList.append(node)

    num_pubs = int(sys.argv[2])
    for i in range(0, num_pubs):
        # Create publishers
        publisher = Publisher(i+1, aicn_registry_ip, aicn_registry_port)

        # Teach them y=1 images
        for image in plus1_list:
            if image[0] == publisher.index:
                publisher.add_image(y=1, pixel_array=image[1], img_name=image[2])

        # Teach them y=-1 images
        for image in neg1_list:
            if image[0] == publisher.index:
                publisher.add_image(y=-1, pixel_array=image[1], img_name=image[2])

        ThreadList.append(publisher)

else:
    logger.error("Failed -- Usage example: 'python ./start_aicn.py <num_nodes> <num_publishers> "
                 "[<registry_ip> <registry_port>]'")
    exit()

# Start all threads
for thread in ThreadList:
    thread.start()

# Wait for all threads
for thread in ThreadList:
    thread.join()
