""" graph search """

import sys
sys.path.append('../..')

import statistics as stats
average = stats.mean
import itertools as it
import random

import client
import gin
import cards


def emulate_game(active_hand, latent_hand, discard, *, turn, depth=2, n=5):
  """
  active_hand is hand of person whose turn it is; latent_hand is hand of the person not playing
  return (move, score) where `move` is the best move to make and `score` is its score
  """

  if turn == 'ours':
    our_hand, their_hand = active_hand, latent_hand
  else:
    our_hand, their_hand = latent_hand, active_hand

  if depth == 0:
    # Return heuristic
    return gin.score_hand(our_hand, their_hand)

  # possible moves, each as (discard_location, drawn_card, discard_card, do_end)
  possible_moves = []

  # draw from discard
  if len(discard) > 0:
    draw_choice = discard[-1]
    for discard_choice in active_hand:
      for do_end in [True, False]:
        possible_moves.append( ('discard', draw_choice, discard_choice, do_end) )

  # draw from deck
  deck = cards.all_cards - active_hand - latent_hand - set(discard)
  for draw_choice in deck:
    for discard_choice in active_hand:
      for do_end in [True, False]:
        possible_moves.append( ('deck', draw_choice, discard_choice, do_end) )

  #= recur =#

  def recur(move):
    draw_location, drawn_card, discard_card, do_end = move

    nonlocal discard
    if draw_location == 'discard':
      discard = discard[:-1]
    discard = discard + [discard_card]

    if do_end:
      return gin.score_hand(our_hand, their_hand)
    else:
      # swtich hands since other person is player
      return emulate_game(
        latent_hand,
        active_hand | {drawn_card},
        discard,
        turn = { 'ours': 'theirs', 'theirs': 'ours' }[turn],
        depth=depth - 1,
        n=n,
      )

  sample = random.sample(possible_moves, n)
  results = list(map(recur, sample))

  if turn == 'ours':
    return max(results)
  else:
    return min(results)

def sample_possible_their_hands(hand, derivables, *, n=5):
  """ Generate a sample of the possible states of the other player's hand """

  # definitely in the their person's hand
  known = derivables['other_hand']

  # possibly in the their person's hand
  maybe = cards.all_cards - set(derivables['discard']) - known

  # how many are they missing?
  remaining_count = 10 - len(known)

  def generate_hand():
    # Generate a possible hand of theirs
    remaining_cards = set(random.sample(maybe, remaining_count))
    return known | remaining_cards

  for _ in range(n):
    yield generate_hand()

def do_search(hand, derivables, *, turn):
  their_hand_sample = sample_possible_their_hands(hand, derivables)
  for their_hand in their_hand_sample:
    yield emulate_game(hand, their_hand, derivables['discard'], turn=turn)

def score_gamestate(hand, derivables, *, turn='theirs'):
  return min(do_search(hand, derivables, turn=turn))

# -- #

def choose_draw(hand, history, derivables):
  """ choose where to draw a card from """
  discard = derivables['discard']
  their_hand = derivables['other_hand']

  deck = cards.all_cards - hand - their_hand - set(discard)
  draw_choices = deck | {discard[-1]}

  # TODO: This, and similar lines, look right, but arent.
  #       This is because `score_gamestate` starts the emulation at the
  #       BEGINNING of a turn, but we're in the middle of a turn right
  #       here: we're passing it our draw choice, which means it should
  #       start emulation right after drawing.
  best_choice = max(
    score_gamestate(hand | {draw_choice}, derivables)
    for draw_choice in draw_choices
  )

  if best_choice == discard[-1]:
    return 'discard'
  else:
    return 'deck'

def choose_discard(hand, history, derivables):
  """ choose which card to discard """

  def resultant_score(discard_choice):
    return score_gamestate(hand - {discard_choice}, derivables)

  return min(hand, key=resultant_score)

def should_end(hand, history, derivables):
  """ choose whether or not to go down """
  assert False

simple_bot = client.make_bot(choose_draw, choose_discard, should_end)

if __name__ == '__main__':
  client.play_bot(simple_bot)

