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

  discard_copy = [*discard]
  draw_choice, discard_choice, bot_ending = player_turn(deck, history, discard, bot, bot_hand)

  if draw_choice == 'discard':
    gained_card = discard_copy[-1]
    print(f"I'll take the {gained_card} the discard; thanks.")

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

  draw_choice = {
    '1': 'deck',
    '2': 'discard',
  }[draw_choice]

  if draw_choice == 'deck':
    deck.card_count -= 1
  if draw_choice == 'discard':
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

  history.append((draw_choice, discard_choice))

  return (draw_choice, discard_choice, human_ending)


if __name__ == '__main__':
  import sys
  sys.path.append('bots/simple')
  from simple_gin import simple_bot
  play(simple_bot, bot_plays_first=True)



# == # == #

# The following code is bad and slated for removal but is needed for this module to run right now

def do_turn(deck, history, discard, player1, hand1, player2, hand2, current_player):
  """ do a turn, returning the score or None if the game isn't done """
  # We choose to make the deck running out be a tie
  if len(deck) == 0:
    return 0

  current_player_hand = hand1 if current_player == player1 else hand2
  other_player_hand   = hand2 if current_player == player1 else hand1
  _, _, player_ending = player_turn(deck, history, discard, current_player, current_player_hand)

  if player_ending:
    score = score_hand(current_player_hand, other_player_hand)
    score_sign = 1 if current_player_hand == hand1 else -1
    return score_sign * score

def player_turn(deck, history, discard, player, hand):
  """ have the player take a turn; return whether or not the player ends the game """

  draw_choice, _                = player_draw   (deck, history, discard, player, hand)
  discard_choice, player_ending = player_discard(deck, history, discard, player, hand)

  history.append((draw_choice, discard_choice))

  return (draw_choice, discard_choice, player_ending)

def player_draw(deck, history, discard, player, hand):
  """ have the player draw a card """
  draw_choice = player({*hand}, [*history])

  if draw_choice == 'deck':
    drawn_card = deck.pop()

  elif draw_choice == 'discard':
    if len(discard) == 0:
      raise ValueError("Cannot draw from an empty discard!")
    drawn_card = discard.pop()

  else:
    raise ValueError(f"Expected either 'deck' or 'discard', not {repr(draw_choice)}.")

  hand.add(drawn_card)

  return (draw_choice, drawn_card)

def player_discard(deck, history, discard, player, hand):
  """ have the player discard a card and optionally end the game """
  discard_choice, do_end = player({*hand}, [*history])
  discard_choice = Card(discard_choice)

  if discard_choice not in hand:
    raise ValueError(f"Cannot discard {discard_choice} since it's not in your hand.")

  discard.append(discard_choice)
  hand.remove(discard_choice)

  if do_end:  # end the game
    if points_leftover(hand) > MAX_POINTS_TO_GO_DOWN:
      raise ValueError(f"Cannot end on more than {MAX_POINTS_TO_GO_DOWN} points.")

  return (discard_choice, do_end)

