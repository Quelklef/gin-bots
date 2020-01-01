import os, subprocess, argparse, sys
from pathlib import Path
import itertools as it
import statistics as stat

from cards import Card
import communication
import gin

class GinBot:
  def __init__(self, name, exec_loc):
    self.name = name
    self.exec_loc = exec_loc

  def __str__(self):
    return self.name

  def __enter__(self):
    self.fifo_in, self.fifo_out = communication.open_comms(self.exec_loc)

  def __exit__(self, exc_type, exc_value, traceback):
    communication.close_comms(self.fifo_in, self.fifo_out)
    raise exc_value

  def send_msg(self, message: str):
    assert isinstance(message, str)
    return communication.send_to_client(self.fifo_in, self.fifo_out, message)

  def recv(self):
    return communication.receive_from_client(self.fifo_in, self.fifo_out)

  def send(self, message):
    # This method is questionable (lol)

    message_string = None

    if type(message) is tuple:

      if type(message[1]) is bool:
        hand, is_starting = message
        hand_string = ','.join(map(str, hand))
        message_string = f"{hand_string};{is_starting}"

      else:
        draw_location, discard_choice = message
        message_string = f"{draw_location};{discard_choice}"

    elif type(message) is Card:
      message_string = str(message)

    assert isinstance(message_string, str)

    self.send_msg(message_string)

  def send_and_recv(self, message):
    self.send(message)
    return self.recv()

def compete(bot1, bot2, num_hands=15):
  """ pit two bots against each other """

  with bot1, bot2:

    print(f"\n#= {bot1} vs {bot2} =#")

    scores = []

    is_infinite = num_hands is 0
    if is_infinite:
      range_it = it.count(0)
    else:
      range_it = range(num_hands)

    for i in range_it:
      print(f"Hand #{i + 1}/{num_hands}... ", end='', flush=True)

      result = gin.play_hand(bot1, bot2)
      scores.append(result)

      if result == 0:
        print("tie")
      else:
        winner = bot1 if result > 0 else bot2
        winner_score = abs(result)
        print(f"{winner} wins for {winner_score} points")

      if infinite:
        mean, stdev = mean_and_stdev(scores)
        print(f"cumulative statistics: mean = {mean:+.2f}, stdev = {stdev:.2f}")

    return scores

def do_tournament(bots, num_hands=15):
  """ for a list of bots, pit each bot against every other """

  # Pit every bot against each other
  matches = list(it.combinations(bots, 2))
  match_results = { match: compete(*match, num_hands=num_hands) for match in matches }
  print_scoreboard(match_results)

def print_scoreboard(match_results):
  print("\n\n#== Scoreboard ==#")

  for match, scores in match_results.items():
    bot1, bot2 = match
    mean, stdev = mean_and_stdev(scores)
    print(f"{bot1} vs {bot2}: mean = {mean:+.2f}, stdev = {stdev:.2f}")

def mean_and_stdev(games):
  assert(type(games) is list)
  assert(len(games) is not 0)
  if len(games) is 1:
    return games[0], 0
  return stat.mean(games), stat.stdev(games)


parser = argparse.ArgumentParser(description='Run some gin bots!')
parser.add_argument('bot_names', nargs='*')
parser.add_argument('-n', '--num_hands', type=int, default=15, help='the number of hands of play per match, defaults to 15, 0 means infinite')

if __name__ == '__main__':
  args = parser.parse_args()

  if len(args.bot_names) is 0:
    bot_names = os.listdir('bots/')
  elif len(args.bot_names) is 1:
    print("need to specify two or more bots!")
    sys.exit(1)
  else:
    bot_names = args.bot_names

  try:
    bots = { bot_name: GinBot(bot_name, Path(f"bots/{bot_name}/{bot_name}.sh"))
             for bot_name in args.bot_names }
    do_tournament(bots.values(), num_hands=args.num_hands)
  except FileNotFoundError as e:
    print(f'\n {e.filename} not found')
    sys.exit(1)
