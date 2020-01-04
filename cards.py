
class Card:
  def __init__(self, card):

    suit = card[0]
    rank = card[1:]

    assert rank in 'AXJQKaxjqk' or int(rank) in range(1, 13 + 1)
    assert suit in 'CDHScdhs'

    suit = suit.upper()

    ranks = { 'A': 1, 'X': 10, 'J': 11, 'Q': 12, 'K': 13 }
    rank = ranks.get(rank.upper()) or int(rank)

    self.suit = suit.upper()
    self.rank = rank

  def __repr__(self):
    return f"Card({repr(str(self))})"

  @property
  def sigil(self):
    sigils = { 'C': '♣', 'D': '♦', 'H': '♥', 'S': '♠' }
    return sigils[self.suit]

  @property
  def pretty_rank(self):
    ranks = { 1: 'A', 11: 'J', 12: 'Q', 13: 'K' }
    return ranks.get(self.rank) or str(self.rank)

  def __str__(self):
    return f"{self.suit}{self.pretty_rank}"

  @property
  def value(self):
    # rank-value but face cards are 10
    return min(self.rank, 10)

  def adjacent(self, other):
    """ Are the two cards of the same suit and one different in rank? """
    return self.suit == other.suit and abs(self.rank - other.rank) == 1

  @property
  def _tuple(self):
    return (self.rank, self.suit)

  def __eq__(self, other): return isinstance(other, Card) and self._tuple == other._tuple
  def __ne__(self, other): return not isinstance(other, Card) or self._tuple != other._tuple
  def __lt__(self, other): return self._tuple <  other._tuple
  def __le__(self, other): return self._tuple <= other._tuple
  def __gt__(self, other): return self._tuple >  other._tuple
  def __ge__(self, other): return self._tuple >= other._tuple

  def __hash__(self): return self._tuple.__hash__()


all_cards = frozenset({ Card(f"{suit}{rank}")
                        for suit in 'cdhs'
                        for rank in range(1, 13 + 1) })

def parse_card_is_ok(string):
  try:
    Card(string)
    return True
  except ValueError:
    return False
