import secrets
import hashlib

#### a simple SHA256 key pair library #####

# generate private key
def gen_priv_key():
    return secrets.token_hex(32)

# generate public key
def gen_pub_key(priv_key):
    priv_key = priv_key.encode('utf-8')
    return hashlib.sha256(priv_key).hexdigest()