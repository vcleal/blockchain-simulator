import block
import random
import hashlib
import datetime
import threading
import blockchain
import sqldb
import wallet

MSG_LASTBLOCK = 'getlastblock'
MSG_BLOCK = 'block'
MSG_BLOCKS = 'getblocks'
MSG_HELLO = 'hello'

def handleMessages(bc, messages):
    cmd = messages[0] if isinstance(messages, list) else str(messages)
    cmd = cmd.lower()
    if cmd == MSG_LASTBLOCK:
        return bc.getLastBlock() # sql query?
    elif cmd == MSG_HELLO:
        return MSG_HELLO
    elif cmd == MSG_BLOCKS:
        return sqldb.blocksQuery(messages)
    elif cmd == MSG_BLOCK:
        return sqldb.blockQuery(messages)
    else:
        return None

def validateBlockHeader(b):
    # check block header
    if b.hash == b.calcBlockhash():
        return True
    return False

def validateBlock(block, lastBlock):
    # check block chaining
    if block.prev_hash == lastBlock.hash:
        return True
    return False

def validateChain(bc, l):
    lastBlock = bc.getLastBlock()
    #print lastBlock.blockInfo()
    for b in l:
        #print b
        b = sqldb.dbtoBlock(b)  # maybe avoid converting
        # validade block header ?
        #validateBlockHeader(b)
        if validateBlock(b, lastBlock):
            lastBlock = b
            bc.addBlocktoBlockchain(b)
            sqldb.writeBlock(b)
        else: # fork
            #sqldb.writeFork(b)
            return b
    return None

class Consensus:

    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.type = "PoW"
        self.MAX_NONCE = 2 ** 32
        self.target = 2 ** (4 * self.difficulty) - 1
    
    def POW(self, lastBlock, stop):
        # TODO change stop to skip
        # chr simplifies merkle root and add randomness
        tx = chr(random.randint(1,100))
        mroot = hashlib.sha256(tx).hexdigest()
        timestamp = str(datetime.datetime.now())
        c_header = str(lastBlock.hash) + mroot + timestamp # candidate header
        for nonce in xrange(self.MAX_NONCE):
            if stop.is_set():
                return False, False, False, False
            hash_result = hashlib.sha256(str(c_header)+str(nonce)).hexdigest()
            if int(hash_result[0:self.difficulty], 16) == 0:
                #print("Mined Block " + b.hash)
                return hash_result, nonce, timestamp, tx
        return False, nonce, timestamp, tx
    
    def POS(self, lastBlock, r, stake, stop):
        tx = chr(random.randint(1,100))
        mroot = hashlib.sha256(tx).hexdigest()
        c_header = str(lastBlock.hash) + mroot
        round = lastBlock.round + r 
        if stop.is_set():
            return False, False, False, False
        hash_result = hashlib.sha256(str(c_header) + str(round)).hexdigest()    
        if hash_result < stake * self.target:
            return hash_result, tx
        return False, tx

    def generateNewblock(self, lastBlock, stop=False):
        r = 0
        while True:
            if self.type == 'PoW':
                new_hash, nonce, timestamp, tx = self.POW(lastBlock, stop)
                if not nonce:
                    return None
                if new_hash:
                    return block.Block(lastBlock.index + 1, lastBlock.hash, nonce, new_hash, timestamp, tx)
            elif self.type == 'PoS':
                r = r + 1
                new_hash, tx = self.POS(lastBlock, r, wallet.getStake(),stop)
                if new_hash:
                    last_arrive_time =  new_arrive_time
                    new_arrive_time = str(datetime.datetime.now())
                    return block.Block(lastBlock.index + 1, lastBlock.hash, nonce, new_hash, timestamp, tx)
        
    def rawConsensusInfo(self):
        return {'difficulty': self.difficulty, 'type': self.type}
