""" A human player """

import argparse

import sys
sys.path.append('../..')

import prettify
from cards import Card, parse_card_is_ok
from util import input_until
import client

def prettify_state_table(*args, **kwargs):
  return prettify.prettify_state_table(*args, **kwargs, player_1_char='T', player_2_char='Y')

prettify_state = prettify_state_table

def print_state(hand, history, derivables, *, drawn_card=None):

  discard = derivables['discard']
  other_hand = derivables['other_hand']
  pretty = prettify_state(other_hand, hand, history, discard, drawn_card_2=drawn_card)

  print(pretty)

hand_before_draw = None

def choose_draw(hand, history, derivables):
  print_state(hand, history, derivables)

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

  print_state(hand, history, derivables, drawn_card=drawn_card)

  discard_choice = Card(input_until(
    "Card to discard: ",
    lambda card: parse_card_is_ok(card) and Card(card) in hand,
    error="Either bad format or card not in hand.",
  ))

  return discard_choice

def should_end(hand, history, derivables):
  print_state(hand, history, derivables)

  return 'y' == input_until(
    "End the game here? ['y'/'n']: ",
    lambda s: s in ['y', 'n'],
  )

human_bot = client.make_bot(choose_draw, choose_discard, should_end)

parser = argparse.ArgumentParser(description='Have a human play as a bot')
parser.add_argument(
  '-s', '--style', type=str, default='tabletop',
  help='Choose the style, either "tabletop" or "grid"'
)

if __name__ == '__main__':

  args = parser.parse_args()
  prettify_state = {
    'tabletop': prettify.prettify_state,
    'grid': prettify_state_table,
  }[args.style]

  client.play_bot(human_bot)

