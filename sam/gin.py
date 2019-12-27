import cards
import value

def play(hand, discard):
    assert(type(hand) is set)
    assert(type(discard) is list)
    top_discard = discard[-1]
    deck = cards.deck - set(discard) - set(hand)
