import itertools

# https://docs.python.org/3.6/library/itertools.html#itertools-recipes
def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return itertools.chain.from_iterable(
        itertools.combinations(s, r) for r in range(len(s)+1))
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)
def flatten(listOfLists):
    "Flatten one level of nesting"
    return itertools.chain.from_iterable(listOfLists)

def is_book(cards):
    for card in cards:
        if card.value != cards[0].value:
            return False
    return True

def is_run(cards):
    for prev_card, card in pairwise(sorted(cards)):
        if card.suit != prev_card.suit or card.value - prev_card.value != 1:
            return False
    return True

def is_meld(cards):
    assert(len(cards) in [3, 4])
    return is_book(cards) or is_run(cards)

def get_melds(hand):
    melds_3 = filter(is_meld, itertools.combinations(hand, 3))
    melds_4 = filter(is_meld, itertools.combinations(hand, 4))
    return itertools.chain(melds_4, melds_3)

def conflicting(melds):
    for meld1, meld2 in itertools.combinations(melds, 2):
        if len(meld1 + meld2) != len(set(meld1 + meld2)):
            return True
    return False

def sum_cards_value(cards):
    return sum([card.value for card in cards])

# sum of value of deadwood cards
# https://stackoverflow.com/a/542706/4781072
def value(hand):
    all_possible_melds = get_melds(hand)
    meld_sets = powerset(all_possible_melds)
    valid_meld_sets = itertools.filterfalse(conflicting, meld_sets)
    def deadwood(meld_set):
        cards_in_melds = set(flatten(meld_set))
        return [card for card in hand if card not in cards_in_melds]
    deadwood_sets = map(deadwood, valid_meld_sets)
    return min(map(sum_cards_value, deadwood_sets))

if __name__ == '__main__':
    assert(value(cards.test_hand) is 19)
