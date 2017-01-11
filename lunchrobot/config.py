import re

"""
It does not work anyway.
"""
ORDER_ZUPA = False


USERNAME = "example@random.pl"
PASSWD = "password123"


RULES = [
    re.compile(r'[Aa]grest.*'),
    re.compile(r'[Ss]chab.*'),
    re.compile(r'[Kk]otlet.*')
]


"""
Check every X minutes if it's a time
to order a meal.
"""
CHECK_EVERY = 10


"""
Since STARTING_TIME script will try
to order meal.
"""
STARTING_TIME = 9, 30