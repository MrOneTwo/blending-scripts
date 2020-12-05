import xmlrpc.client

HOST = "127.0.0.1"
PORT = 8000

client = None

def start():
  global client
  client = xmlrpc.client.ServerProxy(f"http://{HOST}:{PORT}")
  if client is None:
    print("Client failed to connect... ")
  else:
    print(f"Client: {client}")


