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

msg_size = 50

def calc_to_client_loc(client_location: Path):
  return client_location.parent.joinpath('to_client.fifo')

def calc_to_server_loc(client_location: Path):
  return client_location.parent.joinpath('to_server.fifo')

def open_comms(client_location: Path):

  logger.info(f"SERVER OPENING COMMUNICATIONS WITH {client_location.parent.name}")

  # Set up communication channels

  to_client_loc = calc_to_client_loc(client_location)
  to_server_loc = calc_to_server_loc(client_location)

  if os.path.exists(to_client_loc):
    os.remove(to_client_loc)
  if os.path.exists(to_server_loc):
    os.remove(to_server_loc)

  os.mkfifo(to_client_loc)
  os.mkfifo(to_server_loc)

  # Start client

  subprocess.Popen(
    ['sh', client_location.name],
    cwd=client_location.parent,
    stdout=sys.stdout,
  )

  # Bind to channels

  fifo_out = open(to_client_loc, 'w')
  fifo_in = open(to_server_loc, 'r')

  return (fifo_in, fifo_out)

def close_comms(fifo_in, fifo_out):

  logger.info(f"SERVER CLOSING COMMUNICATIONS WITH {Path(fifo_in.name).parent.name}")

  # Close communication channels

  fifo_in.close()
  fifo_out.close()

  os.remove(fifo_in.name)
  os.remove(fifo_out.name)

def send_to_client(fifo_in, fifo_out, message: str):
  assert(len(message) <= msg_size)
  assert(isinstance(message, str))

  client_name = Path(fifo_in.name).parent.name  # REMOVE
  logger.info(f"SERVER SENDING TO {client_name}: {repr(message)}")

  padded = message.ljust(msg_size)
  fifo_out.write(padded)
  fifo_out.flush()

def receive_from_client(fifo_in, fifo_out):
  client_name = Path(fifo_in.name).parent.name  # REMOVE
  logger.info(f"SERVER WAITING FOR RESPONSE FROM {client_name}")
  response = fifo_in.read(msg_size).strip()
  logger.info(f"SERVER READ FROM {client_name}: {repr(response)}")
  return response
