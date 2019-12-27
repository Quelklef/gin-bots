import random
import sys
sys.path.append('../..')

from gin import can_end
from cards import Card
from client import play_bot

def bot(hand, stack, history):
  """ play some gin """

  if len(hand) == 10:
    # Need to choose where to draw from

    if len(stack) == 0:
      return 'deck'
    else:
      return random.choice(['deck', 'stack'])

  else:

    # end with 30% chance if we're able to
    if can_end(hand) and random.random() < 0.3:
      return 'end'

    # Need to choose what card to discard
    return random.choice([*hand])


if __name__ == '__main__':
  play_bot(bot)
