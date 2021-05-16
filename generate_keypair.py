import sys
from Crypto.PublicKey import RSA

def generate_private_key(bits=1024, private_pem_output_path="private.pem"):
    key = RSA.generate(bits)
    f = open(private_pem_output_path, "wb")
    f.write(key.exportKey('PEM'))
    f.close()
    return key

def generate_public_key(private_pem_path="private.pem", public_pem_output_path="public.pem"):
    f = open(private_pem_path, "rb")
    key = RSA.importKey(f.read())
    pubkey = key.publickey()
    f = open(public_pem_output_path, "wb")
    f.write(pubkey.exportKey('PEM'))
    f.close()
    return pubkey


def generate_keypair(bits=1024, private_pem_output_path="private.pem", public_pem_output_path="public.pem"):
    return generate_private_key(bits, private_pem_output_path), generate_public_key(private_pem_output_path,public_pem_output_path)

def main():
    if len(sys.argv) == 2:
        generate_keypair(sys.argv[1])
    elif len(sys.argv) == 4:
        generate_keypair(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        generate_keypair()

if __name__ == '__main__':
    main()

