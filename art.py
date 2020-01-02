""" A module for manipulating ascii art """

import itertools as it
import sty

class Art:
  def __init__(self, text=None, *, lines=None, color=''):
    if text is not None: assert text != ''
    if lines is not None: assert lines != []
    assert not (text is not None and lines is not None)

    if text is not None:
      self.lines = text.split('\n')
    elif lines is not None:
      self.lines = lines

    self._pad()

    self.color = color

  def _pad(self):
    """ Pad each line to the length of the longest """
    longest_len = max(map(len, self.lines))
    self.lines = [ line.ljust(longest_len) for line in self.lines ]

  def __str__(self):
    colored_lines = [ f"{self.color}{line}{sty.rs.all}" for line in self.lines ]
    return '\n'.join(colored_lines)

  @staticmethod
  def blank(self, *, width, height):
    return Art([' ' * width] * height)

  def colored(self, color):
    return Art(lines=self.lines, color=self.color + color)

  @property
  def height(self):
    return len(self.lines)

  def _taller(self, growth_amount):
    gained_lines = [" " * self.width] * growth_amount
    return Art(lines=self.lines + gained_lines, color=self.color)

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
    return Art(lines=new_lines, color=other.color)

  def __radd__(self, other):
    if isinstance(other, str):
      return Art(other) + self

  # == Methods lifted from string == #

  def replace(self, target, replacement):
    return Art(
      lines=list(map(lambda line: line.replace(target, replacement), self.lines)),
      color=self.color,
    )


if __name__ == '__main__':

  # Ascii art adapted from http://patorjk.com/software/taag/#p=display&h=0&f=Big&t=Art

  A = Art(
      "     /\\\n"
      "    /  \\\n"
      "   / /\\ \\\n"
      "  / ____ \\\n"
      " /_/    \\_\\"
  )

  A = A.colored(sty.fg.li_red)

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

  T = T.colored(sty.ef.bold + sty.fg.li_blue)

  print(A)
  print(R)
  print(T)

  # Addition inherits color of last element
  print(A + R + T)

  # Strings may be added
  print("===>" + A + R + T + "<===")
  # This is mostly useful for use like ' '.join(arts)
