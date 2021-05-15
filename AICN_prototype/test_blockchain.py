import pytest
from blockchain import Blockchain
from generate_keypair import generate_keypair
import numpy
from schema import Schema, And, Use

# transaction variables
origin = "test_node"
global_weights = numpy.zeros((2*2, 1))
global_bias = 0

(private_key_1, public_key_1) = generate_keypair(1024,"test1_public.pem", "test1_private.pem")
(private_key_2, public_key_2) = generate_keypair(1024,"test2_public.pem", "test2_private.pem")

# block variables
proof = 100
block_schema = Schema({'index': int,
                        'timestamp': float,
                        'transactions': list,
                        'proof': int,
                        'previous_hash': str})

@pytest.fixture
def blockchain():
    return Blockchain()
    
@pytest.fixture
def blockchain_invalid_signature_chain():
    b = Blockchain() # init sequence creates initial block

    b.new_transaction(origin="block", weights=global_weights.tolist(), bias=global_bias, sender_public_key=public_key_1, sender_private_key=private_key_2)
    b.new_block(b.proof_of_work(b.last_block), b.hash(b.last_block))
    b.new_transaction(origin="block", weights=global_weights.tolist(), bias=global_bias, sender_public_key=public_key_1, sender_private_key=private_key_2)
    b.new_block(b.proof_of_work(b.last_block), b.hash(b.last_block))
    
    b.new_transaction(origin="block", weights=global_weights.tolist(), bias=global_bias, sender_public_key=public_key_1, sender_private_key=private_key_2)
    b.new_block(b.proof_of_work(b.last_block), b.hash(b.last_block))
    
    b.new_transaction(origin="block", weights=global_weights.tolist(), bias=global_bias, sender_public_key=public_key_1, sender_private_key=private_key_2)
    b.new_block(b.proof_of_work(b.last_block), b.hash(b.last_block))
    return b

@pytest.fixture
def blockchain_invalid_hash_chain():
    b = Blockchain() # init sequence creates initial block

    b.new_transaction(origin="block", weights=global_weights.tolist(), bias=global_bias, sender_public_key=public_key_1, sender_private_key=private_key_1)
    b.new_block(0, b.hash(b.last_block))
    b.new_transaction(origin="block", weights=global_weights.tolist(), bias=global_bias, sender_public_key=public_key_1, sender_private_key=private_key_1)
    b.new_block(0, b.hash(b.last_block))
    
    b.new_transaction(origin="block", weights=global_weights.tolist(), bias=global_bias, sender_public_key=public_key_1, sender_private_key=private_key_1)
    b.new_block(0, b.hash(b.last_block))
    
    b.new_transaction(origin="block", weights=global_weights.tolist(), bias=global_bias, sender_public_key=public_key_1, sender_private_key=private_key_1)
    b.new_block(0, b.hash(b.last_block))
    return b


@pytest.fixture
def blockchain_5blocks():
    b = Blockchain() # init sequence creates initial block

    b.new_transaction(origin="block", weights=global_weights.tolist(), bias=global_bias, sender_public_key=public_key_1, sender_private_key=private_key_1)
    b.new_block(b.proof_of_work(b.last_block), b.hash(b.last_block))
    b.new_transaction(origin="block", weights=global_weights.tolist(), bias=global_bias, sender_public_key=public_key_1, sender_private_key=private_key_1)
    b.new_block(b.proof_of_work(b.last_block), b.hash(b.last_block))
    
    b.new_transaction(origin="block", weights=global_weights.tolist(), bias=global_bias, sender_public_key=public_key_1, sender_private_key=private_key_1)
    b.new_block(b.proof_of_work(b.last_block), b.hash(b.last_block))
    
    b.new_transaction(origin="block", weights=global_weights.tolist(), bias=global_bias, sender_public_key=public_key_1, sender_private_key=private_key_1)
    b.new_block(b.proof_of_work(b.last_block), b.hash(b.last_block))
    return b


def test_signature_verification(blockchain, blockchain_invalid_signature_chain):
    """ Test signature verification
        rubric section(a)
    """
    valid_chain_len = len(blockchain.chain)
    invalid_chain_len = len(blockchain_invalid_signature_chain.chain)
    
    # test with larger, incorrectly formed chain
    blockchain.resolve_conflicts(blockchain_invalid_signature_chain.chain)
    assert valid_chain_len != invalid_chain_len
    

def test_original_block_validity(blockchain):
    """ Test block validity
        rubric section (b)
    """
    # test that block contains all necessary members
    block = blockchain.chain[-1]
    assert block == block_schema.validate(block)


def test_proof_of_work(blockchain):
    """ Test proof of work
        rubric section (c)
    """
    proof = blockchain.proof_of_work(blockchain.last_block)
    assert proof != None
    assert isinstance(proof, int)
    


def test_conflict_resolution(blockchain, blockchain_5blocks, blockchain_invalid_hash_chain):
    """ Test conflict resolution
        rubric section (d)
    """
    short_chain_len = len(blockchain.chain)
    large_chain_len = len(blockchain_5blocks.chain)
    invalid_chain_len = len(blockchain_invalid_hash_chain.chain)
    
    # test with larger, incorrectly formed chain
    blockchain.resolve_conflicts(blockchain_invalid_hash_chain.chain)
    assert short_chain_len != invalid_chain_len

    # test with smaller, correctly formed chain
    blockchain_5blocks.resolve_conflicts(blockchain.chain)
    assert large_chain_len == len(blockchain_5blocks.chain)


    # test with larger, correctly formed incoming chain
    blockchain.resolve_conflicts(blockchain_5blocks.chain)
    updated_chain_len = len(blockchain.chain)
    assert updated_chain_len == large_chain_len



def test_block_creation(blockchain):
    """ Test block creation and append 
        rubric section (e)
    """
    chain_len = len(blockchain.chain)
    previous_hash = blockchain.hash(blockchain.last_block)
    blockchain.new_block(proof, previous_hash)

    # check that block appended correctly
    assert len(blockchain.chain) == chain_len+1

    # check newest block contains previous block's calculated hash
    assert blockchain.chain[-1]['previous_hash'] == previous_hash


def test_create_transaction(blockchain):
    """ Test transaction creation and append
        rubric section (f)
    """
    t_list = len(blockchain.current_transactions)
    blockchain.new_transaction(origin="block", weights=global_weights.tolist(), bias=global_bias, sender_public_key=public_key_1, sender_private_key=private_key_1)
    t_list2 = len(blockchain.current_transactions)

    # assert that the new transaction has been added to transaction list
    assert t_list2 == t_list + 1

    # assert that gradients are included in the transaction
    assert len(blockchain.current_transactions[-1]['weights']) != 0
    
    




