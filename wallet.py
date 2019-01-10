import crypto

class wallet:
    def __init__(self):
        self.stake = 0
        self.sk = ""
        self.pk = ""
    
    def setStake(self, stake):
        self.stake = stake
    
    def getStake(self):
        return self.stake
    
    def generateKeys(self):
        self.sk, self.pk = crypto.gen_sign_keys()