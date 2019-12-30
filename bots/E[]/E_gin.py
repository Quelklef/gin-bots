""""""

import sys
sys.path.append('../..')

import statistics as stats
average = stats.mean
import itertools as it

import client
import gin

def calculate_other_hand(history):
  """ From a history, calculate the cards that are definitely in the other player's hand
  Assumes that the current turn is 'our' turn. """

  # whose turn was the first turn
  their_turn = len(history) % 2 != 0

  their_hand = set()

  # discard pile
  discard = []

  # simulate game
  for draw_choice, discard_choice in history:
    if draw_choice == 'discard':
      card = discard.pop()
      if their_turn:
        their_hand.add(card)

    discard.append(discard_choice)
    if their_turn:
      their_hand.discard(discard_choice)

    their_turn = not their_turn

  return their_hand

def calculate_seen(hand, history):
  """ Calculate all the cards that definitely ARENT in the deck """
  played = { discard_choice for draw_choice, discard_choice in history }
  return played + hand

def caluclate_unseen(hand, history):
  return cards.all_cards - calculate_seen(hand, history)

def emulate_their_turn(our_hand, history, *, depth):
  unseen = calculate_unseen(hand, history)

  # known cards in their hand
  known_cards = calculate_other_hand(history)
  # possible other cards in their hand
  possible_other_cards = it.combinations(unseen, 10 - len(known_cards))
  # all possible hands of theirs
  possible_hands = map(known_cards.__add__, possible_other_cards)

  for their_hand in possible_hands:
    yield from emulate_turn(their_hand, history, depth=depth, turn='theirs')

def other_turn(turn):
  if turn == 'ours': return 'theirs'
  if turn == 'theirs': return 'ours'

def emulate_game(our_hand, their_hand, history, *, depth=5, turn='ours'):
  if depth == 0:
    score = gin.score_hand(our_hand, their_hand)
    return score

  hands = { 'ours': our_hand, 'theirs': their_hand }
  hand = hands[turn]

  # draw from discard
  discard = gin.calculate_discard(history)
  draw_choice = discard[-1]
  for discard_choice in hand:
    yield from emulate_game(
      hand | {draw_choice},
      history + [('discard', discard_choice)]
      depth=depth - 1,
      turn=other_turn(turn),
    )

  # draw from deck
  unseen = cards.all_cards - calculate_seen(hand, history)
  for drawn_card in unseen:
    for discard_choice in hand:
      yield from emulate_game(
        hand | {drawn_card},
        history + [('deck', discard_choice)],
        depth=depth - 1,
        turn=other_turn(turn),
      )

# -- #

def choose_draw(hand, history):
  """ choose where to draw a card from """
  unseen = cards.all_cards - calculate_seen(hand, history)
  discard = gin.calculate_discard(history)

  # average score if choose from deck
  deck_score = average(
    score_gamestate(hand | {card})
    for card in unseen
  )

  # score if choose from discard
  discard_score = score_gamestate(hand | {discard[-1]})

  if deck_score > discard_score:
    return 'deck'
  else:
    return 'discard'

def choose_discard(hand, history):
  """ choose which card to discard """

  def resultant_score(discard_choice):
    return score_gamestate(hand - {discard_choice}, history)

  return min(hand, key=resultant_score)

def should_end(hand, history):
  """ choose whether or not to go down """
  assert False

simple_bot = client.make_bot(choose_draw, choose_discard, should_end)

if __name__ == '__main__':
  client.play_bot(simple_bot)

