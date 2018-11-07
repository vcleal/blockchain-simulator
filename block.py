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
            self.hash = b_hash
        else:
            self.hash = self.calcBlockhash()

    def calcBlockhash(self):
        h = str(self.index) + str(self.timestamp) + self.prev_hash + str(self.nonce)
        return hashlib.sha256(h.encode('utf-8')).hexdigest()

    def rawblockInfo(self):
        return {'index': str(self.index) , 'timestamp': str(self.timestamp) , 'prev_hash': self.prev_hash , 'hash': self.hash, 'nonce': str(self.nonce)}
    
    def blockInfo(self):
        return json.dumps(self.rawblockInfo(), indent=4)

def dbtoBlock(b):
    if isinstance(b, Block) or b is None:
        return b
    else:
        return Block(b[0],b[2],b[4],b[3],b[1])