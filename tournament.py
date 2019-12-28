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

  def __str__(self):
    return self.name

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
  matches = list(it.combinations(bots, 2))
  scores = { match: 0 for match in matches }

  for match in matches:
    bot1, bot2 = match

    print(f"{bot1} vs {bot2}... ", end='', flush=True)

    result = gin.play_hand(bot1, bot2)
    scores[match] = result

    if result == 0:
      print("tie")
    else:
      winner = bot1 if result > 0 else bot2
      winner_score = abs(result)
      print(f"{winner} wins for {winner_score} points")


def main():
  bot_names = os.listdir('bots/')

  bots = [ GinBot(bot_name, Path(f"bots/{bot_name}/{bot_name}.sh"))
           for bot_name in bot_names ]

  do_tournament(bots)


if __name__ == '__main__':
  main()
