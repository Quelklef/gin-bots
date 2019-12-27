""" Helper module for gin bots that so choose to be written in Python """

from cards import Card
from gin import can_end

def try_card(arg):
  try:
    return Card(arg)
  except ValueError:
    return arg

def play_bot(choose_draw, should_end, choose_discard):
  with open('comm.txt', 'r') as f:
    lines = f.read()

  hand, stack, history = lines.split('\n')

  hand    = [] if not hand    else { Card(card) for card in hand.split(',') }
  stack   = [] if not stack   else [ Card(card) for card in stack.split(',') ]
  history = [] if not history else [ try_card(s) for s in history.split(',') ]

  result = str(choose_move(choose_draw, should_end, choose_discard, hand, stack, history))

  with open('comm.txt', 'w') as f:
    f.write(result)

def choose_move(choose_draw, should_end, choose_discard, hand, stack, history):
  if len(hand) == 10:
    # If stack is empty, must draw from deck
    if len(stack) == 0:
      return 'deck'
    return choose_draw(hand, stack, history)

  if can_end(hand) and should_end(hand, stack, history):
    return 'end'

  return choose_discard(hand, stack, history)
