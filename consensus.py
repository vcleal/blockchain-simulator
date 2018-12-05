import block
import random
import hashlib
import datetime
import threading
import blockchain
import sqldb

MSG_LASTBLOCK = 'getlastblock'
MSG_BLOCK = 'block'
MSG_BLOCKS = 'getblocks'
MSG_HELLO = 'hello'
MSG_PEERS = 'peers'

def handleMessages(bc, messages):
    cmd = messages[0] if isinstance(messages, list) else str(messages)
    cmd = cmd.lower()
    if cmd == MSG_LASTBLOCK:
        return bc.getLastBlock()
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
    for b in l:
        b = sqldb.dbtoBlock(b)
        if not validateBlockHeader(b): # invalid
            return b, True
        if validateBlock(b, lastBlock):
            lastBlock = b
            bc.addBlocktoBlockchain(b)
            sqldb.writeAll(b)
        else: # fork
            return b, False
    return None, False

def selectChain():
    pass

class Consensus:

    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.type = "PoW"
        self.MAX_NONCE = 2 ** 32
        self.target = 2 ** (4 * self.difficulty) - 1
    
    def POW(self, lastBlock, skip):
        """ Find nonce for PoW returning block information """
        # chr simplifies merkle root and add randomness
        tx = chr(random.randint(1,100))
        mroot = hashlib.sha256(tx).hexdigest()
        timestamp = str(datetime.datetime.now())
        c_header = str(lastBlock.hash) + mroot + timestamp # candidate header
        for nonce in xrange(self.MAX_NONCE):
            if skip.is_set():
                return False, False, False, False
            hash_result = hashlib.sha256(str(c_header)+str(nonce)).hexdigest()
            if int(hash_result[0:self.difficulty], 16) == 0:
                #print("Mined Block " + b.hash)
                return hash_result, nonce, timestamp, tx
        return False, nonce, timestamp, tx

    def generateNewblock(self, lastBlock, skip=False):
        """ Loop for PoW in case of reaching MAX_NONCE, returning new Block object """
        while True:
            new_hash, nonce, timestamp, tx = self.POW(lastBlock, skip)
            if not nonce:
                return None
            if new_hash:
                return block.Block(lastBlock.index + 1, lastBlock.hash, nonce, new_hash, timestamp, tx)
        
    def rawConsensusInfo(self):
        return {'difficulty': self.difficulty, 'type': self.type}
