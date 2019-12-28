import os
import subprocess
from pathlib import Path
import itertools as it
from collections import namedtuple

import communication
import gin

class GinBot:
  def __init__(self, name, exec_loc):
    self.name = name
    self.exec_loc = exec_loc

  def call_exec(self, *args):
    return communication.to_client(self.exec_loc, args)

  def __call__(self, hand, history):
    result = self.call_exec(
      ','.join(map(str, hand)),
      ','.join(f"{draw_choice};{discard_choice}" for draw_choice, discard_choice in history),
    )
    return result


def do_tournament(bots):
  """ For a list of bots, pit each bot against every other """

  # Pit every bot against each other

  matches = it.combinations(bots, 2)
  scores = { match: 0 for match in matches }

  for match in matches:
    bot1, bot2 = match

    result = play_hand(bot1, bot2)

    scores[match] += result

    if result == 0:
      print(f"{bot1} vs {bot2}: tie")
    else:
      winner = bot1 if result > 0 else bot2
      winner_score = abs(result)
      print(f"{bot1} vs {bot2}: {winner} wins with a score of {winner_score}")


def main():
  bot_names = os.listdir('bots/')

  bots = [ GinBot(bot_name, Path(f"bots/{bot_name}/{bot_name}.sh"))
           for bot_name in bot_names ]

  do_tournament(bots)


if __name__ == '__main__':
  #main()

  random_bot_1 = GinBot('random1', Path('bots/random/random.sh'))
  random_bot_2 = GinBot('random2', Path('bots/random/random.sh'))
  result = gin.play_hand(random_bot_1, random_bot_2)
  print(result)
