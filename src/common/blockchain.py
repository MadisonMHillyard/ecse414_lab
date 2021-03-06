import hashlib
import json
from time import time
import binascii
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA


class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []

        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: A blockchain
        :return: True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            last_block_hash = self.hash(last_block)

            # Check that signature is correct for each transactino in the block
            for transaction in block["transactions"]:
                current = {
                            'origin': transaction["origin"],
                            'weights': transaction["weights"],
                            'bias': transaction["bias"]
                        }
                signature = binascii.unhexlify(bytes(transaction["signature"],'utf-8'))
                sender_public_key = bytes(transaction['sender_public_key'], 'utf-8')
                if not self.verify_transaction_signature(current, signature, sender_public_key):
                    print("Transaction signature wasnt valid")
                    return False
                print("Transaction signature was valid")


            # Check that the hash of the block is correct
            # last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self, incoming_chain):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: True if our chain was replaced, False if not
        """

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Verify new chain against current chain
        length = len(incoming_chain)
        chain = incoming_chain

        # Check if the length is longer and the chain is valid
        if length > max_length and self.valid_chain(chain):
            self.chain = incoming_chain
            return True

        return False

    def new_block(self, proof, previous_hash):
        """
        Create a new Block in the Blockchain
        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :return: New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def generate_transaction_signature(self, transaction_data, sender_private_key):
        signature_source_data = SHA.new(str(transaction_data).encode('utf8'))
        signer = PKCS1_v1_5.new(sender_private_key)
        signature = signer.sign(signature_source_data)
        return signature

    def verify_transaction_signature(self, transaction_data, transaction_signature, sender_public_key):
        public_key = RSA.importKey(sender_public_key)
        verifier = PKCS1_v1_5.new(public_key)
        expected_signature_source_data = SHA.new(str(transaction_data).encode('utf8'))
        verification_result = verifier.verify(expected_signature_source_data, transaction_signature)
        return verification_result

    def new_transaction(self, origin, weights, bias, sender_public_key, sender_private_key):
        """
        Creates a new transaction to go into the next mined Block
        :param self: 
        :param origin:
        :param weights:
        :param bias: 
        :return: The index of the Block that will hold this transaction
        """
        current = {
            'origin': origin,
            'weights': weights,
            'bias': bias
        }
        signature = self.generate_transaction_signature(current,sender_private_key)

        current['signature'] =  str(binascii.hexlify(signature),'utf-8')
        #print(current['signature'])

        current['sender_public_key'] = str(sender_public_key.exportKey("PEM"),'utf-8')
        #print(current['sender_public_key'])

        #print(json.dumps(current))

        self.current_transactions.append(current)

        return self.last_block['index'] + 1
    
    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block
        :param block: Block
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes
         - Where p is the previous proof, and p' is the new proof

        :param last_block: <dict> last Block
        :return: <int>
        """

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        """
        Validates the Proof
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :param last_hash: <str> The hash of the Previous Block
        :return: <bool> True if correct, False if not.
        """

        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
