import random

def agent(hand, stack, history):
  """ play some gin """

  if len(hand) == 10:
    # Need to choose where to draw from

    if len(stack) == 0:
      return 'deck'
    else:
      return random.choice(['deck', 'stack'])

  else:

    if random.random() < 0.1:
      return 'end'

    # Need to choose what card to discard
    return random.choice(hand)


if __name__ == '__main__':
  with open('comm.txt', 'r') as f:
    lines = f.read()

  hand, stack, history = lines.split('\n')

  hand    = [] if not hand    else hand   .split(',')
  stack   = [] if not stack   else stack  .split(',')
  history = [] if not history else history.split(',')

  result = agent(hand, stack, history)

  with open('comm.txt', 'w') as f:
    f.write(result)
