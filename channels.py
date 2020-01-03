import os
import sys
from pathlib import Path
import subprocess

import logging
import logging.handlers
import traceback as tb

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler('log.log', mode='w', maxBytes=1e5, backupCount=3)
formatter = logging.Formatter("%(name)s [%(levelname)s]: %(message)s")
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)
logger.addHandler(handler)

# log exceptions
def exception_handler(*args):
  logger.exception(''.join(tb.format_exception(*args)))
sys.excepthook = exception_handler

# == #

def generate_random_string(*, length=35):
  # TODO: ensure unique
  return ''.join( str(random.randint(0, 9)) for _ in range(length) ) 

class Channel:
  """
  Two-way synchronous communication between processes.

  For use by a server, who owns the channel, and a client, who does not.

  All channels have an ID which must by system-wide unique.
  If no ID is given when a channel is created, a new ID will be generated.

  For simple communication, a server can create a channel like

    >>> channel = Channel('my channel', id='test', role=Channel.SERVER)

  and begin sending and receiving messages with

    >>> channel.open()
    >>> channel.send('hello client')
    >>> channel.recv()
    'hello server'
    >>> channel.close()

  The client-side code may look like
    >>> channel = Channel('my channel', id='test', role=Channel.CLIENT)
    >>> channel.open()
    >>> channel.recv()
    'hello client'
    >>> channel.send('hello server')
    >>> channel.close()

  """

  # Roles
  CLIENT = 'client'
  SERVER = 'server'

  def __init__(self, name, *, id=None, role, chunk_size=50):
    self.name = name

    self.id = id or generate_random_string()
    self.role = role
    self.chunk_size = chunk_size

    logger.info(f"__init__ for channel {repr(self.name)} with id {repr(self.id)}.")

  def _log(self, msg, *, level=logging.INFO):
    logger.log(level, f"Channel {repr(self.name)}: {msg}")

  def _make_fifo(self, location):
    if os.path.exists(location):
      self._log("Fifo already exists; will override",
                level=logging.WARNING)

      os.remove(location)

    location.parent.mkdir(parents=True, exist_ok=True)

    # Uncomment if you wanna play with someone else on your system
    # os.umask(0o000)
    # os.mkfifo(location, 0o777)
    os.mkfifo(location)

  @property
  def _fifo_in_loc(self):
    if self.role == Channel.SERVER:
      return Path(f"/tmp/gin/channel_to_server_{self.id}.fifo")
    elif self.role == Channel.CLIENT:
      return Path(f"/tmp/gin/channel_to_client_{self.id}.fifo")

  @property
  def _fifo_out_loc(self):
    if self.role == Channel.SERVER:
      return Path(f"/tmp/gin/channel_to_client_{self.id}.fifo")
    elif self.role == Channel.CLIENT:
      return Path(f"/tmp/gin/channel_to_server_{self.id}.fifo")

  def _make_fifos(self):
    self._log("Making fifos")
    self._make_fifo(self._fifo_in_loc)
    self._make_fifo(self._fifo_out_loc)

  def _remove_fifos(self):
    self._log("Destroying fifos")
    os.remove(self._fifo_in_loc)
    os.remove(self._fifo_out_loc)

  def open(self):
    self._log("Opening")

    if self.role == Channel.SERVER:
      self._make_fifos()

    # Don't actually open the fifos yet.
    # The open() call will be blocking, so wait until the first send() or recv()
    self.fifo_in = None
    self.fifo_out = None

    self._fifos_opened = False

  def _ensure_fifos_opened(self):

    if not self._fifos_opened:

      # Reverse the open() order for client/server since we need them
      # to open the same file first
      if self.role == Channel.CLIENT:
        self.fifo_in = open(self._fifo_in_loc, 'r')
        self.fifo_out = open(self._fifo_out_loc, 'w')

      elif self.role == Channel.SERVER:
        self.fifo_out = open(self._fifo_out_loc, 'w')
        self.fifo_in = open(self._fifo_in_loc, 'r')

      self._fifos_opened = True

  def close(self):
    self._log("Closing")

    if self._fifos_opened:
      self.fifo_in.close()
      self.fifo_out.close()

    if self.role == Channel.SERVER:
      self._remove_fifos()

  def __enter__(self):
    self.open()
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.close()

  def send(self, message: str):
    assert isinstance(message, str)
    self._ensure_fifos_opened()

    self._log(f"Delivering '{message}'")

    for chunk, continues in chunk_string(message, self.chunk_size):
      # If the message done, prepend and append a '!' a '!'; else, use a '+'
      marker = '+' if continues else '!'
      self.fifo_out.write(marker + (chunk + marker).ljust(self.chunk_size + 1))

    self.fifo_out.flush()

  def recv(self):
    self._ensure_fifos_opened()

    self._log("Waiting")

    chunks = []
    while True:
      read = self.fifo_in.read(self.chunk_size + 2).strip()

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


