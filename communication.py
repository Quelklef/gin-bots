import os
from pathlib import Path
import subprocess

def to_client(client_location: Path, args):
  comm_loc = client_location.parent.joinpath('comm.txt')
  payload = '\n'.join(args)

  with open(comm_loc, 'w') as f:
    f.write(payload)

  status = subprocess.run(['sh', client_location.name], cwd=client_location.parent)

  if status.returncode != 0:
    raise Exception(f"Client at {client_location} exited with status code {status.returncode}.")

  with open(comm_loc, 'r') as f:
    response = f.read()

  os.remove(comm_loc)

  return response
