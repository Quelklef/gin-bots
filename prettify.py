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
    art = Art(
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
      art = art.replace('*', ' ')

    return fill_template(art, card)

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

  return fill_template(art, card)

def prettify_discard(discard):
  """ Turn a discard pile into Art """
  if not discard:
    return Art(lines=[] * 3)

  discard = [*discard]
  last = discard.pop()
  return join_art( list(map(card_to_art_but_just_a_lil, discard)) + [card_to_art(last)], sep='' )

def prettify_cards(cards, *, drawn_card=None):
  """ Turn a list of cards into Art """
  if len(cards) == 0:
    return Art.blank(width=1, height=7)

  return '  '.join(card_to_art(card, drawn_card) for card in cards)

def prettify_move(move):
  """ Turn a game move into a pretty string """
  draw_location, discard_choice, do_end = move
  end_str = ' end!' if do_end else ''
  return f"(+{draw_location} -{discard_choice}{end_str})"

def prettify_history(history):
  """ Turn a history into a pretty string """
  return "; ".join(map(prettify_move, history))

def prettify_state(hand, history, derivables, *, drawn_card=None):
  """ Turn a game state into Art """

  discard = derivables['discard']
  other_hand = derivables['other_hand']

  other_hand_padded = sorted(other_hand) + [None] * (10 - len(other_hand))

  return ''.join([
    "\nOther player's hand:\n",
    prettify_cards(other_hand_padded),
    "\nDiscard:\n",
    prettify_discard(discard),
    "\nYour hand:\n",
    prettify_cards(sorted(hand), drawn_card),
    "\nHistory:\n",
    prettify_history(history),
  ])

# == A different way of displaying state == #

def prettify_state_table(hand, history, derivables, *, drawn_card=None):
  """ Return a game state into a pretty string of a table """

  their_hand = derivables['other_hand']
  discard = derivables['discard']
  our_discard = derivables['our_discard']
  their_discard = derivables['their_discard']

  print()
  print('new card:', str(drawn_card))
  print('discard pile:', ','.join(map(str, discard)))
  melds, deadwood = gin.arrange_hand(hand)
  print('history:', '; '.join(map(lambda move: f"(+{move[0]} -{move[1]})", history)))
  print('melds:', ' & '.join(map(lambda meld: ','.join(map(str, meld)), melds)))
  print('deadwood:', ','.join(map(str, deadwood)))
  print('deadwood points:', gin.points_leftover(hand))
  print()

  grid_style = sty.ef.dim

  template = f"""
blue: yours (underline: just drawn); red: theirs; green: discarded (underline: just discarded by them)
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
    if card in hand:
      string = sty.ef.bold + sty.fg.li_blue + 'Y' + sty.rs.all + grid_style
      if card == drawn_card:
        string = sty.ef.underl + string
      return string

    elif card in their_hand:
      return sty.ef.bold + sty.fg.li_red + 'T' + sty.rs.all + grid_style

    elif card in discard:
      letter = 'Y' if card in our_discard else 'T'
      string = sty.ef.bold + sty.fg.green + letter + sty.rs.all + grid_style
      if card == discard[-1] and card in their_discard:
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

