""" A human player """

import sys
sys.path.append('../..')

from prettify import prettify_state_table
from cards import Card, parse_card_is_ok
from util import input_until
import client

hand_before_draw = None

def choose_draw(hand, history, derivables):
  print(prettify_state_table(hand, history, derivables))

  global hand_before_draw
  hand_before_draw = {*hand}

  return input_until(
    "Draw from deck or discard? ['deck'/'discard']: ",
    lambda s: s in ['deck', 'discard'],
  )

def choose_discard(hand, history, derivables):
  if hand_before_draw:
    drawn_card = next(iter(hand - hand_before_draw))
  else:
    drawn_card = None

  print(prettify_state_table(hand, history, derivables, drawn_card=drawn_card))

  discard_choice = Card(input_until(
    "Card to discard: ",
    lambda card: parse_card_is_ok(card) and Card(card) in hand,
    error="Either bad format or card not in hand.",
  ))

  return discard_choice

def should_end(hand, history, derivables):
  print(prettify_state_table(hand, history, derivables))

  return 'y' == input_until(
    "End the game here? ['y'/'n']: ",
    lambda s: s in ['y', 'n'],
  )

human_bot = client.make_bot(choose_draw, choose_discard, should_end)

if __name__ == '__main__':
  client.play_bot(human_bot)

