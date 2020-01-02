""" A human player """

import sys
sys.path.append('../..')

from sty import fg, bg, ef, rs

import client
import gin
from util import input_until
from cards import Card, parse_card_is_ok

def art_height(art):
  return len(art.split('\n'))

def art_width(art):
  return max(map(len, art.split('\n')))

def join_art(arts, sep=' '):
  lines = [ [] for _ in range(max(map(art_height, arts))) ]

  for art in arts:
    for i, line in enumerate(art.split('\n')):
      lines[i].append(line)

  return '\n'.join( sep.join(line) for line in lines )

def color_art(art, color):
  return '\n'.join( color + line + rs.all for line in art.split('\n') )

# == End art lib == #

colors = {
  'C': ef.bold,
  'D': fg.red + ef.bold,
  'H': fg.red + ef.bold,
  'S': ef.bold,
}

def prettier_rank(card):
  return 'X' if card.rank == 10 else card.pretty_rank

def print_state(hand, drawn_card, history, derivables):
  discard = derivables['discard']
  other_hand = derivables['other_hand']

  other_hand_display = sorted(other_hand) + [None] * (10 - len(other_hand))

  print("\nOther player's hand:\n")
  print(cards_to_art(other_hand_display))
  print("\nDiscard:\n")
  print(discard_to_art(discard))
  print("\nYour hand:\n")
  print(cards_to_art(sorted(hand), drawn_card))
  print("\nHistory:\n")
  print(history_to_art(history))

def card_template_to_art(template, card):
  pretty = (template[1:-1]
    .replace('@', card.sigil)
    .replace('R', prettier_rank(card))
    )

  return color_art(pretty, colors[card.suit])

def card_to_art(card, drawn_card=None):
  if card is None:
    s = """
╭───────╮
│ ╲   ╱ │
│  ╲ ╱  │
│   ╳   │
│  ╱ ╲  │
│ ╱   ╲ │
╰───────╯
"""
    return color_art(s[1:-1], colors['H'])

  else:
    template = r"""
╭───────╮
│ @ @ @ │
│       │
│   R   │
│       │
│ @ @ @ │
╰───────╯
*********
"""

  if drawn_card is None or card != drawn_card:
    template = template.replace('*', ' ')

  return card_template_to_art(template, card)

def card_to_art_but_just_a_lil(card):
  template = """
╭───
│ @ 
│   
│ R 
│   
│ @ 
╰───
"""

  return card_template_to_art(template, card)

def discard_to_art(discard):
  if not discard:
    return "\n" * 3

  discard = [*discard]
  last = discard.pop()
  return join_art( list(map(card_to_art_but_just_a_lil, discard)) + [card_to_art(last)], sep='' )

def cards_to_art(cards, drawn_card=None):
  if len(cards) == 0:
    return "\n" * 3

  arts = [ card_to_art(card, drawn_card) for card in cards ]
  return join_art(arts, sep='  ')

def history_to_art(history):
  h = '; '.join( f"{draw_choice} -> {discard_choice}" for draw_choice, discard_choice, do_end in history )
  return f"\n{h}\n"


# == A different way of displaying state == #


def print_state_tables(hand, drawn_card, history, derivables):
  print(state_to_art_tables(hand, drawn_card, history, derivables))

def state_to_art_tables(hand, drawn_card, history, derivables):

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

  grid_style = ef.dim

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
{rs.all}
"""[1:-1]

  style_suit = lambda s: rs.all + s + rs.all + grid_style
  suits = map(style_suit, 'A23456789XJQK')

  style_rank = lambda r: rs.all + ef.bold + r + rs.all + grid_style
  ranks = map(style_rank, ['♠ ', '♥ ', '♦ ', '♣ '])

  def cells():
    for suit in 'SHDC':
      for rank in range(1, 13 + 1):
        card = Card(f"{suit}{rank}")

        if card in hand:
          string = ef.bold + fg.li_blue + 'Y' + rs.all + grid_style
          if card == drawn_card:
            string = ef.underl + string
          yield string

        elif card in their_hand:
          yield ef.bold + fg.li_red + 'T' + rs.all + grid_style

        elif card in discard:
          letter = 'Y' if card in our_discard else 'T'
          string = ef.bold + fg.green + letter + rs.all + grid_style
          if card == their_discard[-1]:
            string = ef.underl + string
          yield string

        else:
          yield ' '

  cells = cells()

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

# == End art == #


hand_before_draw = None

def choose_draw(hand, history, derivables):
  print_state_tables(hand, None, history, derivables)

  global hand_before_draw
  hand_before_draw = {*hand}

  return input_until(
    "Draw from deck or discard? ['deck'/'discard']: ",
    lambda s: s in ['deck', 'discard'],
  )

def choose_discard(hand, history, derivables):
  if hand_before_draw:
    drawn_card = next(iter(hand - hand_before_draw))
  else:
    drawn_card = None

  print_state_tables(hand, drawn_card, history, derivables)

  discard_choice = Card(input_until(
    "Card to discard: ",
    lambda card: parse_card_is_ok(card) and Card(card) in hand,
    error="Either bad format or card not in hand.",
  ))

  return discard_choice

def should_end(hand, history, derivables):
  print_state_tables(hand, None, history, derivables)

  return 'y' == input_until(
    "End the game here? ['y'/'n']: ",
    lambda s: s in ['y', 'n'],
  )

human_bot = client.make_bot(choose_draw, choose_discard, should_end)

if __name__ == '__main__':
  client.play_bot(human_bot)

