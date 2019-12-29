import os
import subprocess
from pathlib import Path
import itertools as it
import statistics as stat

import communication
import gin

class GinBot:
  def __init__(self, name, exec_loc):
    self.name = name
    self.exec_loc = exec_loc

  def __str__(self):
    return self.name

  def call_exec(self, *args):
    return eval(communication.to_client(self.exec_loc, args))

  def __call__(self, hand, history):
    result = self.call_exec(
      ','.join(map(str, hand)),
      ','.join(f"{draw_choice};{discard_choice}" for draw_choice, discard_choice in history),
    )
    return result

def compete(bot1, bot2, n=15):
  """ pit two bots against each other """
  scores = []

  for i in range(n):
    print(f"Hand #{i + 1}/{n}... ", end='', flush=True)

    result = gin.play_hand(bot1, bot2)
    scores.append(result)

    if result == 0:
      print("tie")
    else:
      winner = bot1 if result > 0 else bot2
      winner_score = abs(result)
      print(f"{winner} wins for {winner_score} points")

  return scores

def do_tournament(bots, n=20):
  """ for a list of bots, pit each bot against every other """

  # Pit every bot against each other
  matches = list(it.combinations(bots, 2))
  scores = { match: compete(*match) for match in matches }

  print("\n\n\n#== Scoreboard ==#")

  for match in matches:
    bot1, bot2 = match
    games = scores[match]
    mean = stat.mean(games)
    stdev = stat.stdev(games)
    print(f"{bot1} vs {bot2}: mean = {mean:+.2f}, stdev = {stdev:.2f}")


bot_names = os.listdir('bots/')

bots = { bot_name: GinBot(bot_name, Path(f"bots/{bot_name}/{bot_name}.sh"))
         for bot_name in bot_names }

if __name__ == '__main__':
  do_tournament(bots)
