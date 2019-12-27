import itertools
from collections import namedtuple

Card = namedtuple('Card', ['value', 'suit'])
deck_ = itertools.product(range(1, 13), ['S', 'H', 'D', 'C'])
deck = set([Card(*card_) for card_ in deck_])

test_hand = [Card(value=7, suit='H'), Card(value=2, suit='C'), Card(value=4, suit='S'), Card(value=2, suit='H'), Card(value=11, suit='H'), Card(value=2, suit='S'), Card(value=7, suit='C'), Card(value=3, suit='H'), Card(value=1, suit='H'), Card(value=7, suit='D')]
