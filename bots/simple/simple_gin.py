""" A simple gin bot """

import random
import sys
sys.path.append('../..')

import functools as ft

import gin
import client

def choose_draw(hand, history):
  """ choose where to draw a card from """

  discard = client.calculate_discard(history)
  their_hand = client.calculate_other_hand(history)

  current_points = gin.points_leftover(hand, their_hand)
  theoretical_points = gin.points_leftover(hand | {discard[-1]}, their_hand)

  if theoretical_points < current_points:
    return 'discard'

  return 'deck'

def choose_discard(hand, history):
  """ choose which card to discard """

  their_hand = client.calculate_other_hand(history)

  def resultant_score(discard_choice):
    return gin.points_leftover(hand - {discard_choice}, their_hand)

  melds, deadwood = gin.arrange_hand(hand)

  return min(hand, key=resultant_score)

def should_end(hand, history):
  """ choose whether or not to go down """
  return True

simple_bot = client.make_bot(choose_draw, choose_discard, should_end)

if __name__ == '__main__':
  client.play_bot(simple_bot)

