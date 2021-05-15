# ecse414_lab

#### Authors:

Madison M Hillyard (madison.hillyard@case.edu)

Andrew Dupuis (andrew.dupuis@case.edu)


## Description

This lab is a blockchain enabled distributed machine learning system for facial recognition.

## To Run

To install:
1. Clone the repo
2. ```run python3 -m pip -r requirements.txt```

Generate Keys:


To run  the registry:
1. Open a terminal
2. ```cd LOCAL/PATH/TO/REPO/AICN_prototype/```
3. In the terminal run ```python3 ./start_aicn_registry.py <PUBLIC_KEY_PATH>```
   
To create and run the nodes:
1. Open a terminal
2.  ```cd LOCAL/PATH/TO/REPO/AICN_prototype/```
3. In the terminal run ```python3 ./start_aicn.py <NUM_NODES> <NUM_PUBLISHERS> <REGISTRY_IP> <REGISTRY_PORT> <PRIVATE_KEY_PATH>```
   
Please note the nodes can be run locally or on another machine within the network.


## Testing
The rubric of this lab includes these sections.
   1. Signature verification when sending local gradients
   2. Determination of block validity 
   3. Verification of the mining process, i.e., proof of work (PoW)
   4. Conflict resolution 
      1. Handle if 2 miners complete PoW and create new block at the same time
   5. Creation and appending new block 
      1. Inclusion of previous block's hash
   6. Creation of new transactions, i.e., 
      1. Inclusion of the updated gradients should be included
### To Run

To create and run the nodes:
1.  Open a terminal
2.  ```cd LOCAL/PATH/TO/REPO/AICN_prototype/```
3.  ```pytest test_blockchain.py```

To include a print out of results use the ```-s``` switch

### Test Descriptions

1. 