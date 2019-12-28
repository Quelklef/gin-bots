""" A simple gin bot """

import random
import sys
sys.path.append('../..')

import client
import gin

def calculate_other_hand(history):
  """ From a history, calculate the cards that are definitely in the other player's hand
  Assumes that the current turn is 'our' turn. """

  # whose turn was the first turn
  their_turn = len(history) % 2 == 0

  their_hand = set()

  # discard pile
  discard = []

  # emulate game
  for draw_choice, discard_choice in history:
    if draw_choice == 'discard':
      card = discard.pop()
      if their_turn:
        their_hand.add(card)

    if their_turn:
      their_hand.discard(discard_choice)

    discard.append(discard_choice)
    their_turn = not their_turn

  return their_hand

# -- #

def choose_draw(hand, history):
  """ choose where to draw a card from """

  discard = gin.calculate_discard(history)
  their_hand = calculate_other_hand(history)

  current_score = gin.score_hand(hand, their_hand)
  theoretical_score = gin.score_hand(hand | {discard[-1]}, their_hand)

  if theoretical_score > current_score:
    return 'discard'

  return 'deck'

def should_end(hand, history):
  """ choose whether or not to go down """
  return True

def choose_discard(hand, history):
  """ choose which card to discard """

  their_hand = calculate_other_hand(history)

  def resultant_score(discard_choice):
    return gin.score_hand(hand - {discard_choice}, their_hand)

  return max(hand, key=resultant_score)

if __name__ == '__main__':
  client.play_bot(choose_draw, should_end, choose_discard)

