from random import randint


def generate_wallet_number():
    return f"302{str(randint(1000000, 9999999))}"


# To generate cypher key run it once...
from cryptography.fernet import Fernet

key = Fernet.generate_key()
print(key.decode())