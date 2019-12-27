import os
from pathlib import Path

class GinBot:
  def __init__(self, name: str, exec_loc: Path):
    self.name = name
    self.exec_loc = exec_loc

def do_tournament(bots):
  """ For a list of bots, pit each bot against every other """

  # Pit every bot against each other

  matches = ( (bot1, bot2)
              for bot1 in bots
              for bot2 in bots
              # Don't make bots fight themselves
              if bot1 != bot2 )

  scores = { match: 0 for match in matches }

  for match in matches:
    bot1, bot2 = match

    result = do_match(
      f"bots/{bot1}",
      f"bots/{bot2}",
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
