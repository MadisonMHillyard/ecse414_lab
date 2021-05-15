# ecse414_lab

# To Run

To install:
1. Clone the repo
2. ```run python3 -m pip -r requirements.txt```

Generate Keys:
1. Open a terminal
2. ```cd LOCAL/PATH/TO/REPO```
3. In the terminal run ```python3 ./generate_keypair.py```. Optionally, select a key bit depth and .PEM locations with ```python3 ./generate_keypair.py <KEY_BITS> <PRIVATE_KEY_OUTPUT_PATH> <PUBLIC_KEY_OUTPUT_PATH>```
To run  the registry:
1. Open a terminal
2. ```cd LOCAL/PATH/TO/REPO```
3. In the terminal run ```python3 ./start_aicn_registry.py <PUBLIC_KEY_PATH>```
   
To create and run the nodes:
1. Open a terminal
2.  ```cd LOCAL/PATH/TO/REPO```
3. In the terminal run ```python3 ./start_aicn.py <NUM_NODES> <NUM_PUBLISHERS> <REGISTRY_IP> <REGISTRY_PORT> <PRIVATE_KEY_PATH>```
   
Please note the nodes can be run locally or on another machine within the network.


# To Run Testing Suite
To Run

## Test Descriptions
