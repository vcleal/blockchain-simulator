import sqlite3
import logging
logger = logging.getLogger(__name__)
import block
import blockchain

databaseLocation = 'blocks/blockchain.db'

def dbConnect():
    pass

def dbCheck():
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    logging.info('checking database')
    cursor.execute("""CREATE TABLE IF NOT EXISTS blocks (
        id integer primary key, 
        ctime text, 
        phash text, 
        hash text, 
        nonce integer,
        mroot text,
        tx text)""")
    cursor.execute('SELECT * FROM blocks WHERE id = (SELECT MAX(id) FROM blocks)')
    # Last block from own database
    lastBlock_db = cursor.fetchone()
    bc = blockchain.Blockchain(lastBlock_db)
    # Empty database
    if not lastBlock_db:
        genesis = bc.getLastBlock()
        writeBlock(genesis)
    db.commit()
    db.close()
    return bc

def writeBlock(b):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    try:
        if isinstance(b, list):
            cursor.executemany('INSERT INTO blocks VALUES (?,?,?,?,?,?,?)', b)
        else:
            cursor.execute('INSERT INTO blocks VALUES (?,?,?,?,?,?,?)', (
                    b.__dict__['index'],
                    b.__dict__['timestamp'],
                    b.__dict__['prev_hash'],
                    b.__dict__['hash'],
                    b.__dict__['nonce'],
                    b.__dict__['mroot'],
                    b.__dict__['tx']))
    except sqlite3.IntegrityError:
        logger.warning('db insert duplicated block')
    finally:
        db.commit()
        db.close()

def blockQuery(messages):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute('SELECT * FROM blocks WHERE id = ?', (messages[1],))
    b = cursor.fetchone()
    db.close()
    return b

def blocksQuery(messages):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    cursor.execute('SELECT * FROM blocks WHERE id BETWEEN ? AND ?', (messages[1],messages[2]))
    l = cursor.fetchall()
    db.close()
    return l

def blocksListQuery(messages):
    db = sqlite3.connect(databaseLocation)
    cursor = db.cursor()
    idlist = messages[1:]
    #idlist = [int(i) for i in messages[1:]]
    cursor.execute('SELECT * FROM blocks WHERE id IN ({0})'.format(', '.join('?' for _ in idlist)), idlist)
    l = cursor.fetchall()
    db.close()
    return 

def dbtoBlock(b):
    if isinstance(b, Block) or b is None:
        return b
    else:
        return Block(b[0],b[2],b[4],b[3],b[1],b[6])