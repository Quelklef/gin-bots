""" This file handles implementing the game of Gin """

import random
from cards import Card, all_cards

frz = frozenset

UNDERCUT_BONUS = 20
GIN_BONUS = 20


def score_hand(our_hand, their_hand):
  """ Accepts two hands. The first hand is that of the player who ended the game.
  Calculates the number of points that that player scores. """

  # First arrange our hand as best as possible
  (our_sets, our_runs, our_leftovers) = _arrange_hand(our_hand)

  # Now arrange the their hand, keeping in mind that
  # it can build off of the first hand's sets and runs
  (their_sets, their_runs, their_leftovers) = _arrange_hand(their_hand, our_sets, our_runs)

  # Calculate number of points in each hand
  our_points = sum(card.value for card in our_leftovers)
  their_points = sum(card.value for card in their_leftovers)

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
    is_gin = our_leftovers == []
    if is_gin: our_score += GIN_BONUS
    return our_score


def _arrange_hand(hand, other_sets=frz(), other_runs=frz()):
  """ Return (sets, runs, leftovers), minimizing leftover points.
  Accepts optional values `other_sets` and `other_runs` which are
  a list of sets and runs that the hand can build on. This is for
  use when a player goes down for some number of points, since the
  other player can build off of his sets and runs. """
  best_arrangement = None
  least_points = float('inf')

  for arrangement in _arrange_hand_all(hand):
    sets, runs, leftover = arrangement
    points = sum(card.value for card in leftover)
    if points < least_points:
      best_arrangement = arragement
      least_points = points

  return best_arrangement


def _arrange_hand_all(hand, sets=frz(), runs=frz(), other_sets=frz(), other_runs=frz()):
  """ Yield every possible way to organize this hand into sets and runs.
  The values `other_sets` and `other_runs` represent sets and runs that can
  be built on from the other player's hand.
  Values are yielded in the form (sets, runs, leftovers).
  If cards are tacked onto `other_sets` or `other_runs`, they do not
  appear in the yielded value. """

  for card in hand:

    # As we do the rest of the algorithm, also
    # compute whether or not this card is a leftover, i.e.
    # belongs to no runs or sets
    card_is_leftover = True

    # Try this card in all possible sets
    for set in _make_sets(card, hand):
      yield from _arrange_hand_all(
        hand - set,
        sets | frz({set}),
        runs,
        other_sets,
        other_runs,
      )

      card_is_leftover = False

    # Try tacking this card onto a set from the other hand
    for other_set in other_sets:
      if _can_tack_onto_set(card, other_set):
        yield from _arrange_hand_all(
          hand - frz({card}),
          sets,
          runs,
          other_sets - frz({other_set}),
          other_runs
        )

        card_is_leftover = False

    # Try this card in all poossible runs
    for run in _make_runs(card, hand):
      yield from _arrange_hand_all(
        hand - run,
        sets,
        runs | frz({run}),
        other_sets,
        other_runs
      )

      card_is_leftover = False

    # Try tacking this card onto a set from the other hand
    for other_run in other_runs:
      if _can_tack_onto_run(card, other_run):
        yield from _arrange_hand_all(
          hand - frz({card}),
          sets,
          runs,
          other_sets,
          other_runs - frz({other_run}),
        )

        card_is_leftover = False

    if card_is_leftover:
      # Use this card as a leftover
      yield from _arrange_hand_all(
        hand - frz({card}),
        sets,
        runs,
        other_sets,
        other_runs
      )


def _make_sets(card, cards):
  """ Yield all possible sets containing the given card that can be made
  with the given card and the other cards """

  cards_with_same_rank = frz(filter(lambda c: c.rank == card.rank, cards))

  if len(cards_with_same_rank) < 2:
    return

  if len(cards_with_same_rank) == 2:
    yield card + cards_with_same_rank
    return

  if len(cards_with_same_rank) == 3:
    # Either do all 4
    yield frz({card}) | cards_with_same_rank
    # Or exclude one
    for removed_card in cards_with_same_rank:
      yield frz({card}) | (cards_with_same_rank - {removed_card})
    return


def _make_runs(card, cards):
  """ Return all possible runs containing the given card that can be made
  with the given card and the other cards """

  # First collect all the cards which form a contiguous range around the given card
  contiguous = {card}
  while True:
    for card in cards:
      # Add the card to candidates if it's not already there and it's
      # adjacent to one of the cards
      if card not in contiguous and any(map(lambda c: card.adjacent(c), contiguous)):
        contiguous.add(card)

    else:
      # No more extensions can be done
      break

  # Turn from set into sorted list
  contiguous = sorted(contiguous)
  print(contiguous)

  # Now yield every possible run
  for run_len in range(3, len(contiguous) + 1):
    for run_start in range(0, len(contiguous) - run_len):
      print(run_len, run_start, contiguous[run-start : run_start + run_len])
      yield set(contiguous[run_start : run_start + run_len])


def _can_tack_onto_set(card, set):
  return card.rank == set[0].rank


def _can_tack_onto_run(card, run):
  sorted_run = sorted(run)
  return adjacent(card, sorted_run[0]) or adjacent(card, sorted_run[-1])


def play_hand(agent1, agent2):
  """ Pit two agents against each other in a single hand of Gin.
  Return an integer value V where:
    abs(V) is the value of the winning bot
    V > 0 only if bot 1 won
    V < 0 only if bot 2 won

  Agents should be a (stateful) function that accepts
  a GameState and returns their move as a GameMove object.

  Agent 1 plays first. """

  deck = list(all_cards)
  random.shuffle(deck)

  # discard stack
  stack = []

  history = []
  hand1 = [ deck.pop() for _ in range(10) ]
  hand2 = [ deck.pop() for _ in range(10) ]

  # Whose turn is it?
  player = agent1
  # Reference to player's hand
  hand = hand1
  other_hand = hand2

  def switch():
    if player == agent1:
      player, hand, other_hand = agent2, hand2, hand1
    elif player == agent2:
      player, hand, other_hand = agent1, hand1, hand2

  while True:

    # We choose to make the deck running out be a tie
    if deck == []:
      return 0

    # Play the turn
    draw_choice = player(hand[::], history[::])
    history.append(draw_choice)

    if draw_choice == 'deck':
      drawn_card = deck.pop()
    elif draw_choice == 'stack':
      drawn_card = stack.pop()

    hand.append(drawn_card)
    action = player(hand[::], history[::])
    if action == 'end':
      # end the game
      return score_hands(hand, other_hand)
    else:
      # discarding a card
      discard_choice = action
      stack.append(discard_choice)
      history.append(discard_choice)

    # Switch players
    switch_players()

