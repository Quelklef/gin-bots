"""
For playing a human player against a bot using a physical deck.

Sample REPL code to use this module:
  >>> import sys
  >>> sys.path.append('bots/simple')
  >>> from simple_gin import simple_bot
  >>> import interactive
  >>> interactive.play(simple_bot, bot_plays_first=True)

Of course, you can replace the simple bot with any bot
"""

import gin
import client
from cards import Card, parse_card_is_ok
from util import input_until

#= define physical deck =#

class PhysicalDeck:
  def __init__(self):
    self.card_count = 52

  def pop(self):
    card = Card(input_until(
      "Draw for me, please: ",
      parse_card_is_ok,
    ))
    self.card_count -= 1
    return card

  def __len__(self):
    return self.card_count

#= define game =#

def get_hand():
  hand = set()

  for i in range(1, 10 + 1):
    while True:
      card = Card(input_until(
        f"Card #{i}: ",
        lambda s: parse_card_is_ok,
      ))

      if card in hand:
        print("Woah, you've already given me that card. Try again.")
        continue

      hand.add(card)
      break

  return hand

def get_bot_hand():
  print("What's my hand?")
  return get_hand()

def play(bot, *, bot_plays_first: bool):
  deck = PhysicalDeck()
  history = []
  discard = []

  bot_hand = get_bot_hand()
  is_bots_turn = bot_plays_first

  while True:
    # Deck running out is a tie
    if len(deck) == 0:
      return 0

    if is_bots_turn:
      _, _, bot_ending = play_bots_turn(deck, history, discard, bot, bot_hand)
      if bot_ending: break

    else:
      _, _, player_ending = play_humans_turn(deck, history, discard)
      if player_ending: break

    is_bots_turn = not is_bots_turn

  end_game(bot_hand)

def end_game(bot_hand):
  print(f"What were the human player's cards?")
  human_hand = get_hand()
  score = gin.score_hand(bot_hand, human_hand)
  print(f"Score, bot-relative, is {score}")

def play_bots_turn(deck, history, discard, bot, bot_hand):

  draw_choice, discard_choice, bot_ending = gin.player_turn(deck, history, discard, bot, bot_hand)

  if draw_choice == 'discard':
    print(f"I'll take the {discard[-1]} from the discard; thanks.")

  if bot_ending:
    points = gin.points_leftover(bot_hand)
    if points == 0:
      print(f"Discard {discard_choice}: Gin!")
    else:
      print(f"I'll discard {discard_choice} to go down for {points}.")
  else:
    print(f"Discard {discard_choice}, please.")

  return (draw_choice, discard_choice, bot_ending)

def play_humans_turn(deck, history, discard):
  draw_choice = input_until(
    "Did the human draw from the deck (1) or from the discard (2)? [1/2]: ",
    lambda s: s in ['1', '2']
  )

  if draw_choice == '1':
    deck.card_count -= 1
  if draw_choice == '2':
    discard.pop()

  human_move = input_until(
    "What did the human discard? Or are they ending the game? [card/'end']: ",
    lambda s: s == 'end' or parse_card_is_ok(s),
  )

  human_ending = human_move == 'end'

  if human_ending:
    # Not sure what the human discarded since played face-down
    discard_choice = None
  else:
    discard_choice = Card(human_move)
    discard.append(discard_choice)

  return (draw_choice, discard_choice, human_ending)


if __name__ == '__main__':
  import sys
  sys.path.append('bots/simple')
  from simple_gin import simple_bot
  play(simple_bot, bot_plays_first=True)
