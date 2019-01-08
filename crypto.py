from Crypto.PublicKey import DSA
from Crypto.Hash import SHA
from Crypto.Random import random

def gen_vrf_keys(value, sk):
    return NotImplemented

def vrf(value, sk):
    return NotImplemented

def verify_vrf(value, sk):
    return NotImplemented

def hash(value):
    return SHA.new(value).digest()

def sign(message, keys):
    r = random.StrongRandom().randint(1,keys.q-1)
    sig = keys.sign(message, r)
    return sig

def ver_sign(keys, message, sig):
    if keys.verify(message,sig):
        return True
    else:
        return False

def gen_sign_keys():
    return DSA.generate(1024)
        