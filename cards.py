
class Card:
  def __init__(self, suit, rank):
    self.suit = {
      'c': 'clubs',
      'd': 'diamonds',
      'h': 'hearts',
      's': 'spades',
    }[suit.lower()[0]]

    if isinstance(rank, str):
      if rank.lower() in 'ajqk':
        self.rank = {
          'a': 1,
          'j': 11,
          'q': 12,
          'k': 13,
        }[rank.lower()]
      else:
        self.rank = int(rank)
    else:
      self.rank = rank

  def __repr__(self):
    return f"Card({repr(self.suit)}, {repr(self.rank)})"

  def __str__(self):
    suit = {
      'clubs': "C",
      'diamonds': "D",
      'hearts': "H",
      'spades': "S",
    }[self.suit]

    ranks = {
      1: 'A',
      11: 'J',
      12: 'Q',
      13: 'K',
    }

    rank = ranks[self.rank] if self.rank in ranks else str(self.rank)

    return rank + suit

  @property
  def value(self):
    # rank-value but face cards are 10
    return min(self.rank, 10)

  def adjacent(self, other):
    """ Are the two cards of the same suit and one different in rank? """
    return self.suit == other.suit and abs(self.rank - other.rank) == 1

  @property
  def _tuple(self):
    return (self.suit, self.rank)

  def __eq__(self, other): return self._tuple == other._tuple
  def __ne__(self, other): return self._tuple != other._tuple
  def __lt__(self, other): return self._tuple <  other._tuple
  def __le__(self, other): return self._tuple <= other._tuple
  def __gt__(self, other): return self._tuple >  other._tuple
  def __ge__(self, other): return self._tuple >= other._tuple

  def __hash__(self): return self._tuple.__hash__()


all_cards = { Card(suit, rank)
              for suit in ['clubs', 'hearts', 'diamonds', 'spades']
              for rank in range(1, 13 + 1) }
