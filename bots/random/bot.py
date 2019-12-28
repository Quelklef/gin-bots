""" A gin bot that plays randomly """

import random
import sys
sys.path.append('../..')

from cards import Card
from client import play_bot

def choose_draw(hand, history):
  """ choose where to draw a card from """
  return random.choice(['deck', 'discard'])

def should_end(hand, history):
  """ choose whether or not to go down """
  return random.random() < 0.3

def choose_discard(hand, history):
  """ choose which card to discard """
  return random.choice([*hand])

if __name__ == '__main__':
  play_bot(choose_draw, should_end, choose_discard)
