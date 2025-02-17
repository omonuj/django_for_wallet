from random import randint


def generate_wallet_number(self):
    return f"302{str(randint(1000000, 9999999))}"