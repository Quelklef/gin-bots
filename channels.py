import os
import sys
from pathlib import Path
import subprocess

import logging
import traceback as tb

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler('log.log', mode='w')
formatter = logging.Formatter("%(name)s [%(levelname)s]: %(message)s")
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)
logger.addHandler(handler)

# log exceptions
def exception_handler(*args):
  logger.exception(''.join(tb.format_exception(*args)))
sys.excepthook = exception_handler

# Communication between server and client emulates synchronocity
# It's implemented with two channels, one client -> server and one server -> client
# The server sends messages then waits for a response
# The server is responsible for starting the client

# TODO: processes need to fail gracefully when a process that they rely on fails.
#       currently, if a client or server fails, the other will too, but it will do
#       so by reading '' as a message and that will cause an error.

class Channel:
  def __init__(self, name, location, mode, *, msg_size=50):
    self.name = name
    self.location = location
    self.mode = mode
    self.msg_size = msg_size

    logger.info(f"__init__ for channel '{self.name}' at '{self.location}'.")

  def _log(self, msg):
    logger.info(f"Channel {repr(self.name)}: {msg}")

  def make_fifo(self):
    self._log("Making fifo")

    if os.path.exists(self.location):
      self._log("Fifo already existed; will override")
      os.remove(self.location)

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
    self.fifo.write(message.ljust(self.msg_size))
    self.fifo.flush()

  def recv(self):
    self._log("Waiting")
    message = self.fifo.read(self.msg_size).strip()
    self._log(f"Received '{message}'")
    return message
