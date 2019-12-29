
class Card:
  def __init__(self, card):

    suit = card[0].lower()
    rank = int(card[1:])

    assert rank in range(1, 13 + 1)
    assert suit in 'cdhs'

    self.suit = suit.lower()
    self.rank = rank

  def __repr__(self):
    return f"Card({repr(str(self))})"

  def __str__(self):
    return f"{self.suit.upper()}{str(self.rank).zfill(2)}"

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


all_cards = { Card(f"{suit}{rank}")
              for suit in 'cdhs'
              for rank in range(1, 13 + 1) }
