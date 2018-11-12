import Blockchain
import Node
import Consensus
from collections import deque
from Crypto.Random import random
from Crypto.PublicKey import DSA
import hashlib

#TODO Register peer and set Stake
#TODO use message to start minting
#TODO process to verify minter

class POS:
    def __init__(self, round):
        self.target = 2 ** (4 * self.difficulty) - 1
        self.round  = round
    
    # Para iniciar o consenso os usuarios deven se registrar por meio de uma mensagem 'REGISTER'
    # Para iniciar o sorteio todos os peers online devem ter executado a função de consenso e enviar a mensagem 'ELECT'
    # uma vez finalizado o sorteio se envia o mensagem 'ELECTED' com um valor '1' se ganha caso contrario '0' e trocar o role a 'MINTER', este deve criar o novo bloco e coloca-lo na cadeia
    # Iniciar o processo de Novo
    
    def signature(self):
        sk = DSA.generate(1024)
        h = SHA.new(message).digest()
        k = random.StrongRandom().randint(1,key.q-1)
        sig = key.sign(h,k)
        return sig
    
    def verify_signature(self):
        if key.verify(h,sig):
            return True
        else:
            return False

    def register(self, Node):
        # Estabelecer o stake na rodada
        # enviar mensagem 'REGISTER',Node  para entrar no processo de consenso
        # se recebe o mensagem 'REGISTERED', Node  como ACK
        
        return NotImplemented
    
    def lottery(self, Node):
        peers = Node.getPeers()
        sum = get_total_stake()
        probabilities = [x.getstake() / sum for x in peers]
        elected = random_pick(peers, probabilities)
        # Item, Message, Value
        if elected == Node:
           # Notificar a todos os outros nós
        # Enviar ao nó o mensagem 'ELECTED', 1 ao escolhido e 'ELECTED', 0
        #return elected, 'ELECTED', 0
            return NotImplemented
    
    def mint(self, Node, lastBlock):
        elected = random(Node, lastBlock)
        if Node == elected:
            return Block(lastBlock.index + 1, lastBlock.hash, nonce, new_hash, timestamp)
        
    def verify_minter(self):
        # enviar uma menssagem para saber quem foi escolhido 
        return NotImplemented
    
    def random(self, lastBlock, Node):
        timestamp = str(datetime.datetime.now())
        header = chr(random.randint(1,100)) + str(lastBlock.index + 1) + str(lastBlock.hash) + timestamp
        hash_result = hashlib.sha256(str(header).hexdigest()
        if (int(hash_result, 16) < (Node.balance * target)):
            return True
        else:
            return False
        
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
