import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

DIFFICULTY = 3


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash="genesis", proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.last_block)
        }

        # Resets the current list of transactions
        self.current_transactions = []
        # Append the chain to the block
        self.chain.append(block)

        return block

    def new_transaction(self, sender=0, recipient="you", amount=1):

        transaction = {
            "index": len(self.current_transactions) + 1,
            "timestamp": time(),
            "sender": sender,
            "recipient": recipient,
            "amount": amount
        }

        self.current_transactions.append(transaction)

        return len(self.chain) + 1

    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        # Use json.dumps to convert json into a string
        # Use hashlib.sha256 to create a hash
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        # It convertes the string to bytes.
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes

        # TODO: Create the block_string
        block_string = json.dumps(block, sort_keys=True).encode()
        # TODO: Hash this string using sha256
        hash_value = hashlib.sha256(block_string).hexdigest()

        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand

        # TODO: Return the hashed block string in hexadecimal format
        return hash_value

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 3
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """
        block_string = json.dumps(block_string, sort_keys=True)
        guess_string = f'{block_string}{proof}'.encode()
        guess = hashlib.sha256(guess_string).hexdigest()
        print(guess)
        # return True or False
        return guess[:DIFFICULTY] == '0' * DIFFICULTY


# Instantiate our Node
app = Flask(__name__)
# app.config['JSON_SORT_KEYS'] = False

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['POST'])
def mine():
    data = request.get_json()
    proof = data['proof']
    # if data.proof and data.id:
    if blockchain.valid_proof(blockchain.last_block, proof):
        previous_hash_value = blockchain.hash(blockchain.last_block)
        new_block = blockchain.new_block(proof, previous_hash_value)
        response = {
            'message': 'New Block Forged',
            'new_block': new_block
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'Nope nope nope nope nope. Try again.'
        }
        return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    data = request.get_json()
    miner_id = data['id']
    try:
        block_index = blockchain.new_transaction(recipient=miner_id)
        response = {
            'message': f"Transaction added to block #{block_index}"
        }
        return jsonify(response), 200
    except:
        response = {
            'message': "Something went wrong. Please try again"
        }
        return jsonify(response), 400


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


@app.route('/last_block', methods=['GET'])
def last_block():
    print("Server-side last block: ", blockchain.last_block)
    response = {
        'last_block': blockchain.last_block
    }
    return jsonify(response), 200


# Run the program on port 5000
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
