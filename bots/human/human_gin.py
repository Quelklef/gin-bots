""" A human player """

import sys
sys.path.append('../..')

from sty import fg, bg, ef, rs

import client
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

def print_state(hand, new_card, history, derivables):
  discard = derivables['discard']
  other_hand = derivables['other_hand']

  other_hand_display = sorted(other_hand) + [None] * (10 - len(other_hand))

  print("\nOther player's hand:\n")
  print(cards_to_art(other_hand_display))
  print("\nDiscard:\n")
  print(discard_to_art(discard))
  print("\nYour hand:\n")
  print(cards_to_art(sorted(hand), new_card))
  print("\nHistory:\n")
  print(history_to_art(history))

def card_template_to_art(template, card):
  pretty = (template[1:-1]
    .replace('@', card.sigil)
    .replace('R', prettier_rank(card))
    )

  return color_art(pretty, colors[card.suit])

def card_to_art(card, new_card=None):
  if card is None:
    s = """
╭───────╮
| ╲   ╱ |
|  ╲ ╱  |
|   ╳   |
|  ╱ ╲  |
| ╱   ╲ |
╰───────╯
"""
    return color_art(s[1:-1], colors['H'])

  else:
    template = r"""
╭───────╮
| @ @ @ |
|       |
|   R   |
|       |
| @ @ @ |
╰───────╯
*********
"""

  if new_card is None or card != new_card:
    template = template.replace('*', ' ')

  return card_template_to_art(template, card)

def card_to_art_but_just_a_lil(card):
  template = """
╭───
| @ 
|   
| R 
|   
| @ 
╰───
"""

  return card_template_to_art(template, card)

def discard_to_art(discard):
  if not discard:
    return "\n" * 3

  discard = [*discard]
  last = discard.pop()
  return join_art( list(map(card_to_art_but_just_a_lil, discard)) + [card_to_art(last)], sep='' )

def cards_to_art(cards, new_card=None):
  if len(cards) == 0:
    return "\n" * 3

  arts = [ card_to_art(card, new_card) for card in cards ]
  return join_art(arts, sep='  ')

def history_to_art(history):
  h = '; '.join( f"{draw_choice} -> {discard_choice}" for draw_choice, discard_choice, do_end in history )
  return f"\n{h}\n"


# == End art == #

last_hand = None

def choose_draw(hand, history, derivables):
  print_state(hand, None, history, derivables)

  return input_until(
    "Draw from deck or discard? ['deck'/'discard']: ",
    lambda s: s in ['deck', 'discard'],
  )

def choose_discard(hand, history, derivables):
  global last_hand

  if last_hand:
    new_card = next(iter(hand - last_hand))
  else:
    new_card = None

  print_state(hand, new_card, history, derivables)

  discard_choice = Card(input_until(
    "Card to discard: ",
    parse_card_is_ok,
  ))

  last_hand = hand - {discard_choice}
  return discard_choice

def should_end(hand, history, derivables):
  return 'y' == input_until(
    "End the game here? ['y'/'n']: ",
    lambda s: s in ['y', 'n'],
  )

human_bot = client.make_bot(choose_draw, choose_discard, should_end)

if __name__ == '__main__':
  client.play_bot(human_bot)

