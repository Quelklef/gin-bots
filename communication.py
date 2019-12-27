""" This file handles communication with the gin bots.

Communication is done via a file called 'comm.txt' in the same directory as the client script.

The server opens communications by creating comm.txt.
The server sends a message by modifying to comm.txt.
The client responds by modifying comm.txt.
The server closes communications by deleting comm.txt.

Clients are required to respond to messages, but servers are not.

Communication is synchronous/blocking. """

from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


comm_file_name = 'comm.txt'


def comm_loc(client_loc: Path):
  """ Calculate the location of the communication file
  from the location of the client """
  return client_loc.parent.joinpath(comm_file_name)


def send_message(client_loc: Path, message: str):
  """ Send a message (string) to a client.
  Returns the client's response."""
  comm_file_loc = comm_loc(client_loc)

  with open(comm_file_loc, 'w') as f:
    f.write(message)

  # Now wait for response...

  class Handler(FileSystemEventHandler):
    def on_modified(self, event):
      self.stop()

  observer = Observer()
  observer.schedule(Handler(), path=comm_file_loc, recursive=False)
  observer.start()
  observer.join()

  with open(comm_file_loc, 'r') as f:
    return f.read()


def close_comms(client_loc: Path):
  """ Close communications with a client. """
  os.remove(comm_loc(client_loc))
