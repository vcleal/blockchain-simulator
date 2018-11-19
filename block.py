import datetime
import hashlib
import random
import json


class Block:
    def __init__(self, index, prev_hash, nonce, b_hash=None, timestamp=str(datetime.datetime.now()), tx=''):
        self.index = index
        self.timestamp = timestamp
        self.prev_hash = prev_hash
        self.nonce = nonce
        self.tx = tx
        self.mroot = self.calcMerkleRoot()
        if b_hash:
            self.hash = b_hash
        else: # mostly genesis
            self.hash = self.calcBlockhash()

    # TODO Merkle tree class
    def calcMerkleRoot(self):
        return hashlib.sha256(self.tx).hexdigest()

    def calcBlockhash(self):
        # Check concatenate order
        h = self.prev_hash + self.mroot + str(self.timestamp) + str(self.nonce)
        return hashlib.sha256(h.encode('utf-8')).hexdigest()

    def rawblockInfo(self):
        return {'index': str(self.index) , 'timestamp': str(self.timestamp) , 'prev_hash': self.prev_hash , 'hash': self.hash, 'nonce': str(self.nonce), 'merkle_root': self.mroot, 'tx': self.tx}
    
    def blockInfo(self):
        return json.dumps(self.rawblockInfo(), indent=4)