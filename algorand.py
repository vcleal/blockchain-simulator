import Blockchain
import Node
import math
from scipy.stats import binom

#TODO Verificable Random Function
#TODO SeedGeneration
#TODO Message Control

class algorand:
    def __init__(self):
        pass
    
    def sortition(sk, seed, tau, role, w, W):
        hash, pi = crypto.vrf(seed+role,sk) 
        p = tau / W
        j = 0
        
        while not isinrangebinom(w,p,ub):
            j =+1
       
        return hash. pi, j
    
     def verifysortition(pk, hash, pi, seed, tau, role, w, W):
         if not verifyvrf(hash, pi, seed+role, pk):
            return 0

         p = tau / W
         
         while not isinrangebinom(w,p,ub):
             j =+ 1
         
         return j
 
     def totalbinom(n, p, ub):
         sum = 0
         for k=0 in xrange(ub):
             sum =+ binom.pmf(k ,n ,p)
         return sum

     def isinrangebinom(n, p, ub):
         return hash / (2 ** len(hash)) >= totalbinom(n, p, ub) and hash / (2 ** len(hash)) < totalbinom(n, p, ub+1)

     def baast(ctx, round, block):
         hblock = reduction(ctx, round, hash(block))
         hblockast = binaryba(ctx, round, hashblock)
         
         r = countvotes(ctx, round, 'FINAL', Tfinal, taufinal, timeoutstep) 

         if blockhash == r:
             return 'FINAL', blockofhash(hblockast)
         else:
             return 'TENTATIVE', blockofhash(hblockast)

     def committevote(ctx, round, step, tau, value):
         role = [comitee, round, step]
         sorthash, pi, j = sortition(user.sk, ctx.semente, tau, role, ctx.weight[user.pk], ctx.W)
         if j > 0:
            gossip([user.pk, signed(round, step, sorthash, pi, hash(ctx.last), value)])

     def countvotes(ctx, rodada, step, T, tau, timeout):
          
