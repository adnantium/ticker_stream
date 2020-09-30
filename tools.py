
import logging
import logging.config

import string
import random

def build_tickertape_uid(m):
    """Build a uid key for an tickertape message"""
    uid_fields = ["symbol"]
    return build_uid(m, uid_fields)

def get_logger(name, filename='logging.conf'):
    logging.config.fileConfig(filename)
    return logging.getLogger(name)

def make_fake_tick():
    symbol = ''.join(random.choices(string.ascii_uppercase, k=4))
    price = random.randrange(1, 100)
    return {symbol: price}
