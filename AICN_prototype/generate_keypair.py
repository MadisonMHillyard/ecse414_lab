import sys
from Crypto.PublicKey import RSA

def generate_private_key(bits=1024, private_pem_output_path="private.pem"):
    key = RSA.generate(bits)
    f = open(private_pem_output_path, "wb")
    f.write(key.exportKey('PEM'))
    f.close()

def generate_public_key(private_pem_path="private.pem", public_pem_output_path="public.pem"):
    f = open(private_pem_path, "rb")

    key = RSA.importKey(f.read())

    pubkey = key.publickey()
    f = open(public_pem_output_path, "wb")
    f.write(pubkey.exportKey('PEM'))
    f.close()


def main():
    if len(sys.argv) == 2:
        generate_private_key(sys.argv[1])
        generate_public_key()
    elif len(sys.argv) == 4:
        generate_private_key(sys.argv[1], sys.agv[2])
        generate_public_key(sys.argv[2], sys.argv[3])
    else:
        generate_private_key()
        generate_public_key()
   
if __name__ == '__main__':
    main()

