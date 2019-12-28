""" This file handles implementing the game of Gin """

import random
import itertools as it

from cards import Card, all_cards
from util import powerset, pairwise, flatten, union


UNDERCUT_BONUS = 20
GIN_BONUS = 20
MAX_POINTS_TO_GO_DOWN = 7

def is_book(cards):
  """ a 3- or 4-of a kind """
  return len(cards) in [3, 4] and len(set(card.rank for card in cards)) == 1

def is_run(cards):
  """ a straight flush with 3 or more cards """
  return len(cards) in [3, 4] and all( prev_card.adjacent(card) for prev_card, card in pairwise(sorted(cards)) )

def is_meld(cards):
  """ a book or a run """
  return is_book(cards) or is_run(cards)

def get_melds(hand):
  melds_3 = filter(is_meld, it.combinations(hand, 3))
  melds_4 = filter(is_meld, it.combinations(hand, 4))
  return map(set, it.chain(melds_4, melds_3))

def conflicting(melds):
  """ two melds contain the same card """
  return sum(map(len, melds)) != len(union(melds, set()))

def sum_cards_value(cards):
  return sum(card.value for card in cards)

def arrange_hand(hand, other_melds={}):
  """ Arrange a hand into (melds, deadwood)
  If `other_melds` is included, allows cards in `hand` to be tacked
  onto those melds when creating melds """
  # https://discardoverflow.com/a/542706/4781072

  all_possible_melds = get_melds(hand)
  meld_sets = powerset(all_possible_melds)
  valid_meld_sets = it.filterfalse(conflicting, meld_sets)

  def can_be_added_to_other_melds(card):
    return any(is_meld(meld | {card}) for meld in other_melds)

  def deadwood(meld_set):
    cards_in_melds = set(flatten(meld_set))
    leftover_cards = hand - cards_in_melds
    deadwood = it.filterfalse(can_be_added_to_other_melds, leftover_cards)
    return deadwood

  def points_leftover(meld_set):
    return sum_cards_value(deadwood(meld_set))

  best_meld_set = min(valid_meld_sets, key=points_leftover)
  return best_meld_set, deadwood(best_meld_set)

def points_leftover(hand):
  melds, deadwood = arrange_hand(hand)
  return sum_cards_value(deadwood)

def can_end(hand):
  return points_leftover(hand) <= MAX_POINTS_TO_GO_DOWN

def calculate_discard(history):
  """ Calculate the current discard pile from a history """
  discard = []

  for draw_choice, discard_choice in history:
    if draw_choice == 'discard':
      discard.pop()
    discard.append(discard_choice)

  return discard

def score_hand(our_hand, their_hand):
  """ Accepts two hands. The first hand is that of the player who ended the game.
  Calculates the number of points that that player scores. """

  # First arrange our hand as best as possible
  our_melds, our_deadwood = arrange_hand(our_hand)

  # Now arrange the their hand, keeping in mind that
  # it can build off of the first hand's books and runs
  their_melds, their_deadwood = arrange_hand(their_hand, our_melds)

  # Calculate number of points in each hand
  our_points = sum_cards_value(our_deadwood)
  their_points = sum_cards_value(their_deadwood)

  # Check if an undercut
  if their_points < our_points:
    # Other player undercuts us
    # Calculate the number of points they will get
    their_score = our_points - their_points + UNDERCUT_BONUS
    # Return as a value relative to us
    return -their_score

  # Not an undercut
  else:
    # Calculate our score
    our_score = their_points - our_points
    # Check if gin or not
    is_gin = our_deadwood == []
    if is_gin: our_score += GIN_BONUS
    return our_score

def play_hand(player1, player2):
  """ Pit two players against each other in a single hand of Gin.
  Return an integer value V where:
    abs(V) is the value of the winning bot
    V > 0 only if bot 1 won
    V < 0 only if bot 2 won

  Agents should be a (stateful) function that accepts
  a GameState and returns their move as a GameMove object.

  Agent 1 plays first. """

  deck = list(all_cards)
  random.shuffle(deck)

  # discard pile
  discard = []

  history = []
  hand1 = { deck.pop() for _ in range(10) }
  hand2 = { deck.pop() for _ in range(10) }

  # Whose turn is it?
  player = player1
  # Reference to player's hand
  hand = hand1
  other_hand = hand2

  def switch_players():
    nonlocal player
    if player == player1:
      player, hand, other_hand = player2, hand2, hand1
    elif player == player2:
      player, hand, other_hand = player1, hand1, hand2

  def message():
    """ send the player the current state and get their response """
    return player({*hand}, [*history])

  while True:

    # We choose to make the deck running out be a tie
    if deck == []:
      return 0

    # Play the turn
    draw_choice = message()

    if draw_choice == 'deck':
      drawn_card = deck.pop()

    elif draw_choice == 'discard':
      if len(discard) == 0:
        raise ValueError("Cannot draw from an empty discard!")
      drawn_card = discard.pop()

    else:
      raise ValueError(f"Expected either 'deck' or 'discard', not {repr(draw_choice)}.")

    hand.add(drawn_card)
    action = message()
    if action == 'end':
      # end the game
      if points_leftover(hand) > MAX_POINTS_TO_GO_DOWN:
        raise ValueError(f"Cannot end on more than {MAX_POINTS_TO_GO_DOWN} points.")

      return score_hand(hand, other_hand)

    # else, discarding a card
    discard_choice = Card(action)
    discard.append(discard_choice)
    hand.remove(discard_choice)

    history.append((draw_choice, discard_choice))

    # Switch players
    switch_players()
