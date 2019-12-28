""" Helper module for gin bots that so choose to be written in Python """

from cards import Card
import gin

def play_bot(choose_draw, should_end, choose_discard):
  with open('comm.txt', 'r') as f:
    lines = f.read()

  hand_str, history_str = lines.split('\n')

  if hand_str == '':
    hand = set()
  else:
    hand = { Card(card) for card in hand_str.split(',') }

  if history_str == '':
    history = []
  else:
    history = []
    for turn in history_str.split(','):
      draw_choice, discard_choice = turn.split(';')
      history.append( (draw_choice, Card(discard_choice)) )

  move_choice = choose_move(choose_draw, should_end, choose_discard, hand, history)
  result = str(move_choice)

  with open('comm.txt', 'w') as f:
    f.write(result)

def choose_move(choose_draw, should_end, choose_discard, hand, history):
  if len(hand) == 10:

    # If discard is empty, must draw from deck
    discard = gin.calculate_discard(history)
    if len(discard) == 0:
      return 'deck'
    else:
      return choose_draw(hand, history)

  if gin.can_end(hand) and should_end(hand, history):
    return 'end'

  return choose_discard(hand, history)
