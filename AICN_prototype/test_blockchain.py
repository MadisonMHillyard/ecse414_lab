import pytest
from blockchain import Blockchain
import numpy
from schema import Schema, And, Use

# transaction variables
origin = "test_node"
global_weights = numpy.zeros((2*2, 1))
global_bias = 0

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
def blockchain_5blocks():
    b = Blockchain() # init sequence creates initial block
    b.new_transaction(origin="block", weights=global_weights.tolist(), bias=global_bias)
    b.new_block(b.proof_of_work(b.last_block), b.hash(b.last_block))
    b.new_transaction(origin="block", weights=global_weights.tolist(), bias=global_bias)
    b.new_block(b.proof_of_work(b.last_block), b.hash(b.last_block))
    
    b.new_transaction(origin="block", weights=global_weights.tolist(), bias=global_bias)
    b.new_block(b.proof_of_work(b.last_block), b.hash(b.last_block))
    
    b.new_transaction(origin="block", weights=global_weights.tolist(), bias=global_bias)
    b.new_block(b.proof_of_work(b.last_block), b.hash(b.last_block))
    return b


# Test signature verification
def test_signature_verification(blockchain):
    pass

# 
def test_original_block_validity(blockchain):
    """ Test block validity
        rubric section (b)
    """
    # test that block contains all necessary members
    block = blockchain.chain[-1]
    assert block == block_schema.validate(block)

# 
def test_proof_of_work(blockchain):
    """ Test proof of work
        rubric section (c)
    """
    proof = blockchain.proof_of_work(blockchain.last_block)
    assert proof != None

# 
def test_conflict_resolution(blockchain, blockchain_5blocks):
    """ Test conflict resolution
        rubric section (d)
    """
    orig_chain_len = len(blockchain.chain)
    blockchain.resolve_conflicts(blockchain_5blocks.chain)
    updated_chain_len = len(blockchain.chain)

    assert len(blockchain.chain) == len(blockchain_5blocks.chain)
    


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
    blockchain.new_transaction(origin=origin, weights=global_weights.tolist(), bias=global_bias)
    t_list2 = len(blockchain.current_transactions)

    # assert that the new transaction has been added to transaction list
    assert t_list2 == t_list + 1

    # assert that gradients are included in the transaction
    assert len(blockchain.current_transactions[-1]['weights']) != 0
    
    




