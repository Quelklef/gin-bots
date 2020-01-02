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

def print_state(hand, new_card, history, discard):
  print("\n\nHand:\n")
  print(hand_to_art(hand, new_card))
  print("\n\nDiscard:\n")
  print(discard_to_art(discard))
  print("\n\nHistory:\n")
  print(history_to_art(history))

def card_template_to_art(template, card):
  pretty = (template[1:-1]
    .replace('@', card.sigil)
    .replace('R', prettier_rank(card))
    .replace('r', '╭')
    .replace('\\', '╮')
    .replace('L', '╰')
    .replace('/', '╯')
    .replace('|', '│')
    .replace('-', '─')
    )

  return color_art(pretty, colors[card.suit])

def card_to_art(card, new_card=None):
  template = r"""
r-------\
| @ @ @ |
|       |
|   R   |
|       |
| @ @ @ |
L-------/
^^^^^^^^^
"""

  if card != new_card:
    template = template.replace('^', ' ')

  return card_template_to_art(template, card)

def card_to_art_but_just_a_lil(card):
  template = """
r---
| @ 
|   
| R 
|   
| @ 
L---
"""

  return card_template_to_art(template, card)

def discard_to_art(discard):
  if not discard:
    return "\n" * 3

  discard = [*discard]
  last = discard.pop()
  return join_art( list(map(card_to_art_but_just_a_lil, discard)) + [card_to_art(last)], sep='' )

def hand_to_art(hand, new_card):
  arts = [ card_to_art(card, new_card) for card in hand ]
  return join_art(arts, sep='  ')

def history_to_art(history):
  h = '; '.join( f"{draw_choice} -> {discard_choice}" for draw_choice, discard_choice, do_end in history )
  return f"\n{h}\n"


# == End art == #

last_hand = None

def choose_draw(hand, history, derivables):
  discard = derivables['discard']
  print_state(sorted(hand), None, history, discard)

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

  discard = derivables['discard']

  print_state(sorted(hand), new_card, history, discard)

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

