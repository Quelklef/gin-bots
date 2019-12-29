from cards import Card

def parse(string):
  return {*map(Card, string.split(','))}

test_hand1 = parse("H7,C2,S4,H2,H1,S2,C7,H3,H9,D7")
test_hand2 = parse("S1,S2,S3,D4,D5,H7,S7,C9,D9,H9")
test_hand3 = parse("SA,C2,C3,C4,S4,H6,S8,C8,C9,S9")
# starting hand, 11 cards
test_hand4 = parse("SA,D3,D4,C5,D6,D7,H8,H9,DQ,HQ,HK")
test_hand5 = parse("D3,D4,D6,D7,H8,H9,DQ,HQ,HK,DK")
