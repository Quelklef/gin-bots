
class Card:
  def __init__(self, suit, rank):
    """
    Suit is either 'clubs', 'diamonds', 'hearts', or 'spades', case-insensitive

    Ranks are:
      'A' or 'a' or 1 for ace;
      2-10 for 2-10;
      'J' or 'j' or 11 for Jack;
      'Q' or 'q' or 12 for Queen;
      'K' or 'k' or 13 for King;
    """

    if not isinstance(suit, str) or suit.lower() not in ['clubs', 'diamonds', 'hearts', 'spades']:
      raise ValueError(f"suit must be 'clubs', 'diamonds', 'hearts', or 'spades', not {repr(suit)}")
    if rank not in range(1, 15) and rank not in 'AJQKajqk':
      raise ValueError(f"rank must be from 1 through 14 (inclusive) or one of 'AJQK' or 'ajqk', not {repr(rank)}")

    self.suit = suit.lower()

    if isinstance(rank, int):
      self.rank = rank
    else:
      self.rank = {
        'A': 1,
        'J': 11,
        'Q': 12,
        'K': 13,
      }[rank.lower()]


  def __repr__(self):
    return f"Card({repr(self.suit)}, {repr(self.rank)})"


  @property
  def as_unicode(self):
    ace = {
      'clubs': 0x1f0d1,
      'diamonds': 0x1f0c1,
      'hearts': 0x1f0b1,
      'spades': 0x1f0a1,
    }[self.suit]
    codepoint = ace + (self.rank - 1)
    return chr(codepoint)


  def __str__(self):
    return self.as_unicode


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
              for rank in range(1, 14 + 1) }


a_hand = frozenset({
  Card('spades', 3),
  Card('diamonds', 3),
  Card('hearts', 3),

  Card('spades', 10),
  Card('spades', 11),
})
