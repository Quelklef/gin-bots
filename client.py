""" Helper module for gin bots that are written in Python """

from cards import Card
import cards
import gin
from channels import Channel

def play_bot(bot):
  """ Accepts a bot and plays it against the server.
  The bot must be a generator which accepts and yields the
  proper values at the right times :-).
  Just use the make_bot function to make it... """

  with Channel('client -> server', 'to_server.fifo', 'w') as channel_out, \
       Channel('server -> client', 'to_client.fifo', 'r') as channel_in:

    def read(expected_desc):
      message = channel_in.recv()
      desc, payload = message.split(':')
      assert desc == expected_desc, f"Server and client have fallen out of sync. Server at '{desc}' but client at '{expected_desc}'"
      return payload

    def write(desc, payload):
      message = f"{desc}:{payload}"
      channel_out.send(message)

    starting_hand, who_starts = read('starting').split(';')
    starting_hand = set(map(Card, starting_hand.split(',')))
    am_starting = { 'you start': True, 'opponent starts': False }[who_starts]
    turn = 'ours' if am_starting else 'theirs'

    next(bot)
    bot.send((starting_hand, am_starting))

    while True:

      if turn == 'theirs':
        # get the opponent's move
        draw_location, discard_choice, end_str = read('opponent_turn').split(';')
        discard_choice = Card(discard_choice)
        do_end = { 'end': True, 'continue': False }[end_str]

        if do_end:
          break

        move = (draw_location, discard_choice, do_end)
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
  Takes three functions `choose_draw`, `choose_discard`, and `should_end` and returns a gin bot.
  All three functions should take (hand, history, derivables), where

    `hand`: The bot's current hand

    `history`: The history of the game, as (draw_location, discard_choice) pairs

    `derivables`: A bunch of information that is derivable from hand and history
    but done in this function for convenience and efficiency. Contains the following keys:
      "discard"   : the discard pile, ordered chronologically
      "other_hand": cards that are definitely in the other player's hand

  and each should return:

    `choose_draw`: Whether the bot should draw from the deck ('deck') or
    from the discard ('discard'). This function is only called if the bot has a choice;
    if there are no cards in the discard, the bot will be forced to draw from the deck.

    `choose_discard`: What hand the bot wants to discard. Called after `choose_draw`.

    `should_end`: Whether or not the bot wants to end the game. Called after `choose_discard`.

  Bots MUST NOT mutate any of these values.
  """

  # Our hand
  hand = set()

  # Deck size
  # Need to keep track of in order to know when a reshuffle happens
  deck_size = 52

  # History of moves
  history = []

  # Discard pile
  discard = []

  # Cards that are definitely in the other hand
  other_hand = set()

  def deck_pop():
    nonlocal deck_size
    deck_size -= 1

    if deck_size == 0:
      # Reshuffle happens
      deck_size = 0
      discard.clear()

  def event__opponent_turn(draw_location, drawn_card, discard_choice, do_end):
    """ Opponent's turn passed. `drawn_card` is a card if known, else None. """
    deck_pop()
    history.append((draw_location, discard_choice, do_end))
    discard.append(discard_choice)
    if drawn_card is not None:
      other_hand.add(drawn_card)

  def event__drew(draw_location, drawn_card):
    """ Drew a card. """
    deck_pop()
    hand.add(drawn_card)

  def event__discarded(discard_choice):
    """ Discarded a card. """
    hand.remove(discard_choice)
    discard.append(discard_choice)

  def event__ending(do_end):
    """ Whether or not we're ending the game. """
    pass

  def event__turn(draw_location, drawn_location, discard_choice, do_end):
    """ Turn passed. Isomorphic to putting code in drew, discarded, and ending. """
    history.append((draw_location, discard_choice, do_end))

  # These values are split into two groups
  # The first groups is the `hand` and `discard` since it encodes
  # the entire game state for a player.
  # The second is all the rest, which we call 'derivables' since
  # they /could/ be derived from the hand and history. They are
  # instead calculated here for convenience and afficiency.

  derivables = {
    "discard": discard,
    "other_hand": other_hand,
  }

  # Who starts? either 'ours' or 'theirs'
  starting_hand, am_starting = yield
  yield

  active_player = 'us' if am_starting else 'them'

  # Starting hand is encoded as a bunch of draws
  for card in starting_hand:
    event__drew('deck', card)

  while True:

    if active_player == 'them':
      turn = draw_location, discard_choice, do_end = yield
      yield

      if draw_location == 'discard':
        drawn_card = discard[-1]
      else:
        drawn_card = None

      event__opponent_turn(draw_location, drawn_card, discard_choice, do_end)

      if do_end:
        break

    elif active_player == 'us':
      if len(discard) == 0:
        draw_location = 'deck'
      else:
        draw_location = choose_draw(hand, history, derivables)
      drawn_card = yield draw_location

      event__drew(draw_location, drawn_card)

      discard_choice = choose_discard(hand, history, derivables)
      do_end = gin.can_end(hand) and should_end(hand, history, derivables)

      yield (discard_choice, do_end)

      event__discarded(discard_choice)
      event__ending(do_end)

      event__turn(draw_location, drawn_card, discard_choice, do_end)

    else:
      assert False, f"Unknown active player {repr(active_player)}"

    # Switch turns
    active_player = {
      'us': 'them',
      'them': 'us',
    }[active_player]

