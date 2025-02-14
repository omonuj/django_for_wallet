from random import randint
import uuid


def generate_wallet_number():
    return str(uuid.uuid4().int)[:10]