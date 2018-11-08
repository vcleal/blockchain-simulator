import datetime
import hashlib
import random
import json


class Block:
    def __init__(self, index, prev_hash, nonce, b_hash=None, timestamp=str(datetime.datetime.now())):
        self.index = index
        self.timestamp = timestamp
        self.prev_hash = prev_hash
        self.nonce = nonce
        if b_hash:
            self.tx = chr(random.randint(1,100)) # TODO Merkle tree class
            self.hash = b_hash
        else: # mostly genesis
            self.tx = ''
            self.hash = self.calcBlockhash()
        self.mroot = self.calcMerkleRoot()

    def calcMerkleRoot(self):
        return hashlib.sha256(self.tx).hexdigest()

    def calcBlockhash(self):
        h = str(self.index) + str(self.timestamp) + self.prev_hash + str(self.nonce) + self.tx
        return hashlib.sha256(h.encode('utf-8')).hexdigest()

    def rawblockInfo(self):
        return {'index': str(self.index) , 'timestamp': str(self.timestamp) , 'prev_hash': self.prev_hash , 'hash': self.hash, 'nonce': str(self.nonce), 'merkle_root': self.mroot}
    
    def blockInfo(self):
        return json.dumps(self.rawblockInfo(), indent=4)

def dbtoBlock(b):
    if isinstance(b, Block) or b is None:
        return b
    else:
        return Block(b[0],b[2],b[4],b[3],b[1])