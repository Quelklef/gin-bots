""" Helper module for gin bots that are written in Python """

from cards import Card
import gin

def calculate_discard(history):
  """ calculate the current discard pile from a history """
  discard = []

  for draw_choice, discard_choice in history:
    if draw_choice == 'discard':
      discard.pop()
    discard.append(discard_choice)

  return discard

def calculate_other_hand(history):
  """ From a history, calculate the cards that are definitely in the other player's hand
  Assumes that the current turn is 'our' turn. """

  # whose turn was the first turn
  their_turn = len(history) % 2 != 0

  their_hand = set()

  # discard pile
  discard = []

  # simulate game
  for draw_choice, discard_choice in history:
    if draw_choice == 'discard':
      card = discard.pop()
      if their_turn:
        their_hand.add(card)

    discard.append(discard_choice)
    if their_turn:
      their_hand.discard(discard_choice)

    their_turn = not their_turn

  return their_hand

def calculate_seen(hand, history):
  """ Calculate all the cards that definitely ARENT in the deck """
  played = { discard_choice for draw_choice, discard_choice in history }
  return played | hand

def caluclate_unseen(hand, history):
  return cards.all_cards - calculate_seen(hand, history)

# == #

def play_bot(bot):
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

  move_choice = bot(hand, history)
  result = repr(move_choice)

  with open('comm.txt', 'w') as f:
    f.write(result)

def make_bot(choose_draw, choose_discard, should_end):
  """ Takes three functions `choose_draw`, `choose_discard`, and `should_end` and returns a bot.
  All three functions should take (hand, history) and return:

    `choose_draw`: Whether the bot should draw from the deck ('deck') or
    from the discard ('discard'). This function is only called if the bot has a choice;
    if there are no cards in the discard, the bot will be forced to draw from the deck.

    `choose_discard`: What hand the bot wants to discard. Called after `choose_draw`.

    `should_end`: Whether or not the bot wants to end the game. Called after `choose_discard`.

  """

  def bot(hand, history):
    assert(len(hand) in [10, 11])

    if len(hand) == 10:
      discard = calculate_discard(history)
      # If discard is empty, must draw from deck
      if len(discard) == 0:
        return 'deck'
      else:
        return choose_draw({*hand}, [*history])

    discard_choice = choose_discard({*hand}, [*history])
    hand.remove(discard_choice)

    do_end = gin.can_end(hand) and should_end({*hand}, [*history])

    return (str(discard_choice), do_end)

  return bot
