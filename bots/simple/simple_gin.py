""" A simple gin bot """

import random
import sys
sys.path.append('../..')

import gin
import client

def choose_draw(hand, history, derivables):
  """ choose where to draw a card from """

  discard = derivables['discard']
  their_hand = derivables['other_hand']

  current_points = gin.points_leftover(hand, their_hand)
  theoretical_points = gin.points_leftover(hand | {discard[-1]}, their_hand)

  if theoretical_points < current_points:
    return 'discard'
  else:
    return 'deck'

def choose_discard(hand, history, derivables):
  """ choose which card to discard """

  their_hand = derivables['other_hand']

  def score_from_removing(discard_choice):
    return gin.points_leftover(hand - {discard_choice}, their_hand)

  return min(hand, key=score_from_removing)

def should_end(hand, history, derivables):
  """ choose whether or not to go down """

  return True

simple_bot = client.make_bot(choose_draw, choose_discard, should_end)

if __name__ == '__main__':
  client.play_bot(simple_bot)

