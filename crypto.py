from fastecdsa import keys, curve, ecdsa
import hashlib
import random

def gen_vrf_keys(value, sk):
    return NotImplemented

def vrf(value, sk):
    return NotImplemented

def verify_vrf(value, sk):
    return NotImplemented

def hash(value):
    return hashlib.sha256(value).hexdigest()

def sign(message, private_key):
    r, s = ecdsa.sign(message, private_key)
    return r, s

def ver_sign(r, s, message, public_key):
    if ecdsa.verify((r, s), message, public_key):
        return True
    else:
        return False

def gen_sign_keys():
    return keys.gen_keypair(curve.secp256k1)   