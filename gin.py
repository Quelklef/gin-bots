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
  return len(cards) in [3, 4] and all(prev_card.adjacent(card) for prev_card, card in pairwise(sorted(cards)))

def is_meld(cards):
  """ a book or a run """
  return is_book(cards) or is_run(cards)

def get_melds(hand):
  melds_3 = filter(is_meld, map(frozenset, it.combinations(hand, 3)))
  melds_4 = filter(is_meld, map(frozenset, it.combinations(hand, 4)))
  return frozenset({*melds_3, *melds_4})

def conflicting(melds):
  """ two melds contain the same card """
  return sum(map(len, melds)) != len(union(melds, set()))

def sum_cards_value(cards):
  return sum(card.value for card in cards)

def arrange_hand(hand):
  """ Arrange a hand into (melds, deadwood)
  If `other_melds` is included, allows cards in `hand` to be tacked
  onto those melds when creating melds """
  # adapted from https://discardoverflow.com/a/542706/4781072

  all_possible_melds = get_melds(hand)
  meld_sets = powerset(all_possible_melds)
  valid_meld_sets = it.filterfalse(conflicting, meld_sets)

  def deadwood(meld_set):
    meld_cards = frozenset(flatten(meld_set))
    deadwood = frozenset(hand - meld_cards)
    return deadwood

  def points_leftover(meld_set):
    return sum_cards_value(deadwood(meld_set))

  best_meld_set = min(valid_meld_sets, key=points_leftover)
  return best_meld_set, deadwood(best_meld_set)

def points_leftover(our_hand, their_hand=None):
  """ How many deadwood points does this hand have?
  If a second hand is provided, deadwood in this hand will be played on the other hand's melds. """
  if their_hand: their_melds, their_deadwood = arrange_hand(their_hand)
  our_melds, our_deadwood = arrange_hand(our_hand)
  if their_hand: our_deadwood = frozenset(it.filterfalse(extends_any_meld(their_melds), our_deadwood))
  return sum_cards_value(our_deadwood)

def extends_any_meld(melds):
  """ returns a predicate of a card that decides whether that card can
  extend any of these given melds """
  return lambda card: any(is_meld(meld | {card}) for meld in melds)

def can_end(hand):
  """ is the player able to end the game, given the current hand? """
  return points_leftover(hand) <= MAX_POINTS_TO_GO_DOWN

def calculate_discard(history):
  """ calculate the current discard pile from a history """
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

  # Now arrange the their hand
  their_melds, their_deadwood = arrange_hand(their_hand)

  # Play our deadwood on their melds and vice-versa
  our_deadwood = frozenset(it.filterfalse(extends_any_meld(their_melds), our_deadwood))
  their_deadwood = frozenset(it.filterfalse(extends_any_meld(our_melds), their_deadwood))

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

  current_player = player1

  while True:
    result = do_turn(deck, discard, history, player1, hand1, player2, hand2, current_player)

    if result is not None:
      end_score = result
      return end_score

    # switch players
    current_player = {
      player1: player2,
      player2: player1,
    }[current_player]

def do_turn(deck, discard, history, player1, hand1, player2, hand2, current_player):
  """ do a turn, returning the score or None if the game isn't done """
  # We choose to make the deck running out be a tie
  if len(deck) == 0:
    return 0

  current_player_hand = hand1 if current_player == player1 else hand2
  player_ending = player_turn(deck, discard, history, current_player, current_player_hand)

  if player_ending:
    return score_hand(hand1, hand2)

def player_turn(deck, discard, history, player, hand):
  """ have the player take a turn; return whether or not the player ends the game """

  draw_choice                   = player_draw   (deck, discard, history, player, hand)
  discard_choice, player_ending = player_discard(deck, discard, history, player, hand)

  history.append((draw_choice, discard_choice))

  return player_ending

def player_draw(deck, discard, history, player, hand):
  """ have the player draw a card """
  draw_choice = player({*hand}, [*history])

  if draw_choice == 'deck':
    drawn_card = deck.pop()

  elif draw_choice == 'discard':
    if len(discard) == 0:
      raise ValueError("Cannot draw from an empty discard!")
    drawn_card = discard.pop()

  else:
    raise ValueError(f"Expected either 'deck' or 'discard', not {repr(draw_choice)}.")

  hand.add(drawn_card)

def player_discard(deck, discard, history, player, hand):
  """ have the player discard a card and optionally end the game """
  discard_choice, do_end = player({*hand}, [*history])
  discard_choice = Card(discard_choice)

  if discard_choice not in hand:
    raise ValueError(f"Cannot discard {discard_choice} since it's not in your hand.")

  discard.append(discard_choice)
  hand.remove(discard_choice)

  if do_end:  # end the game
    if points_leftover(hand) > MAX_POINTS_TO_GO_DOWN:
      raise ValueError(f"Cannot end on more than {MAX_POINTS_TO_GO_DOWN} points.")

  return discard_choice, do_end
