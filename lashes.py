# This script generates eye lashes based on two guides. It uses NURBS curves for
# the lashes.
#
# from michal import lashes
# lashes.create_lash("lash_bot_guide", "lash_top_guide")

import bpy
import random
import math


class BlackHole():
    """ This class is used to attract objects to simulate clumping."""
    def __init__(self, pos: list, radius: float):
        self.pos = pos
        self.radius = radius


def points_distance(p1: list, p2:list):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    dz = p1[2] - p2[2]
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def attract(blackhole: BlackHole, point: list, strength: float):
    """ This is basically lerping function... """

    # Vector pointing from the point to the black hole.
    dx = -point[0] + blackhole.pos[0]
    dy = -point[1] + blackhole.pos[1]
    dz = -point[2] + blackhole.pos[2]

    _x = dx * strength + point[0]
    _y = dy * strength + point[1]
    _z = dz * strength + point[2]

    return (_x, _y, _z)


def find_closest_blackhole(blackholes: list, point: list):
    distances = []
    for h in blackholes:
        distances.append(points_distance(h.pos, point))
    return blackholes[distances.index(min(distances))]


def create_curve(name: str, points: list, radiuses: list=None, target_collection: str="Collection", bevel_depth: float=0.0):
    assert len(points) > 1
    _points = points

    _radiuses = radiuses
    if radiuses == None:
        _radiuses = [1.0] * len(_points)

    d_crv = bpy.data.curves.new(f'd_{name}', 'CURVE')
    d_crv.dimensions = '3D'
    d_crv.resolution_u = 4
    d_crv.bevel_depth = bevel_depth
    d_crv.bevel_resolution = 4

    # Map point coordinates to spline.
    spline = d_crv.splines.new(type='NURBS')

    # Spline is created with one point already so allocate one less.
    spline.points.add(len(_points) - 1)
    # Modify the points of the spline.
    for i, point in enumerate(_points):
        x,y,z = point
        spline.points[i].co = (x, y, z, 1)
    spline.use_endpoint_u = True
    spline.use_endpoint_v = True
    spline.points.foreach_set("radius", _radiuses)

    obj = bpy.data.objects.new(name, d_crv)
    bpy.data.collections[target_collection].objects.link(obj)
    return obj


def get_curve_points(name: str):
    # Convert the curve to mesh to get the vertices but don't add that mesh to
    # the scene since it's temporary.
    curve_obj = bpy.data.objects[name]
    _curve_mesh = curve_obj.to_mesh()
    curve_mesh_obj = bpy.data.objects.new("delete_me", _curve_mesh.copy())
    return [(v.co.x, v.co.y, v.co.z) for v in curve_mesh_obj.data.vertices]


def create_lash(guide_bot_name: str, guide_top_name: str, thickness: float=0.01):
    try:
        bpy.data.collections["eyelashes_generated"]
    except KeyError:
        bpy.data.collections.new("eyelashes_generated")
        bpy.context.scene.collection.children.link(bpy.data.collections["eyelashes_generated"])

    root_points = get_curve_points(guide_bot_name)
    tip_points = get_curve_points(guide_top_name)
    # Those probably won't be the same vertices count with current approach.
    tip_points = tip_points[:len(root_points)]

    #
    # NUDGE THE ROOT POINTS A BIT
    #

    # Add some noise to the roots position.
    # TODO(michalc): restrict the movement to the axis that make sense.
    root_points_with_noise = []
    for i, p in enumerate(root_points):
        nudged_point = list(p)
        nudged_point[0] = p[0] + (0.05 * points_distance(p, tip_points[i])) * random.random()
        nudged_point[1] = p[1] + (0.05 * points_distance(p, tip_points[i])) * random.random()
        nudged_point[2] = p[2] + (0.05 * points_distance(p, tip_points[i])) * random.random()
        root_points_with_noise.append(nudged_point)

    root_points = root_points_with_noise

    #
    # CLUMP THE TIP POINTS A BIT
    #

    clumping = True
    blackholes = []
    blackholes_radius = 0.002
    if clumping:
        for i, p in enumerate(tip_points):
            # TODO(michalc): control this chance somewhere
            if i % 3 == 0:
                blackholes.append(BlackHole(p, blackholes_radius))

        top_points_magnetized = []
        for p in tip_points:
            attractor = find_closest_blackhole(blackholes, p)
            top_points_magnetized.append(attract(attractor, p, 0.8))

        tip_points = top_points_magnetized

    #
    # DEBUG - DRAW BLACKHOLES
    #

    DRAW_BLACKHOLES = False
    if DRAW_BLACKHOLES:
        for bh in blackholes:
            bpy.ops.mesh.primitive_ico_sphere_add(location=bh.pos, radius=blackholes_radius)

    #
    # NUDGE THE TIP POINTS A BIT
    #

    # Add some noise to the roots position.
    # TODO(michalc): restrict the movement to the axis that make sense.
    tip_points_with_noise = []
    for i, p in enumerate(tip_points):
        nudged_point = list(p)
        nudged_point[0] = p[0] + (0.05 * points_distance(p, root_points[i])) * random.random()
        nudged_point[1] = p[1] + (0.05 * points_distance(p, root_points[i])) * random.random()
        nudged_point[2] = p[2] + (0.05 * points_distance(p, root_points[i])) * random.random()
        tip_points_with_noise.append(nudged_point)

    tip_points = tip_points_with_noise

    #
    # ADD MIDPOINTS TO CONTROL THE CURVATURE
    #

    mid_points = []
    for i in range(len(tip_points)):
        x = (tip_points[i][0] + root_points[i][0]) / 2
        y = (tip_points[i][1] + root_points[i][1]) / 2
        z = (tip_points[i][2] + root_points[i][2]) / 2
        mid_points.append((x,y,z))


    lashes_objects = []
    for i, lash_points in enumerate(zip(root_points, mid_points, tip_points)):
        lashes_objects.append(create_curve(f"eyelash.{i:03}", lash_points, (0.05, 0.02, 0), "eyelashes_generated", thickness))

    #
    # MERGE LASHES INTO ONE OBJECT FOR EASIER EDITING
    #

    MERGE_LASHES = True
    if MERGE_LASHES:
        bpy.ops.object.select_all(action='DESELECT')
        for o in lashes_objects:
            o.select_set(True)
        bpy.context.view_layer.objects.active = lashes_objects[0]
        bpy.ops.object.join()


#create_lash("lash_guide_bot", "lash_guide_top", 0.01)
