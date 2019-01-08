import node
import block
import datetime
from collections import deque
import random
import hashlib
import crypto

#TODO Register peer and set Stake
#TODO use message to start minting
#TODO process to verify minter

MSG_REGISTER = "stake-register"
MSG_VERIFY = "verify-block"


class POS:
    def __init__(self, round):
        self.difficulty = 8
        self.target = 2 ** (4 * self.difficulty) - 1
        self.round  = round
        self.keys = None
    
    # Para iniciar o consenso os usuarios deven se registrar por meio de uma mensagem 'REGISTER'
    # Para iniciar o sorteio todos os peers online devem ter executado a função de consenso e enviar a mensagem 'ELECT'
    # uma vez finalizado o sorteio se envia o mensagem 'ELECTED' com um valor '1' se ganha caso contrario '0' e trocar o role a 'MINTER', este deve criar o novo bloco e coloca-lo na cadeia
    # Iniciar o processo de Novo
    
    def register(self, Node):
        # Estabelecer o stake na rodada
        # enviar mensagem 'REGISTER',Node  para entrar no processo de consenso
        # se recebe o mensagem 'REGISTERED', Node  como ACK
        
        return NotImplemented
    
    def election(self, hash, Node):
        if (int(hash, 16) < (Node.balance * self.target)):
            return True
        else:
            return False

   
    def mint(self, Node, lastBlock, stop):
        tx = chr(random.randint(1,100))
        mroot = hashlib.sha256(tx).hexdigest()
        timestamp = str(datetime.datetime.now())
        c_header = str(lastBlock.hash) + mroot + timestamp
        keys = Node.keys()
        signature = crypto.sign(str(lastBlock.index + 1) + str(lastBlock.hash),keys)
        hash_result = crypto.hash(str(c_header))
        if stop.is_set():
            return False, False, False, False
        elected = self.election(Node, lastBlock)
        if elected:
            return block.Block(lastBlock.index + 1, lastBlock.hash,keys,signature,hash_result)
        
    def verify_minter(self, s, Node):
        #if 
        # enviar uma menssagem para saber quem foi escolhido 
        return NotImplemented
    
        
    # def random_pick(some_list, probabilities):
    #     x = random.uniform(0, 1)
    #     cumulative_probability = 0.0
    #     for item, item_probability in zip(some_list, probabilities):
    #         cumulative_probability += item_probability
    #         if x < cumulative_probability: break
    #     return item
    
    # def get_total_stake(peerlist):
    #     sum = 0
    #     for i in peerlist:
    #         sum =+ i.getstake()
            
    #     return sum

    # def lottery(self, Node):
        #     peers = Node.getPeers()
        #     sum = get_total_stake()
        #     probabilities = [x.getstake() / sum for x in peers]
        #     elected = random_pick(peers, probabilities)
            # Item, Message, Value
            #if elected == Node:
            # Notificar a todos os outros nós
            # Enviar ao nó o mensagem 'ELECTED', 1 ao escolhido e 'ELECTED', 0
            #return elected, 'ELECTED', 0
                # return NotImplemented
    