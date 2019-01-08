import blockchain
import node
import math
import crypto
from scipy.stats import binom

#TODO Verificable Random Function
#TODO SeedGeneration
#TODO Message Control

class algorand:
    def __init__(self):
        pass
    
    def sortition(self, sk, seed, tau, role, w, W):
        hash, proof = crypto.vrf(seed+role,sk) 
        p = tau / W
        j = 0
        
        while not self.isinrangebinom(w,p,ub):
            j =+1
       
        return hash, proof, j
    
    def verifysortition(self, pk, hash, pi, seed, tau, role, w, W):
        if not crypto.verify_vrf(hash, pi, seed+role, pk):
           return 0

        p = tau / W
        
        while not self.isinrangebinom(w,p,ub):
            j =+ 1
         
        return j
 
    def totalbinom(self, n, p, ub):
        sum = 0
        for k in xrange(ub):
            sum =+ binom.pmf(k ,n ,p)
        return sum

    def isinrangebinom(self, n, p, ub):
        return hash / (2 ** len(hash)) >= self.totalbinom(n, p, ub) and hash / (2 ** len(hash)) < self.totalbinom(n, p, ub+1)

    def baast(self, ctx, round, block):
        hblock = self.reduction(ctx, round, hash(block))
        hblockast = self.binaryba(ctx, round, hashblock)
        
        r = countvotes(ctx, round, 'FINAL', Tfinal, taufinal, timeoutstep) 

        if blockhash == r:
            return 'FINAL', blockofhash(hblockast)
        else:
            return 'TENTATIVE', blockofhash(hblockast)

    def committevote(self, ctx, round, step, tau, value):
        role = [commitee, round, step]
        sorthash, pi, j = self.sortition(user.sk, ctx.semente, tau, role, ctx.weight[user.pk], ctx.W)
        if j > 0:
            gossip([user.pk, signed(round, step, sorthash, pi, hash(ctx.last), value)])

    def countvotes(self, ctx, rodada, step, T, tau, timeout):
        return NotImplemented

    def reduction(self, ctx, round, hash):
        return NotImplemented         
