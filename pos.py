import Blockchain
import Node
import Consensus
from collections import deque
import random

#TODO use message to register peer
#TODO use message to start minting
#TODO process to verify minter

class POW:
    def __init__(self):
        pass
    
    # Para iniciar o consenso os usuarios deven se registrar por meio de uma mensagem 'REGISTER'
    # Para iniciar o sorteio todos os peers online devem ter executado a função de consenso e enviar a mensagem 'ELECT'
    # uma vez finalizado o sorteio se envia o mensagem 'ELECTED' com um valor '1' se ganha caso contrario '0' e trocar o role a 'MINTER', este deve criar o novo bloco e coloca-lo na cadeia
    # Iniciar o processo de Novo
    
    def register(self, Node):
        # enviar mensagem 'REGISTER',Node  para entrar no processo de consenso
        # se recebe o mensagem 'REGISTERED', Node  como ACK
        return NotImplemented
    
    def lottery(self, Node):
        peers = Node.getPeers()
        sum = get_total_stake()
        probabilities = [x.getstake() / sum for x in peers]
        elected = random_pick(peers, probabilities)
        # Item, Message, Value
        
        # Enviar ao nó o mensagem 'ELECTED', 1 ao escolhido e 'ELECTED', 0
        return elected, 'ELECTED', 0
    
    def mint(self, Node):
        elected, message, value = lottery(Node)
        if Node == elected and message == "ELECTED":
            return Block(lastBlock.index + 1, lastBlock.hash, nonce, new_hash, timestamp)
        
    def verify_minter(self):
        # message = 'VERIFY-ELECT'
        # enviar uma menssagem para saber quem foi escolhido 
        return NotImplemented
        
    def random_pick(some_list, probabilities):
        x = random.uniform(0, 1)
        cumulative_probability = 0.0
        for item, item_probability in zip(some_list, probabilities):
            cumulative_probability += item_probability
            if x < cumulative_probability: break
        return item
    
    def get_total_stake(peerlist):
        sum = 0
        for i in peerlist:
            sum =+ i.getstake()
            
        return sum
