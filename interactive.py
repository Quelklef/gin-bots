""" for playing a human player against a bot using a physical deck """

import gin
import client

def input_until(string, predicate):
  while True:
    val = input(string)
    if predicate(val):
      return val
    else:
      print("Invalid input! Try again.")

def parse_card_is_ok(string):
  try:
    Card(string)
    return True
  except ValueError:
    return False

#= define physical deck =#

class PhysicalDeck:
  def __init__(self):
    self.card_count = 52

  def pop(self):
    card = input_until(
      "Draw a card from the deck and tell me what you got: ",
      parse_card_is_ok,
    )
    self.card_count -= 1
    return Card(card)

  def __len__(self):
    return self.card_count

#= define game =#

def play(bot, *, bot_plays_first: bool):
  deck = PhysicalDeck()
  history = []
  discard = []

  bot = bot
  bot_hand = { deck.pop() for _ in range(10) }

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

  print(f"What were the human player's cards?")
  human_hand = set()
  for i in range(1, 11):
    card = input_until(
      "Card #{i}: ",
      parse_card_is_ok,
    )
    human_hand.add(card)

  score = gin.score_hand(bot_hand, human_hand)
  print(f"Score, bot-relative, is {score}")

def play_bots_turn(deck, history, discard, bot, bot_hand):
  draw_choice, discard_choice, bot_ending = gin.player_turn(deck, history, discard, bot, bot_hand)

  if bot_ending:
    print("Bot chooses to end the game.")
  else:
    print(f"Bot discards {discard_choice}.")

  return (draw_choice, discard_choice, bot_ending)

def play_humans_turn(deck, history, discard):
  draw_choice = input_until(
    "Did the human draw from the deck or from the discard? ['deck'/'discard']: ",
    lambda s: s in ['deck', 'discard']
  )

  if draw_choice == 'deck':
    deck.discard()
  if draw_choice == 'discard':
    discard.pop()

  human_ending = 'y' == input_until(
    "Is the human ending the game? ['y'/'n']: ",
    lambda s: s in ['y', 'n'],
  )

  if human_ending:
    # Not sure what the human discarded since played face-down
    discard_choice = None
  if not human_ending:
    discard_choice = Card(input_until(
      "What did the human discard? ",
      parse_card_is_ok,
    ))
    discard.append(discard_choice)

  return (draw_choice, discard_choice, human_ending)
