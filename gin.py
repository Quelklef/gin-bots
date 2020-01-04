""" This file handles implementing the game of Gin """

import random
import itertools as it

from cards import Card, all_cards
from util import powerset, pairwise, flatten, union


UNDERCUT_BONUS = 10
GIN_BONUS = 20
MAX_POINTS_TO_GO_DOWN = 7

def kinds_match(cards):
  return len(set(card.rank for card in cards)) == 1

def in_a_row(cards):
  return all(prev_card.adjacent(card) for prev_card, card in pairwise(sorted(cards)))

def meldlike(cards):
  """ any number of cards that have the same rank or are all next to each other
  (and of same suit) """
  return len(cards) > 1 and (kinds_match(cards) or in_a_row(cards))

def is_pair(cards):
  """ two cards that have same rank or are next to each other """
  card1, card2 = cards
  return len(cards) is 2 and meldlike(cards)

def is_meld(cards):
  """ a book or a run """
  return len(cards) in [3, 4] and meldlike(cards)

def get_pairs(cards):
  return filter(is_pair, map(frozenset, it.combinations(cards, 2)))

def get_melds(cards):
  melds_3 = filter(is_meld, map(frozenset, it.combinations(cards, 3)))
  melds_4 = filter(is_meld, map(frozenset, it.combinations(cards, 4)))
  return frozenset({*melds_3, *melds_4})

def conflicting(melds):
  """ two melds contain the same card """
  return sum(map(len, melds)) != len(union(melds, set()))

def sum_cards_value(cards):
  return sum(card.value for card in cards)

def arrange_hand(hand):
  """ Arrange a hand into (melds, deadwood)"""
  # adapted from https://discardoverflow.com/a/542706/4781072
  all_possible_melds = get_melds(hand)
  meld_sets = powerset(all_possible_melds)
  valid_meld_sets = it.filterfalse(conflicting, meld_sets)

  def deadwood(meld_set):
    meld_cards = frozenset(flatten(meld_set))
    return frozenset(hand - meld_cards)

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

def extends_any_pair(pairs):
  """ returns a predicate of a card that decides whether that card can
  extend any of these given pairs """
  #TODO unify with above
  return lambda card: any(is_pair(pair | {card}) for pair in pairs)

def can_end(hand):
  """ is the player able to end the game, given the current hand? """
  return points_leftover(hand) <= MAX_POINTS_TO_GO_DOWN

def score_hand(our_hand, their_hand):
  """ Accepts two hands. The first hand is that of the player who ended the game.
  Calculates the number of points that that player scores. """

  # First arrange our hand as best as possible
  our_melds, our_deadwood = arrange_hand(our_hand)
  is_gin = len(our_deadwood) == 0

  # Now arrange the their hand
  their_melds, their_deadwood = arrange_hand(their_hand)

  # As long as we didn't Gin,
  # They can play their deadwood on our melds
  if not is_gin:
    their_deadwood = frozenset(it.filterfalse(extends_any_meld(our_melds), their_deadwood))

  # Calculate number of points in each hand
  our_points = sum_cards_value(our_deadwood)
  their_points = sum_cards_value(their_deadwood)

  # Check if an undercut
  if their_points <= our_points:
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
    if is_gin: our_score += GIN_BONUS
    return our_score

def play_hand(player1, player2, *, state_callback=lambda x: None):
  """
  Pit two players against each other in a single hand of Gin.
  Return an integer value V where:
    abs(V) is the value of the winning bot
    V > 0 only if bot 1 won
    V < 0 only if bot 2 won

  If state_callback is given, it will be called with the game
  state (hand1, hand2, history, discard) before the game and then
  after every turn. History /will/ contain the turn just taken.

  Player 1 plays first.

  The players must be objects which will participate in
  two-way communication with this function. This function will
  send each player data at the appropriate times, and the players
  are sometimes expected to return a response (and sometimes not).
  This function will send the players data via the .send() method
  and will ask for responses via a .recv() method.

  The communication looks like the following:

    1. The player is sent a tuple (hand, starting) where
       the `hand` value is the player's starting hand, as a
       set of Card objects, and `starting` is a boolean
       denoting whether the player is the first to play or not.

  Now the turns begin. Each turn looks like the following:

    1. The player is sent the turn that their opponent took,
       as a tuple

         (draw_location, discard_choice, do_end)

       where:

         draw_location: is either 'deck' or 'discard' depending on where
         they drew from

         discard_choice: is the card they discarded, as a Card object

         do_end: is True if they ended the game and False otherwise

    2. The player is expected to send  where they would like
       to draw from, either 'deck' or 'discard'.

    3. The player is send the card they drew.

    4. The player is expected to send a tuple (discard_choice, do_end)
       where discard_choice is the card they would like to discard
       and do_end notes if they would like to end the game.

    5. If the game has not ended, this repeats for the next turn.

  The starting turn begins at step 2 instead of step 1.
  """

  deck = list(all_cards)
  random.shuffle(deck)

  # discard pile
  discard = []

  history = []
  hand1 = { deck.pop() for _ in range(10) }
  hand2 = { deck.pop() for _ in range(10) }

  # Send players their starting hand and starting turn info
  player1.send('starting', hand1, True)
  player2.send('starting', hand2, False)

  state_callback(hand1, hand2, history, discard)

  active_player = player1
  active_hand = hand1
  latent_hand = hand2

  def swap_players():
    nonlocal active_player, active_hand, latent_hand

    if active_player == player1:
      active_player = player2
      active_hand = hand2
      latent_hand = hand1

    elif active_player == player2:
      active_player = player1
      active_hand = hand1
      latent_hand = hand2

  while True:

    # Send the player the other player's turn
    if len(history) > 0:
      previous_turn = history[-1]
      active_player.send('opponent_turn', previous_turn)

      # If the other player's turn ended the game, end it now
      # We do this after sending the turn to the active player so that
      # the client is able to recognize that the game is over and terminate
      draw_location, discard_choice, do_end = previous_turn

      if do_end:
        end_score = score_hand(latent_hand, active_hand)
        return end_score

      # Do reshuffle if needed
      # Reshuffle keeps the top card of the discard
      if len(deck) == 0:
        discard_top = discard.pop()
        deck = discard
        discard = [discard_top]
        random.shuffle(deck)

    # Get where the player wants to draw from
    draw_location = active_player.recv()

    if draw_location not in ['deck', 'discard']:
      raise ValueError(f"Draw location must be 'deck' or 'discard', not {repr(draw_location)}.")

    if draw_location == 'deck':
      drawn_card = deck.pop()
    if draw_location == 'discard':
      if len(discard) == 0:
        raise ValueError("Cannot draw from an empty discard pile.")
      drawn_card = discard.pop()

    active_hand.add(drawn_card)

    discard_choice, do_end = active_player.send_and_recv('drawn', drawn_card)

    if discard_choice not in active_hand:
      raise ValueError(f"Cannot discard {discard_choice} since it's not in your hand.")

    active_hand.remove(discard_choice)
    discard.append(discard_choice)

    turn = (draw_location, discard_choice, do_end)
    history.append(turn)

    state_callback(hand1, hand2, history, discard)
    swap_players()

