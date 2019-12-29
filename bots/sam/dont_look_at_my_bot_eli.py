import sys
sys.path.append('../..')
import client, gin, cards
import logging, random

logger = logging.getLogger('best_bot')
logger.setLevel(logging.INFO)

# draw_choice is one of 'discard', 'deck'
# discard_choice is a Card
# history is [ (draw_choice, discard_choice) ]

def decompose_history(history):
    """ decomposes the history into opponents hand, discard, and remaining deck """
    is_their_turn = (len(history) % 2 != 0)
    deck = cards.all_cards
    their_hand = set()
    discard = []
    for draw_choice, discard_choice in history:
        if draw_choice is 'discard' and is_their_turn:
            their_hand |= {discard.pop()}

        discard.append(discard_choice)
        if is_their_turn:
            their_hand -= {discard_choice}

        is_their_turn = not is_their_turn

    return their_hand, discard, deck

def choose_draw(hand, history):
    assert(type(hand) is set)
    assert(type(history) is list)

    their_hand, discard, deck = decompose_history(history)

    top_discard = discard[-1]

    take_discard_value = gin.points_leftover(hand | {top_discard})
    take_deck_value = sum(gin.points_leftover(hand | {card}) for card in deck) / len(deck)

    if take_deck_value < take_discard_value:
        logger.info('taking card from deck')
        return 'deck'
    logger.info('taking card off discard')
    return 'discard'

def singles(cards):
    """ finds cards not in pairs """
    def doesnt_have_pair(card):
        return all([(card.rank != c.rank and not card.adjacent(c)) for c in cards])
    return filter(doesnt_have_pair, cards)

def choose_discard(hand, history):
    their_hand, discard, deck = decompose_history(history)
    _, deadwood = gin.arrange_hand(hand)
    deaderwood = list(singles(deadwood))
    if len(deaderwood) is 0:
        deaderwood = deadwood
    if len(deaderwood) is 0:
        deaderwood = hand

    card_to_discard = min(deaderwood,
                          key=lambda card: gin.points_leftover(hand - {card}, their_hand))

    logger.info(f'discarding {card_to_discard}')
    return card_to_discard

def should_end(hand, history):
    melds, deadwood = gin.arrange_hand(hand)
    return len(deadwood) is 0

best_bot = client.make_bot(choose_draw, choose_discard, should_end)

if __name__ == '__main__':
    client.play_bot(best_bot)
