import os
import sys
from pathlib import Path
import subprocess

import logging
import logging.handlers
import traceback as tb

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

"""
handler = logging.handlers.RotatingFileHandler('log.log', mode='w', maxBytes=1e5, backupCount=3)
formatter = logging.Formatter("%(name)s [%(levelname)s]: %(message)s")
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)
logger.addHandler(handler)

# log exceptions
def exception_handler(*args):
  logger.exception(''.join(tb.format_exception(*args)))
sys.excepthook = exception_handler
"""

# Communication between server and client emulates synchronocity
# It's implemented with two channels, one client -> server and one server -> client
# The server sends messages then waits for a response
# The server is responsible for starting the client

class Channel:
  def __init__(self, name, location, mode, *, chunk_size=50):
    self.name = name
    self.location = Path(location)
    self.mode = mode
    self.chunk_size = chunk_size

    logger.info(f"__init__ for channel '{self.name}' at '{self.location}'.")

  def _log(self, msg, *, level=logging.INFO):
    logger.log(level, f"Channel {repr(self.name)}: {msg}")

  def make_fifo(self):
    self._log("Making fifo")

    if os.path.exists(self.location):
      self._log("Fifo already existed; will override",
                level=logging.WARNING)
      os.remove(self.location)

    self.location.parent.mkdir(parents=True, exist_ok=True)

    # Uncomment if you wanna play with someone else on your system
    # os.umask(0o000)
    # os.mkfifo(self.location, 0o777)
    os.mkfifo(self.location)

  def remove_fifo(self):
    self._log("Destroying fifo")
    assert os.path.exists(self.location)
    os.remove(self.location)

  def open(self):
    self._log("Opening")
    self.fifo = open(self.location, self.mode)

  def __enter__(self):
    self.open()
    return self

  def close(self):
    self._log("Closing")
    self.fifo.close()

  def __exit__(self, exc_type, exc_value, traceback):
    self.close()

  def send(self, message: str):
    assert isinstance(message, str)

    self._log(f"Delivering '{message}'")

    for chunk, continues in chunk_string(message, self.chunk_size):
      # If the message done, prepend and append a '!' a '!'; else, use a '+'
      marker = '+' if continues else '!'
      self.fifo.write(marker + (chunk + marker).ljust(self.chunk_size + 1))

    self.fifo.flush()

  def recv(self):
    self._log("Waiting")

    chunks = []
    while True:
      read = self.fifo.read(self.chunk_size + 2).strip()

      if read == '':
        self._log("Empty read, meaning the other end of the channel crashed",
                  level=logging.ERROR)
        assert False, "Empty read"

      marker = read[0]
      completed = { '!': True, '+': False }[marker]

      if completed:
        i = read.rindex('!')
        chunk = read[1:i]
      else:
        chunk = read[1:-1]

      chunks.append(chunk)

      if completed:
        break

    message = ''.join(chunks)

    self._log(f"Received '{message}'")

    return message

def chunk_string(string, chunk_size):
  """ yield `chunk_size` characters at a time and a boolean noting whether or not there's more to come.
  chunk_iter("12345678", 3) --> ("123", True), ("456", True), ("78", False) """

  while True:
    chunk = string[:chunk_size]
    string = string[chunk_size:]

    continues = string != ''
    yield (chunk, continues)

    if not continues:
      break


