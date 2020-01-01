""" A gin bot that plays randomly """

import random
import sys
sys.path.append('../..')

import client

def choose_draw(hand, history, derivables):
  """ choose where to draw a card from """
  return random.choice(['deck', 'discard'])

def choose_discard(hand, history, derivables):
  """ choose which card to discard """
  return random.choice([*hand])

def should_end(hand, history, derivables):
  """ choose whether or not to go down """
  return random.random() < 0.3

random_bot = client.make_bot(choose_draw, choose_discard, should_end)

if __name__ == '__main__':
  client.play_bot(random_bot)
