from hypothesis import assume, given, errors, strategies as st
from cards import Card, all_cards
from itertools import filterfalse
import gin
import unittest

Card = st.sampled_from(list(all_cards))
Triple = st.frozensets(Card, min_size=3, max_size=3)
Quadruple = st.frozensets(Card, min_size=4, max_size=4)

@st.composite
def meld(draw, quad=False, cards=all_cards):
  num_cards = 3 if not quad else 4
  proposed_meld = {draw(st.sampled_from(list(cards)))}

  try:
    for i in range(num_cards - 1):
      candidates = list(filter(lambda c:
                               (c not in proposed_meld)
                               and gin.meldlike(proposed_meld | {c}),
                               cards))
      proposed_meld |= {draw(st.sampled_from(candidates))}
  except errors.InvalidArgument:
    # try again
    return draw(meld(quad=quad, cards=cards))
  return frozenset(proposed_meld)

@st.composite
def gin_hand(draw, cards=frozenset(all_cards)):
  meld1 = draw(meld(quad=True, cards=cards))
  cards -= meld1
  meld2 = draw(meld(cards=cards))
  cards -= meld2
  meld3 = draw(meld(cards=cards))
  return frozenset({*meld1, *meld2, *meld3})

@st.composite
def go_down_hand(draw, cards=frozenset(all_cards)):
  # TODO unify with `gin_hand`
  meld1 = draw(meld(cards=cards))
  cards -= meld1
  meld2 = draw(meld(cards=cards))
  cards -= meld2
  meld3 = draw(meld(cards=cards))
  cards -= meld3

  free_points = gin.MAX_POINTS_TO_GO_DOWN
  cards = filter(lambda c: c.value <= free_points, cards)
  cards = filterfalse(gin.extends_any_meld({meld1, meld2, meld3}), cards)
  remaining_card = draw(st.sampled_from(list(cards)))

  return frozenset({*meld1, *meld2, *meld3, remaining_card})

Hand = st.frozensets(Card, min_size=10, max_size=10)

class TestGameMethods(unittest.TestCase):
  @given(gin_hand(), Hand)
  def test_score_gin_hand(self, our_hand, their_hand):
    _, their_deadwood = gin.arrange_hand(their_hand)
    expected_score = gin.GIN_BONUS + gin.sum_cards_value(their_deadwood)
    self.assertEqual(expected_score, gin.score_hand(our_hand, their_hand))

  @given(go_down_hand(), Hand)
  def test_score_go_down_hand(self, our_hand, their_hand):
    our_melds, our_deadwood = gin.arrange_hand(our_hand)
    our_points = gin.sum_cards_value(our_deadwood)
    _, their_deadwood = gin.arrange_hand(their_hand)
    assume(len(their_deadwood) > 0)
    their_unmatched_deadwood = frozenset(filterfalse(gin.extends_any_meld(our_melds), their_deadwood))
    their_points = gin.sum_cards_value(their_unmatched_deadwood)
    assume(their_points > our_points)
    if their_points > our_points:
      expected_score = their_points - our_points
      self.assertEqual(expected_score, gin.score_hand(our_hand, their_hand))
    else:
      expected_score = -10 - (our_points - their_points)
      self.assertEqual(expected_score, gin.score_hand(our_hand, their_hand))

if __name__ == '__main__':
  unittest.main()
