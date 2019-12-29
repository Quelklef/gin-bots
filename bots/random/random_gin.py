""" A gin bot that plays randomly """

import random
import sys
sys.path.append('../..')

import client

def choose_draw(hand, history):
  """ choose where to draw a card from """
  return random.choice(['deck', 'discard'])

def choose_discard(hand, history):
  """ choose which card to discard """
  return random.choice([*hand])

def should_end(hand, history):
  """ choose whether or not to go down """
  return random.random() < 0.3

if __name__ == '__main__':
  client.play_bot(choose_draw, choose_discard, should_end)
