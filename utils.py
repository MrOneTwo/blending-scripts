# Put this script in Blender file structure, lib/michal folder. Remember to create
# __init__.py file in that folder.
#
# from importlib import reload
# reload(michal.utils)
#

import bpy
from pathlib import Path

PATH_ROOT = Path(r"C:\Users\mc\Desktop\devil_lady\parts")

RING = {"file": PATH_ROOT / Path("ring.obj"), "mat": "ring", "object_name": "ring"}
HEAD = {"file": PATH_ROOT / Path("head.obj"), "mat": "head", "object_name": "head"}
HAIR_MAIN = {"file": PATH_ROOT / Path("hair_main.obj"), "mat": "hair", "object_name": "hair_main"}
BODY = {"file": PATH_ROOT / Path("body.obj"), "mat": "body", "object_name": "body"}
MOUTH_CHAIN = {"file": PATH_ROOT / Path("mouth_chain.obj"), "mat": "gold", "object_name": "mouth_chain"}


def material_exists(mat: str):
  if mat in bpy.data.materials.keys():
    return bpy.data.materials[mat]
  else:
    return None

def delete_by_name(name: str):
  # TODO(michalc): restore original selection?
  bpy.ops.object.select_all(action='DESELECT')
  try:
    bpy.data.objects[name].select_set(True)
    bpy.ops.object.delete()
  except KeyError:
    print(f"Failed to delete {name}. Not present.")

def import_obj(obj_info):
  # TODO(michalc):
  delete_by_name(obj_info["object_name"])
  status = bpy.ops.import_scene.obj(filepath=str(obj_info["file"]))
  obj_object = bpy.context.selected_objects[0]
  obj_object.name = obj_info["object_name"]
  # TODO(michalc): rename the obj_object.data ... mesh object inside.
  mat_for_object = material_exists(obj_info["mat"])
  print(f"Imported {obj_object.name}, matching material: {mat_for_object}")
  print(obj_object.data)
  print(bpy.context.view_layer.objects.active)

  if mat_for_object:
    obj_object.data.materials[0] = mat_for_object

def get_objects():
  print(bpy.data.objects.keys())
  print(bpy.data.objects.items())
  print(bpy.data.objects.values())

  imported_object = bpy.ops.import_scene.obj(filepath=str(PATH_ROOT / Path("ring.obj")))
  obj_object = bpy.context.selected_objects[0]
  print('Imported name: ', obj_object.name)
  print(bpy.data.materials.keys())