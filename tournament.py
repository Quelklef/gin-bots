import os
import subprocess
import argparse
import sys
from pathlib import Path
import itertools as it
import statistics as stat

from cards import Card
from channels import Channel
import channels
import gin
import prettify

class GinBot:
  def __init__(self, name, exec_loc):
    self.name = name
    self.exec_loc = exec_loc

  def __str__(self):
    return self.name

  def __enter__(self):
    client_name = self.exec_loc.stem

    registration_channel = Channel(
      name=f"client '{client_name}' registration",
      id="gin_registration",
      role=Channel.SERVER,
    )

    registration_channel.open()

    subprocess.Popen(
      ['sh', self.exec_loc.name],
      cwd=self.exec_loc.parent,
      stdout=sys.stdout,
    )

    channel_id = registration_channel.recv()

    self.channel = Channel(
      name=f'server <-> {client_name}',
      id=channel_id,
      role=Channel.SERVER,
    )

    self.channel.open()

    registration_channel.send('fifos made')
    registration_channel.close()

  def __exit__(self, exc_type, exc_value, traceback):
    self.channel.close()

    if exc_value is not None:
      raise exc_value

  def send_string(self, message: str):
    self.channel.send(message)

  def send(self, desc, *args):
    message_string = None

    if desc == 'starting':
      # Start of the game
      hand, is_starting = args
      hand_str = ','.join(map(str, hand))
      starting_str = { True: 'you start', False: 'opponent starts' }[is_starting]
      message_string = f"starting:{hand_str};{starting_str}"

    elif desc == 'opponent_turn':
      # The opponent played; this was their turn
      opponent_turn, = args
      draw_location, discard_choice, do_end = opponent_turn
      end_str = { True: 'end', False: 'continue' }[do_end]
      message_string = f"opponent_turn:{draw_location};{discard_choice};{end_str}"

    elif desc == 'drawn':
      # This is the card that the agent drew
      drawn_card, = args
      message_string = f"drawn:{drawn_card}"

    else:
      assert False, f"Unrecognized message description {desc}"

    self.send_string(message_string)

  def recv(self):
    message_string = self.channel.recv()
    desc, payload = message_string.split(':')

    if desc == 'draw_from':
      assert payload in ['deck', 'discard']
      return payload

    elif desc == 'discard':
      discard_choice, do_end = payload.split(';')
      discard_choice = Card(discard_choice)
      do_end = { 'True': True, 'False': False }[do_end]
      return (discard_choice, do_end)

    else:
      assert False, f"Unrecognized message description {desc}"

  def send_and_recv(self, *args, **kwargs):
    self.send(*args, **kwargs)
    return self.recv()

prettify_state = prettify.prettify_state
def print_state(hand1, hand2, history, discard):
  pretty = prettify_state(hand1, hand2, history, discard)
  print(pretty, end='')

def compete(bot1, bot2, num_hands=15):
  """ pit two bots against each other """

  print(f"\n#= {bot1} vs {bot2} =#")

  scores = []

  is_infinite = num_hands == 0
  if is_infinite:
    range_it = it.count(0)
  else:
    range_it = range(num_hands)

  for i in range_it:
    print(f"Hand #{i + 1}/{num_hands}... ", end='', flush=True)

    with bot1, bot2:
      result = gin.play_hand(bot1, bot2, state_callback=print_state)

    assert result != 0, "Something is wrong"

    scores.append(result)

    winner = bot1 if result > 0 else bot2
    winner_score = abs(result)
    print(f"{winner} wins for {winner_score} points")

    if is_infinite:
      mean, stdev = mean_and_stdev(scores)
      print(f"[{bot1} vs {bot2}] cumulative statistics: mean = {mean:+.2f}, stdev = {stdev:.2f}\n")

  return scores

def do_tournament(bots, num_hands=15):
  """ for a list of bots, pit each bot against every other """

  # Pit every bot against each other
  matches = list(it.combinations(bots, 2))
  match_results = { match: compete(*match, num_hands=num_hands)
                    for match
                    in matches }
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
parser.add_argument(
  '-n', '--num_hands', type=int, default=15,
  help='the number of hands of play per match, defaults to 15, 0 means infinite'
)
parser.add_argument(
  '-s', '--style', type=str, default='none',
  help='Choose the style, "tabletop" or "grid" or "none". Default: "none"'
)

if __name__ == '__main__':
  args = parser.parse_args()

  prettify_state = {
    'tabletop': prettify.prettify_state,
    'grid': prettify.prettify_state_table,
    'none': lambda *args, **kwargs: ''
  }[args.style]

  if len(args.bot_names) == 0:
    bot_names = os.listdir('bots/')
    # human doesn't get to be in the tournament
    bot_names = filter(lambda n: n != 'human', bot_names)
  elif len(args.bot_names) == 1:
    print("need to specify two or more bots!")
    sys.exit(1)
  else:
    bot_names = args.bot_names

  bots = []
  for bot_name in bot_names:
    bot_path = Path(f"bots/{bot_name}/{bot_name}.sh")
    if not os.path.exists(bot_path):
      print(f"No known bot named '{bot_name}'.")
      sys.exit(1)
    bots.append(GinBot(bot_name, bot_path))

  do_tournament(bots, num_hands=args.num_hands)
