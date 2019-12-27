import itertools
from collections import namedtuple

Card = namedtuple('Card', ['value', 'suit'])
deck_ = itertools.product(range(1, 13), ['S', 'H', 'D', 'C'])
deck = set([Card(*card_) for card_ in deck_])
