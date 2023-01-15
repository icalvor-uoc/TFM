import uuid

def getuuid():
  return str(uuid.uuid4())
  
def get_uri(subgraph='r'):
  return f'http://app.internal/{subgraph}/{getuuid()}'