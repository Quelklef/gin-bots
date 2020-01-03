import sys
sys.path.append('../..')
import client, gin, cards
import logging, random
from util import flatten

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler('bot.log')
logger.addHandler(handler)

# draw_choice is one of 'discard', 'deck'
# discard_choice is a Card
# history is [ (draw_choice, discard_choice, do_end), ... ]
# derivables is { 'disard': discard, 'other_hand': other_hand }

def decompose_history(history):
    """ decomposes the history into opponents hand, discard, and remaining deck """
    is_their_turn = (len(history) % 2 != 0)
    deck = cards.all_cards
    their_hand = set()
    discard = []
    for draw_choice, discard_choice, do_end in history:
        if draw_choice is 'discard' and is_their_turn:
            their_hand |= {discard.pop()}

        discard.append(discard_choice)
        if is_their_turn:
            their_hand -= {discard_choice}

        is_their_turn = not is_their_turn

    return their_hand, discard, deck

def choose_draw(hand, history, derivables):
    assert(type(hand) is set)
    assert(type(history) is list)
    assert(type(derivables) is dict)

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
        return all([(card.rank != c.rank and not card.adjacent(c))
                    for c
                    in cards
                    if c is not card])
    return filter(doesnt_have_pair, cards)

IS_IN_MELD_PENALTY           = 300
IS_IN_PAIR_PENALTY           = 80
GIVES_THEM_FOUR_MELD_PENALTY = 150
GIVES_THEM_MELD_PENALTY      = 100
GIVES_THEM_PAIR_PENALTY      = 30

def choose_discard(hand, history, derivables):
    their_hand, discard, deck = decompose_history(history)
    melds, deadwood = gin.arrange_hand(hand)

    meld_cards = list(flatten(melds))
    is_in_meld = lambda card: card in meld_cards

    pair_cards = list(flatten(gin.get_pairs(deadwood)))
    is_in_pair = lambda card: card in pair_cards

    their_melds, their_deadwood = gin.arrange_hand(their_hand)
    gives_them_four_meld = gin.extends_any_meld(their_melds)

    their_pairs = gin.get_pairs(their_deadwood)
    gives_them_meld = gin.extends_any_pair(their_pairs)

    gives_them_pair = lambda card: any(gin.is_pair(card, c) for c in their_deadwood)

    def score_discard_choice(card):
        score = 0
        score += IS_IN_MELD_PENALTY if is_in_meld(card) else 0
        score += IS_IN_PAIR_PENALTY if is_in_pair(card) else 0
        score += GIVES_THEM_FOUR_MELD_PENALTY if gives_them_four_meld(card) else 0
        score += GIVES_THEM_MELD_PENALTY if gives_them_meld(card) else 0
        score += GIVES_THEM_PAIR_PENALTY if gives_them_pair(card) else 0
        score += (15 - card.value)
        return score

    #discard_candidates = min(hand, key=score_discard_choice)

    #card_to_discard = min(discard_candidates,
    #                      key=lambda card: gin.points_leftover(hand - {card}, their_hand))

    logger.info(sorted((score_discard_choice(card), card) for card in hand))
    card_to_discard = min(hand, key=score_discard_choice)
    logger.info(f'discarding {card_to_discard}')
    return card_to_discard

def should_end(hand, history, derivables):
    #melds, deadwood = gin.arrange_hand(hand)
    #return len(deadwood) is 0
    return True

best_bot = client.make_bot(choose_draw, choose_discard, should_end)

if __name__ == '__main__':
    client.play_bot(best_bot)
