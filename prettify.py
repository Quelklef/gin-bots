""" Pretty displays of game data """

import sty

from art import Art
from cards import Card
import gin

# Map suit -> color
colors = {
  'C': sty.ef.bold,
  'D': sty.fg.red + sty.ef.bold,
  'H': sty.fg.red + sty.ef.bold,
  'S': sty.ef.bold,
}

def prettier_rank(card):
  return 'X' if card.rank == 10 else card.pretty_rank

def fill_template(template, card):
  return (template
    .replace('@', card.sigil)
    .replace('R', prettier_rank(card))
    )

def card_to_art(card, drawn_card=None):
  if card is None:
    art = Art(
      lines=[
        "╭───────╮",
        "│ ╲   ╱ │",
        "│  ╲ ╱  │",
        "│   ╳   │",
        "│  ╱ ╲  │",
        "│ ╱   ╲ │",
        "╰───────╯",
      ],
      color=colors['H']
    )

    return art

  else:
    template = Art(
      lines=[
        "╭───────╮",
        "│ @ @ @ │",
        "│       │",
        "│   R   │",
        "│       │",
        "│ @ @ @ │",
        "╰───────╯",
        "*********",
      ],
      color=colors[card.suit]
    )

    if drawn_card is None or card != drawn_card:
      template = template.replace('*', ' ')

    return fill_template(template, card)

def card_to_art_but_just_a_lil(card):
  template = Art(
    lines=[
      "╭───",
      "│ @ ",
      "│   ",
      "│ R ",
      "│   ",
      "│ @ ",
      "╰───",
    ],
    color=colors[card.suit],
  )

  return fill_template(template, card)

def prettify_discard(discard):
  """ Turn a discard pile into Art """
  if not discard:
    return Art(lines=[""] * 3)

  discard = [*discard]
  last = discard.pop()
  return Art('').join( [card_to_art_but_just_a_lil(card) for card in discard] + [card_to_art(last)] )

def prettify_cards(cards, *, drawn_card=None):
  """ Turn a list of cards into Art """
  if len(cards) == 0:
    return Art.blank(width=1, height=7)

  return Art('  ').join(card_to_art(card, drawn_card) for card in cards)

def prettify_move(move):
  """ Turn a game move into a pretty string """
  draw_location, discard_choice, do_end = move
  end_str = ' end!' if do_end else ''
  return f"(+{draw_location} -{discard_choice}{end_str})"

def prettify_history(history):
  """ Turn a history into a pretty string """
  return "; ".join(map(prettify_move, history))

def prettify_state(hand1, hand2, history, discard, *, drawn_card_1=None, drawn_card_2=None):
  """ Turn a game state into Art """

  def pad_hand(hand):
    return sorted(hand) + [None] * (10 - len(hand))

  # pad hands
  hand1 = pad_hand(hand1)
  hand2 = pad_hand(hand2)

  return ''.join([
    "\n\Hand 1:\n",
    str(prettify_cards(hand1, drawn_card=drawn_card_1)),
    "\n\nDiscard:\n",
    str(prettify_discard(discard)),
    "\n\Hand 2:\n",
    str(prettify_cards(hand2, drawn_card=drawn_card_2)),
    "\n\nHistory:\n",
    str(prettify_history(history)),
    "\n",
  ])

# == A different way of displaying state == #

def split_discard(history):
  """ Split a discard into the cards discarded by the first player, and those by the second """

  deck_size = 52

  discard1 = []
  discard2 = []

  discard = discard2

  def swap_discards():
    nonlocal discard
    if discard is discard1:
      discard = discard2
    else:
      discard = discard1

  for turn in history:
    draw_location, discard_choice, do_end = turn

    if draw_location == 'discard':
      discard.pop()
    else:
      deck_size -= 1

    swap_discards()

    discard.append(discard_choice)

    # reshuffle
    if deck_size == 0:
      discard1 = []
      discard2 = []

  return (discard1, discard2)

def prettify_state_table(hand1, hand2, history, discard,
    *, drawn_card_1=None, drawn_card_2=None, player_1_char='1', player_2_char='2'):
  """ Return a game state into a pretty string of a table """

  discard1, discard2 = split_discard(history)

  grid_style = sty.ef.dim

  template = f"""

blue: hand 1; green: hand 2; red: discarded; underline: recent
{grid_style}
   ╷   ╷   ╷   ╷   ╷   ╷   ╷   ╷   ╷   ╷   ╷   ╷   ╷   ╷
   │ % │ % │ % │ % │ % │ % │ % │ % │ % │ % │ % │ % │ % │
╶──┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
 $_│ # │ # │ # │ # │ # │ # │ # │ # │ # │ # │ # │ # │ # │
╶──┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
 $_│ # │ # │ # │ # │ # │ # │ # │ # │ # │ # │ # │ # │ # │
╶──┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
 $_│ # │ # │ # │ # │ # │ # │ # │ # │ # │ # │ # │ # │ # │
╶──┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
 $_│ # │ # │ # │ # │ # │ # │ # │ # │ # │ # │ # │ # │ # │
╶──┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
{sty.rs.all}
"""[1:-1]

  style_suit = lambda s: sty.rs.all + s + sty.rs.all + grid_style
  suits = map(style_suit, 'A23456789XJQK')

  style_rank = lambda r: sty.rs.all + sty.ef.bold + r + sty.rs.all + grid_style
  ranks = map(style_rank, ['♠ ', '♥ ', '♦ ', '♣ '])

  def style_cell(card):
    if card in hand1:
      string = sty.ef.bold + sty.fg.li_yellow + player_1_char + sty.rs.all + grid_style
      if card == drawn_card_1:
        string = sty.ef.underl + string
      return string

    elif card in hand2:
      string = sty.ef.bold + sty.fg.li_cyan + player_2_char + sty.rs.all + grid_style
      if card == drawn_card_2:
        string = sty.ef.underl + string
      return string

    elif card in discard:
      letter = player_1_char if card in discard1 else player_2_char
      string = sty.ef.bold + sty.fg.blue + letter + sty.rs.all + grid_style
      if card == discard[-1]:
        string = sty.ef.underl + string
      return string

    else:
      return ' '

  cards = [ Card(f"{suit}{rank}") for suit in 'SHDC' for rank in range(1, 13 + 1) ]
  cells = map(style_cell, cards)

  result_chars = []
  for char in template:
    if char == '#':
      result_chars.append(next(cells))
    elif char == '%':
      result_chars.append(next(suits))
    elif char == '$':
      result_chars.append(next(ranks))
    elif char == '_':
      pass
    else:
      result_chars.append(char)

  return ''.join(result_chars)

