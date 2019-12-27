import os
import subprocess
from pathlib import Path
import itertools as it
from collections import namedtuple

import gin

GinBot = namedtuple('GinBot', ['name', 'exec_loc'])

def bot_to_function(bot):
  """ make a Python function that proxies the bot executable """
  def function(argument):
    if not isinstance(argument, str):
      raise ValueError(f"Argument must be an instance of str, not of type {type(argument)}.")

    # https://stackoverflow.com/a/4760517/4608364
    return subprocess.run([bot.exec_loc, argument], stdout=subprocess.PIPE).stdout.decode()
  return function

def do_tournament(bots):
  """ For a list of bots, pit each bot against every other """

  # Pit every bot against each other

  matches = it.combinations(bots, 2)
  scores = { match: 0 for match in matches }

  for match in matches:
    bot1, bot2 = match

    result = play_hand(
      bot_to_function(bot1),
      bot_to_function(bot2),
    )

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
  main()
