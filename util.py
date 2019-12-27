import itertools

def powerset(iterable):
    # https://docs.python.org/3.6/library/itertools.html#itertools-recipes
  "powerset([1,2,3]) -> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
  s = list(iterable)
  return itertools.chain.from_iterable(
    itertools.combinations(s, r) for r in range(len(s)+1))

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

def flatten(list_of_lists):
  "Flatten one level of nesting"
  return itertools.chain.from_iterable(list_of_lists)

def union(xs, start=None):
  result = start if start is not None else set()
  for x in xs:
    result |= x
  return result
