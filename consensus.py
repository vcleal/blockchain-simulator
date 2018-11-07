from block import Block
import random
import hashlib
import datetime
import threading
import blockchain
import sqlite3

MSG_LASTBLOCK = 'getlastblock'
MSG_BLOCK = 'block'
MSG_BLOCKS = 'getblocks'
MSG_HELLO = 'hello'

def handleMessages(bc, messages, cursor):
    cmd = messages[0].lower() # test if str?
    if cmd == MSG_LASTBLOCK:
        return bc.getLastBlock()
    elif cmd == MSG_HELLO:
        return MSG_HELLO
    elif cmd == MSG_BLOCKS:
        # check blocks in db
        cursor.execute('SELECT * FROM blocks WHERE id BETWEEN ? AND ?', (messages[1],messages[2]))
        return cursor.fetchall()
    elif cmd == MSG_BLOCK:
        # change to isolated function
        cursor.execute('SELECT * FROM blocks WHERE id = ?', (messages[1],))
        return cursor.fetchone()
    else:
        return None

class Consensus:

    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.type = "PoW"
        self.MAX_NONCE = 2 ** 32
        self.target = 2 ** (4 * self.difficulty) - 1
    
    def POW(self, lastBlock, stop):
        # chr simplifies merkle root and add randomness
        timestamp = str(datetime.datetime.now())
        header = chr(random.randint(1,100)) + str(lastBlock.index + 1) + str(lastBlock.hash) + timestamp
        for nonce in xrange(self.MAX_NONCE):
            if stop.is_set():
                return False, False, False
            hash_result = hashlib.sha256(str(header)+str(nonce)).hexdigest()
            if int(hash_result[0:self.difficulty], 16) == 0:
                #print("Mined Block " + b.hash)
                return hash_result, nonce, timestamp
        return False, nonce, timestamp
   

    def validateBlock(self, lastBlock, Block):
        #if self.isuniqueindex(Block):
        return NotImplemented

    def generateNewblock(self, lastBlock, stop=False):
        while True:
            new_hash, nonce, timestamp = self.POW(lastBlock, stop)
            if not nonce:
                return None
            if new_hash:
                return Block(lastBlock.index + 1, lastBlock.hash, nonce, new_hash, timestamp)
        
    def rawConsensusInfo():
        return {'difficulty': self.difficulty, 'type': self.type}
