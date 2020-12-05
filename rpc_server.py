import threading
import bpy
from xmlrpc.server import SimpleXMLRPCServer


HOST = "127.0.0.1"
PORT = 8000


def maybe_launch_server():
  server = SimpleXMLRPCServer((HOST, PORT))
  #server.register_introspection_functions()
  server.register_function(list_objects)
  server.register_function(import_obj)
  server.serve_forever()


def rpc():
  t = threading.Thread(target=maybe_launch_server)
  t.daemon = True
  t.start()


def list_objects():
  return bpy.data.objects.keys()


def import_obj(path: str):
  status = bpy.ops.import_scene.obj(filepath=path)
  return 'OK'
