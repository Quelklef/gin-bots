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

def negate(x):
  return -x

def emulate_game(active_hand, latent_hand, history, *, depth=0):
  """ active_hand is hand of person whose turn it is; latent_hand is hand of the person not playing """

  if depth == 0:
    score = gin.score_hand(active_hand, latent_hand)
    yield score
    return

  # possible moves, each as (discard_location, drawn_card, discard_card)
  possible_moves = []

  # draw from discard
  discard = client.calculate_discard(history)
  if len(discard) > 0:
    draw_choice = discard[-1]
    for discard_choice in active_hand:
      possible_moves.append( ('discard', draw_choice, discard_choice) )

  # draw from deck
  unseen = cards.all_cards - client.calculate_seen(active_hand, history)
  for draw_choice in unseen:
    for discard_choice in active_hand:
      possible_moves.append( ('deck', draw_choice, discard_choice) )

  #= recur =#

  for discard_location, drawn_card, discard_card in possible_moves:
    # swtich hands since other person is player
    results = emulate_game(
      latent_hand,
      active_hand | {drawn_card},
      history + [(discard_location, discard_card)],
      depth=depth - 1,
    )

    # negate since the return values are the scores relative to the opponent
    yield from map(negate, results)

def sample_possible_their_hands(hand, history, *, n=75):
  """ Generate a sample of the possible states of the other player's hand """

  # definitely in the their person's hand
  known = client.calculate_other_hand(history)

  # possibly in the their person's hand
  unseen = client.calculate_unseen(hand, history)

  # how many are they missing?
  remaining_count = 10 - len(known)

  def generate_hand():
    # generate the rest of the hand
    remaining_cards = set(random.sample(unseen, remaining_count))
    return known | remaining_cards

  for _ in range(n):
    yield generate_hand()

def do_search(hand, history):
  their_hand_sample = sample_possible_their_hands(hand, history)
  for their_hand in their_hand_sample:
    yield from emulate_game(hand, their_hand, history)

def score_gamestate(hand, history):
  score_sample = do_search(hand, history)
  return average(score_sample)

# -- #

def choose_draw(hand, history):
  """ choose where to draw a card from """
  unseen = cards.all_cards - client.calculate_seen(hand, history)
  discard = client.calculate_discard(history)

  # average score if choose from deck
  deck_score = average(
    score_gamestate(hand | {card}, history)
    for card in unseen
  )

  # score if choose from discard
  discard_score = score_gamestate(hand | {discard[-1]}, history)

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

