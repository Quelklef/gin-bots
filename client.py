""" Helper module for gin bots that are written in Python """

from cards import Card
import gin

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

    if len(hand) == 10:
      discard = gin.calculate_discard(history)
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
