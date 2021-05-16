# ecse414_lab

#### Authors:

Madison M Hillyard (madison.hillyard@case.edu)

Andrew Dupuis (andrew.dupuis@case.edu)


## Description

This lab is a blockchain enabled distributed machine learning system for facial recognition.

## To Run

To install:
1. Clone the repo
2. Run ```python3 -m pip -r requirements.txt```

To run  the registry:
1. Open a terminal
2. ```cd LOCAL/PATH/TO/REPO/```
3. In the terminal run ```python3 ./start_registry.py```
   
To create and run the nodes:
1. Open a terminal
2.  ```cd LOCAL/PATH/TO/REPO/```
3. In the terminal run ```python3 ./start_processing_manager.py <NUM_NODES> <NUM_PUBLISHERS> <REGISTRY_FQDN> <REGISTRY_PORT>```
   
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
2.  ```cd LOCAL/PATH/TO/REPO/```
3.  ```python3 run_all_tests.py``

### Test Descriptions

1. test_signature_verification:
2. test_original_block_validity:
   1. Tests for the correct formation of a block made by the blockchain class
3. test_proof_of_work:
   1. Tests that the mining process returns an integer
   2. Tests that the mining process returns a value that is not None
4. test_conflict_resolution:
   1. Tests that on receipt of a correctly formatted chain containing more blocks, the blockchain class will correctly update the local chain to the incoming chain.
   2. Tests that on the receipt of an incorrectly formatted chain containing more block, the blockchain will not update the local chain.
   3. Tests that on the receipt of a chain containing fewer blocks, the blockchain will not update the local chain. 
5. test_block_creation:
   1. Tests that the new block has been appended to the blockchain
   2. Tests that the new block contains the previous block's hash
6. test_create_transaction:
   1. Tests that the new transaction has been appended to the transaction list
   2. Tests that the new transaction contains the updated gradients