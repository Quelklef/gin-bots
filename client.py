""" Helper module for gin bots that are written in Python """

from cards import Card
import cards
import gin
from channels import Channel

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

def calculate_unseen(hand, history):
  return cards.all_cards - calculate_seen(hand, history)

# == #

def play_bot(bot):
  """ Accepts a bot and plays it against the server.
  The bot must be a generator which accepts and yields the
  proper values at the right times :-).
  Just use the make_bot function to make it... """

  with Channel('client -> server', 'to_server.fifo', 'w') as channel_out, \
       Channel('server -> client', 'to_client.fifo', 'r') as channel_in:

    def read(expected_desc):
      message = channel_in.recv()
      assert message != '', "Server crashed; terminating client."
      desc, payload = message.split(':')
      assert desc == expected_desc, f"Server and client have fallen out of sync. Server at '{desc}' but client at '{expected_desc}'"
      return payload

    def write(desc, payload):
      message = f"{desc}:{payload}"
      channel_out.send(message)

    starting_hand, am_starting = read('starting').split(';')
    starting_hand = set(map(Card, starting_hand.split(',')))

    # Who starts? either 'ours' or 'opponents'
    am_starting = { 'True': True, 'False': False }[am_starting]
    turn = 'ours' if am_starting else 'theirs'

    next(bot)
    bot.send((starting_hand, am_starting))

    while True:

      if turn == 'theirs':
        # get the opponent's move
        # TODO: everywhere, the format for moves should be changed from
        #       (draw_location, discard_choice_or_end) to
        #       (draw_location, discard_choice, do_end)
        draw_location, discard_choice_or_end = read('opponent_turn').split(';')

        if discard_choice_or_end == 'end':
          break

        discard_choice = Card(discard_choice_or_end)
        move = (draw_location, discard_choice)

        next(bot)
        bot.send(move)

      elif turn == 'ours':
        draw_location = next(bot)
        write('draw_from', draw_location)
        drawn_card = Card(read('drawn'))
        discard_choice, do_end = bot.send(drawn_card)
        write('discard', f"{discard_choice};{do_end}")

        if do_end:
          break

      else:
        assert False

      # Switch turns
      turn = {
        'ours': 'theirs',
        'theirs': 'ours',
      }[turn]

def make_bot(choose_draw, choose_discard, should_end):
  """
  Takes three functions `choose_draw`, `choose_discard`, and `should_end` and returns a bot.
  All three functions should take (hand, history, derived), where

    `hand`: The bot's current hand

    `history`: The history of the game, as (draw_location, discard_choice) pairs

    `derived`: (TODO) A bunch of information that is derivable from hand and history
    but done in this function for convenience and efficiency. Contains the following keys:
      "discard"   : the discard pile, ordered chronologically
      "seen"      : cards that have been seen in the game so far
      "unseen"    : cards that have not been seen in the game so far
      "other_hand": cards that are definitely in the other player's hand

  and each should return:

    `choose_draw`: Whether the bot should draw from the deck ('deck') or
    from the discard ('discard'). This function is only called if the bot has a choice;
    if there are no cards in the discard, the bot will be forced to draw from the deck.

    `choose_discard`: What hand the bot wants to discard. Called after `choose_draw`.

    `should_end`: Whether or not the bot wants to end the game. Called after `choose_discard`.
  """

  # our hand
  hand = set()
  # history of moves
  history = []

  # TODO: keep track of derivable values

  # Who starts? either 'ours' or 'theirs'
  starting_hand, am_starting = yield
  yield

  turn = 'ours' if am_starting else 'theirs'
  hand.update(starting_hand)

  while True:

    if turn == 'theirs':
      move = yield
      yield
      history.append(move)

    elif turn == 'ours':
      discard = calculate_discard(history)

      if len(discard) == 0:
        draw_location = 'deck'
      else:
        draw_location = choose_draw({*hand}, [*history])
      drawn_card = yield draw_location

      discard_choice = choose_discard(hand, history)
      do_end = gin.can_end(hand) and should_end({*hand}, [*history])

      yield (discard_choice, do_end)

      hand.remove(discard_choice)
      move = (draw_location, discard_choice)
      history.append(move)

    else:
      assert False

    # Switch turns
    turn = {
      'ours': 'theirs',
      'theirs': 'ours',
    }[turn]
