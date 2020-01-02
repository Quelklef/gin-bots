""" A module for manipulating ascii art """

import itertools as it
import sty

class ColoredText:
  def __init__(self, parts, color):
    self.parts = list(parts)
    self.color = color

  def __str__(self):
    text = ''.join(map(str, self.parts))
    return f"{self.color}{text}{sty.rs.all}"

  def __len__(self):
    return sum(map(len, self.parts))

  def __add__(self, other):
    return ColoredText([self, other], '')

  def __radd__(self, other):
    return ColoredText([other, self], '')

  # == #

  def ljust(self, amt):
    if len(self) < amt:
      new_part = ' ' * (amt - len(self))
      return ColoredText(self.parts + [new_part], self.color)
    else:
      return ColoredText(self.parts, self.color)

  def replace(self, target, replacement):
    part_replace = lambda part: part.replace(target, replacement)
    return ColoredText(map(part_replace, self.parts), self.color)

def paint(text, color):
  return ColoredText([text], color)

class Art:
  def __init__(self, text=None, *, lines=None, color=None):
    assert not (text is not None and lines is not None)

    if text is not None:
      self.lines = text.split('\n')
    else:
      self.lines = list(lines)

    assert len(self.lines) > 0

    if color:
      do_color = lambda line: paint(line, color)
      self.lines = list(map(do_color, self.lines))

    self._pad()

  def _pad(self):
    """ Pad each line to the length of the longest """
    longest_len = max(map(len, self.lines))
    self.lines = [ line.ljust(longest_len) for line in self.lines ]

  def __str__(self):
    return '\n'.join(map(str, self.lines))

  @staticmethod
  def blank(self, *, width, height):
    return Art([' ' * width] * height)

  def colored(self, color):
    paint_line = lambda line: paint(line, color)
    return Art(lines=map(paint_line, self.lines))

  @property
  def height(self):
    return len(self.lines)

  def _taller(self, growth_amount):
    gained_lines = [" " * self.width] * growth_amount
    return Art(lines=self.lines + gained_lines)

  @property
  def width(self):
    return len(self.lines[0])

  def __add__(self, other):
    this = self

    if isinstance(other, str):
      other = Art(other)

    if this.height < other.height:
      this = this._taller(other.height - this.height)
    elif other.height < this.height:
      other = other._taller(this.height - other.height)

    new_lines = [ this_line + other_line for this_line, other_line in zip(this.lines, other.lines) ]
    return Art(lines=new_lines)

  def __radd__(self, other):
    if isinstance(other, str):
      return Art(other) + self

  # == Methods lifted from string == #

  def join(self, others):
    others = list(others)

    if len(others) == 0:
      return Art('')

    result = others[0]
    for other in others[1:]:
      result = result + self + other

    return result

  def replace(self, target, replacement):
    line_replace = lambda line: line.replace(target, replacement)
    return Art(lines=map(line_replace, self.lines))


if __name__ == '__main__':

  # Ascii art adapted from http://patorjk.com/software/taag/#p=display&h=0&f=Big&t=Art

  A = Art(
      "     /\\\n"
      "    /  \\\n"
      "   / /\\ \\\n"
      "  / ____ \\\n"
      " /_/    \\_\\"
  )

  A = A.colored(sty.fg.green)

  # Color can be given by keyword
  R = Art(
    "\n"
    " _ __\n"
    "| '__|\n"
    "| |\n"
    "|_|",
    color=sty.fg.black + sty.bg.white,
  )

  # Alternative initialization
  T = Art(lines=[
    " _",
    "| |_",
    "| __|",
    "| |_",
    " \__|",
  ])

  T = T.colored(sty.ef.bold + sty.fg.red)

  print(A)
  print(R)
  print(T)

  print(A + R + T)

  # Strings may be added
  print("===>" + A + R + T + "<===")
  # This is mostly useful for use like ' '.join(arts)
