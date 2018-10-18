import Blockchain
import Node
from collections import deque
import random

class POW:
    def __init__(self):
        pass
    
    # Para iniciar o consenso os usuarios deven registrar seu stake por meio de uma mensagem 'REGISTER'
    # Para iniciar o sorteio todos os peers online devem ter executado a função de consenso e enviar a mensagem 'ELECT'
    # uma vez finalizado o sorteio se envia o mensagem 'ELECTED' ao ganhador e trocar o role a 'MINTER', este deve criar o novo bloco e coloca-lo na cadeia
    # Iniciar o processo de Novo
    
    def lottery(self, Node):
        peers = Node.getPeers()
        sum = get_total_stake()
        probabilities = [x.getstake() / sum for x in peers]
        elected = random_pick(peers, probabilities)
        return elected, 'ELECTED', 'MINTER' 
        
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