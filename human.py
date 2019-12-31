""" a bot that relays to the human at the computer """

from sty import fg, bg, ef, rs

import client
from util import input_until
from gin import calculate_discard

colors = {
  'C': ef.bold,
  'D': fg.red + ef.bold,
  'H': fg.red + ef.bold,
  'S': ef.bold,
}

def print_state(hand, history):
  discard = gin.calculate_discard(history)

  print()
  print()
  print()
  print("Hand:")
  print()
  print(hand_to_art(hand))
  print()
  print("Discard:")
  print()
  print(discard_to_art(discard))
  print()
  print("History:")
  print(history_to_art(history))

def prettier_rank(card):
  return 'X' if card.rank == 10 else card.pretty_rank

def color_art(art, color):
  return '\n'.join( color + line + rs.all for line in art.split('\n') )

def card_to_art(card, idx=None):
  string = """
╭───────╮
│ @ @ @ │
│       │
│   R   │
│       │
│ @ @ @ │
╰───────╯"""[1:]

  string = color_art(string, colors[card.suit])

  if idx:
   string += f"\n  ({idx:>3})  "

  art = string.replace('@', card.sigil).replace('R', prettier_rank(card))
  return art

def card_to_art_but_just_a_lil(card):
  string = """
╭───
│ @ 
│   
│ R 
│   
│ @ 
╰───"""[1:]

  art = string.replace('@', card.sigil).replace('R', prettier_rank(card))
  return color_art(art, colors[card.suit])

def discard_to_art(discard):
  if not discard:
    return "\n" * 3

  discard = [*discard]
  last = discard.pop()
  return join_art( list(map(card_to_art_but_just_a_lil, discard)) + [card_to_art(last)], sep='' )

def art_height(art):
  return len(art.split('\n'))

def join_art(arts, sep=' '):
  lines = [ [] for _ in range(max(map(art_height, arts))) ]

  for art in arts:
    for i, line in enumerate(art.split('\n')):
      lines[i].append(line)

  return '\n'.join( sep.join(line) for line in lines )

def hand_to_art(hand):
  return join_art([ card_to_art(card, i + 1) for i, card in enumerate(hand) ], sep=' ' * 4)

def history_to_art(history):
  h = '; '.join( f"{draw_choice} -> {discard_choice}" for draw_choice, discard_choice in history )
  return f"\n{h}\n"

#= art is over =#

#= now it's bot time =#

def choose_draw(hand, history):
  hand = sorted(hand)
  print_state(hand, history)

  return input_until(
    "Draw from deck or discard? ['deck'/'discard']: ",
    lambda s: s in ['deck', 'discard'],
  )

def choose_discard(hand, history):
  hand = sorted(hand)
  print_state(hand, history)

  card_idx = int(input_until(
    "Card to discard: ",
    lambda s: parse_int_ok(s) and int(s) in range(1, len(hand) + 1),
  ))

  return hand[card_idx - 1]

def parse_int_ok(s):
  try:
    int(s)
    return True
  except ValueError:
    return False

def should_end(hand, history):
  return 'y' == input_until(
    "End the game here? ['y'/'n']: ",
    lambda s: s in ['y', 'n'],
  )

human_bot = client.make_bot(choose_draw, choose_discard, should_end)

if __name__ == '__main__':
  import sys
  sys.path.append('bots/simple')
  from simple_gin import simple_bot
  import gin
  results = gin.play_hand(human_bot, simple_bot)
  print(f"end score: {results}")