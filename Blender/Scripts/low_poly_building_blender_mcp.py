# Low-poly 3-story building (corrected version).
# Blender 4.2+ / 5.x  (bpy)
#
# Usage:
#   1. Open Blender > Scripting > Text Editor.
#   2. Open this file and press Run Script.
#   3. The script clears the current scene and builds the complete model.

import bpy
import math
from mathutils import Vector

# ============================================================
# CONFIGURATION
# ============================================================

BUILDING_W = 8.0
BUILDING_D = 6.0
FLOORS = 3
FLOOR_H = 3.25
WALL_H = 3.0
WALL_Z0 = 0.35

WINDOW_W = 1.15
WINDOW_H = 1.65
WINDOW_CZ = 1.60          # window centre above each floor's base (keeps frames clear of dentils)

ADD_SIGN = False          # optional "APARTMENTS" sign on the roof access room
SAVE_BLEND = False        # set True to save the scene next to the current .blend

# Filled in by build() AFTER the scene is cleared (see notes: creating them
# before clear_scene() got them deleted).
M = {}      # materials
COLS = {}   # collections


# ============================================================
# SCENE / COLLECTION / MATERIAL SETUP
# ============================================================

def clear_scene():
    """Remove everything using the data API (no operator/context needed)."""
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for block in (bpy.data.meshes, bpy.data.curves, bpy.data.materials,
                  bpy.data.cameras, bpy.data.lights):
        for b in list(block):
            if b.users == 0:
                block.remove(b)


def init_collections():
    for name in ("BUILDING", "WINDOWS", "BALCONIES", "FIRE_ESCAPE", "ROOF", "LIGHTS"):
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
        COLS[name] = c


def make_material(name, color, roughness=0.7, metallic=0.0,
                  emission=None, emission_strength=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    if m.node_tree is None:          # Blender < 5.0 needs use_nodes; 5.0+ always has a tree
        m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        if emission is not None:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission_strength
    return m


def init_materials():
    M["yellow"] = make_material("Wall_Yellow", (0.70, 0.46, 0.035), 0.78)
    M["white"] = make_material("Cornice_White", (0.82, 0.82, 0.77), 0.65)
    M["dark"] = make_material("Iron_Dark", (0.075, 0.085, 0.095), 0.65, 0.05)
    M["dark2"] = make_material("Iron_Dark2", (0.12, 0.13, 0.14), 0.72)
    M["glass"] = make_material("Window_Glass", (0.65, 0.82, 0.85), 0.18)
    M["door"] = make_material("Door_Red", (0.34, 0.055, 0.045), 0.72)
    M["frame"] = make_material("Window_Frame", (0.23, 0.20, 0.14), 0.72)
    M["lit"] = make_material("Window_Lit", (1.0, 0.78, 0.38), 0.30,
                             emission=(1.0, 0.72, 0.30), emission_strength=0.8)
    M["roof"] = make_material("Roof", (0.16, 0.17, 0.18), 0.82)
    M["ground"] = make_material("Ground", (0.055, 0.06, 0.065), 0.95)


# ============================================================
# PRIMITIVE HELPERS (data API only - fast and context independent)
# ============================================================

CUBE_FACES = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
              (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]


def _finish(name, mesh, loc, material, bevel, coll, min_dim=1.0):
    obj = bpy.data.objects.new(name, mesh)
    obj.location = Vector(loc)
    COLS[coll].objects.link(obj)
    if material:
        mesh.materials.append(material)
    if bevel > 0:
        mod = obj.modifiers.new("Small_Bevel", 'BEVEL')
        mod.width = min(bevel, min_dim * 0.4)
        mod.segments = 1
    return obj


def cube(name, loc, size, material=None, bevel=0.0, coll="BUILDING"):
    """Box centred on `loc` with full dimensions `size` = (x, y, z)."""
    hx, hy, hz = size[0] / 2, size[1] / 2, size[2] / 2
    verts = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
             (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], CUBE_FACES)
    me.update()
    return _finish(name, me, loc, material, bevel, coll, min(size))


def cylinder(name, loc, radius, depth, material, vertices=8, rotation=None, coll="BUILDING"):
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=vertices,
                          radius1=radius, radius2=radius, depth=depth)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = _finish(name, me, loc, material, 0.0, coll)
    if rotation:
        obj.rotation_euler = rotation
    return obj


def beam_between(name, a, b, thickness, material, coll="BUILDING"):
    a, b = Vector(a), Vector(b)
    d = b - a
    o = cube(name, (a + b) / 2, (thickness, thickness, d.length), material, 0.02, coll)
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    return o


def add_text(name, text, loc, size, material, rotation=(math.pi / 2, 0, 0), coll="ROOF"):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body = text
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.size = size
    curve.extrude = 0.015
    curve.materials.append(material)
    obj = bpy.data.objects.new(name, curve)
    obj.location = Vector(loc)
    obj.rotation_euler = rotation
    COLS[coll].objects.link(obj)
    return obj


def floor_z(f):
    """Z of the base of floor f (0-based)."""
    return WALL_Z0 + f * FLOOR_H


CORNICE_TOP = floor_z(FLOORS - 1) + WALL_H + 0.04 + 0.11   # top of the last cornice band
ROOF_Z = CORNICE_TOP + 0.125                                 # centre of the 0.25 roof slab
ROOF_TOP = ROOF_Z + 0.125


# ============================================================
# BUILDING CORE
# ============================================================

def build_ground():
    cube("Ground", (0, 0, -0.175), (20, 18, 0.35), M["ground"], 0.05)
    cube("Front_Pavement", (0, -5.4, 0.03), (12, 4.0, 0.06), M["dark2"], 0.03)
    # Plinth closes the gap between the ground and the first floor.
    cube("Plinth", (0, 0, WALL_Z0 / 2 + 0.01),
         (BUILDING_W + 0.30, BUILDING_D + 0.30, WALL_Z0 + 0.02), M["dark"], 0.03)


def build_walls():
    for f in range(FLOORS):
        base = floor_z(f)
        z = base + WALL_H / 2

        cube(f"Wall_F{f+1}_Front", (0, -BUILDING_D / 2, z), (BUILDING_W, 0.30, WALL_H), M["yellow"], 0.04)
        cube(f"Wall_F{f+1}_Back", (0, BUILDING_D / 2, z), (BUILDING_W, 0.30, WALL_H), M["yellow"], 0.04)
        cube(f"Wall_F{f+1}_Left", (-BUILDING_W / 2, 0, z), (0.30, BUILDING_D, WALL_H), M["yellow"], 0.04)
        cube(f"Wall_F{f+1}_Right", (BUILDING_W / 2, 0, z), (0.30, BUILDING_D, WALL_H), M["yellow"], 0.04)

        # White cornice band / floor slab.
        cube(f"Cornice_F{f+1}", (0, 0, base + WALL_H + 0.04),
             (BUILDING_W + 0.55, BUILDING_D + 0.55, 0.22), M["white"], 0.035)

        # Dark strip at the base of each floor.
        cube(f"Foundation_F{f+1}", (0, 0, base - 0.05),
             (BUILDING_W + 0.35, BUILDING_D + 0.35, 0.22), M["dark"], 0.03)


def build_decorative_cornice():
    for f in range(FLOORS):
        z = floor_z(f) + WALL_H - 0.20

        for y in (-BUILDING_D / 2 - 0.18, BUILDING_D / 2 + 0.18):
            for i in range(14):
                x = -BUILDING_W / 2 + 0.35 + i * (BUILDING_W - 0.7) / 13
                cube(f"F{f+1}_Dentil_FB_{i}", (x, y, z), (0.28, 0.24, 0.45), M["white"], 0.015)

        for x in (-BUILDING_W / 2 - 0.18, BUILDING_W / 2 + 0.18):
            for i in range(10):
                y = -BUILDING_D / 2 + 0.30 + i * (BUILDING_D - 0.60) / 9
                cube(f"F{f+1}_Dentil_Side_{i}", (x, y, z), (0.24, 0.28, 0.45), M["white"], 0.015)


# ============================================================
# WINDOWS
# ============================================================

def build_window(name, cx, cy, z, facing):
    """(cx, cy) is the point on the OUTER wall face. One generic routine for all four sides."""
    out = {"front": (0, -1), "back": (0, 1), "left": (-1, 0), "right": (1, 0)}[facing]
    along = (1, 0) if facing in ("front", "back") else (0, 1)
    fb = facing in ("front", "back")

    def part(suffix, u, v, w, d, h, dz, material, bevel):
        px = cx + along[0] * u + out[0] * v
        py = cy + along[1] * u + out[1] * v
        size = (w, d, h) if fb else (d, w, h)
        cube(f"{name}_{suffix}", (px, py, z + dz), size, material, bevel, "WINDOWS")

    part("Glass", 0, 0.02, WINDOW_W, 0.12, WINDOW_H, 0, M["lit"], 0.015)

    for s in (-1, 1):
        part("FrameV", s * (WINDOW_W / 2 + 0.075), 0.02, 0.13, 0.20, WINDOW_H + 0.18, 0, M["frame"], 0.02)
        part("FrameH", 0, 0.02, WINDOW_W + 0.28, 0.20, 0.13, s * (WINDOW_H / 2 + 0.075), M["frame"], 0.02)

    for u in (-0.22, 0.22):
        part("MullionV", u, 0.035, 0.055, 0.22, WINDOW_H, 0, M["frame"], 0.01)
    for dz in (-0.30, 0.0, 0.30):
        part("MullionH", 0, 0.035, WINDOW_W, 0.22, 0.055, dz, M["frame"], 0.01)

    part("Sill", 0, 0.07, WINDOW_W + 0.35, 0.32, 0.13, -WINDOW_H / 2 - 0.14, M["white"], 0.02)


def build_windows():
    x_positions = (-2.65, 0.0, 2.65)
    y_positions = (-1.75, 0.0, 1.75)
    fy = BUILDING_D / 2 + 0.15
    fx = BUILDING_W / 2 + 0.15

    for f in range(FLOORS):
        z = floor_z(f) + WINDOW_CZ

        for i, x in enumerate(x_positions):
            if f == 0 and i == 0:
                continue                      # door position
            build_window(f"Front_F{f+1}_{i+1}", x, -fy, z, "front")
            
        for i, x in enumerate(x_positions):
            build_window(f"Back_F{f+1}_{i+1}", x, fy, z, "back")

        for i, y in enumerate(y_positions):
            build_window(f"Left_F{f+1}_{i+1}", -fx, y, z, "left")
            build_window(f"Right_F{f+1}_{i+1}", fx, y, z, "right")


def build_front_door():
    x = -2.65
    y = -BUILDING_D / 2 - 0.18
    door_h = 2.15
    z = WALL_Z0 + door_h / 2 + 0.02

    cube("Main_Door", (x, y, z), (1.05, 0.22, door_h), M["door"], 0.04, "WINDOWS")
    cube("Door_Frame_L", (x - 0.60, y, z + 0.10), (0.14, 0.28, door_h + 0.2), M["frame"], 0.02, "WINDOWS")
    cube("Door_Frame_R", (x + 0.60, y, z + 0.10), (0.14, 0.28, door_h + 0.2), M["frame"], 0.02, "WINDOWS")
    cube("Door_Lintel", (x, y, z + door_h / 2 + 0.12), (1.34, 0.28, 0.14), M["frame"], 0.02, "WINDOWS")
    cube("Door_Step", (x, y - 0.45, 0.18), (1.7, 0.8, 0.36), M["dark2"], 0.02, "WINDOWS")

    cylinder("Door_Handle", (x + 0.31, y - 0.15, WALL_Z0 + 1.0), 0.055, 0.08, M["white"], 8,
             rotation=(math.pi / 2, 0, 0), coll="WINDOWS")


# ============================================================
# RAILINGS (now take a centre so they sit where the balcony is)
# ============================================================

def _rail_posts(prefix, a, b, z, height, coll):
    a, b = Vector(a), Vector(b)
    beam_between(prefix + "_Top", a + Vector((0, 0, height)), b + Vector((0, 0, height)), 0.12, M["dark"], coll)
    beam_between(prefix + "_Bottom", a, b, 0.10, M["dark"], coll)
    length = (b - a).length
    count = max(2, int(length / 0.38))
    for i in range(count + 1):
        p = a.lerp(b, i / count)
        beam_between(prefix + f"_Post_{i}", p, p + Vector((0, 0, height)), 0.075, M["dark"], coll)


def railing_x(prefix, cx, y, z, width, height=1.0, coll="BALCONIES"):
    """Railing running along X, centred on x = cx. `z` is the walking surface."""
    _rail_posts(prefix, (cx - width / 2, y, z), (cx + width / 2, y, z), z, height, coll)


def railing_y(prefix, x, cy, z, depth, height=1.0, coll="BALCONIES"):
    """Railing running along Y, centred on y = cy. `z` is the walking surface."""
    _rail_posts(prefix, (x, cy - depth / 2, z), (x, cy + depth / 2, z), z, height, coll)


# ============================================================
# BALCONIES
# ============================================================

def build_balcony(side="left", floor=1):
    sgn = 1 if side == "right" else -1
    z = floor_z(floor) + 0.25
    x = sgn * (BUILDING_W / 2 + 1.25)
    y = 0.55
    top = z + 0.09
    name = f"Balcony_{side}_F{floor+1}"

    cube(f"{name}_Platform", (x, y, z), (2.45, 3.15, 0.18), M["dark2"], 0.03, "BALCONIES")

    # Brackets: low on the wall, rising to the outer edge of the platform.
    for yy in (y - 1.0, y + 1.0):
        beam_between(f"{name}_Bracket",
                     (sgn * (BUILDING_W / 2 + 0.15), yy, z - 0.85),
                     (x + sgn * 1.0, yy, z - 0.10),
                     0.13, M["dark"], "BALCONIES")

    railing_x(f"{name}_Front", x, y - 1.52, top, 2.45)
    railing_x(f"{name}_Back", x, y + 1.52, top, 2.45)
    railing_y(f"{name}_Outer", x + sgn * 1.20, y, top, 3.05)


# ============================================================
# FIRE ESCAPE (right side)
# ============================================================

FE_X = BUILDING_W / 2 + 1.25
FE_Y = 0.55


def fe_platform_z(f):
    return floor_z(f) + 0.28


def stair_flight(name, x, y_start, y_end, z_top_start, steps=13, width=1.0):
    """Stairs running along Y, rising FLOOR_H from one platform surface to the next."""
    rise = FLOOR_H / steps
    for i in range(steps):
        y = y_start + (y_end - y_start) * i / (steps - 1)
        top = z_top_start + (i + 1) * rise
        cube(f"{name}_Step_{i+1}", (x, y, top - 0.05), (width, 0.24, 0.10), M["dark2"], 0.015, "FIRE_ESCAPE")

    for sx in (-width / 2 + 0.05, width / 2 - 0.05):
        beam_between(f"{name}_Stringer",
                     (x + sx, y_start, z_top_start + rise - 0.16),
                     (x + sx, y_end, z_top_start + FLOOR_H - 0.16),
                     0.08, M["dark"], "FIRE_ESCAPE")


def build_fire_escape():
    for f in range(FLOORS):
        z = fe_platform_z(f)
        top = z + 0.08
        cube(f"FireEscape_Platform_F{f+1}", (FE_X, FE_Y, z), (2.40, 3.0, 0.16), M["dark2"], 0.025, "FIRE_ESCAPE")
        railing_x(f"FE_Rail_F{f+1}_Front", FE_X, FE_Y - 1.45, top, 2.40, 1.05, "FIRE_ESCAPE")
        railing_x(f"FE_Rail_F{f+1}_Back", FE_X, FE_Y + 1.45, top, 2.40, 1.05, "FIRE_ESCAPE")
        railing_y(f"FE_Rail_F{f+1}_Outer", FE_X + 1.17, FE_Y, top, 2.9, 1.05, "FIRE_ESCAPE")

    for f in range(FLOORS - 1):
        top = fe_platform_z(f) + 0.08
        if f % 2 == 0:
            stair_flight(f"Stairs_{f+1}_to_{f+2}", FE_X, -0.6, 1.7, top)
        else:
            stair_flight(f"Stairs_{f+1}_to_{f+2}", FE_X, 1.7, -0.6, top)

    # Vertical supports at the platform corners.
    z_top = fe_platform_z(FLOORS - 1) + 0.08
    for x in (BUILDING_W / 2 + 0.2, BUILDING_W / 2 + 2.3):
        for y in (FE_Y - 1.4, FE_Y + 1.4):
            beam_between("FireEscape_Support", (x, y, 0.0), (x, y, z_top), 0.10, M["dark"], "FIRE_ESCAPE")


# ============================================================
# ROOF
# ============================================================

def build_roof():
    cube("Roof_Slab", (0, 0, ROOF_Z), (BUILDING_W + 0.45, BUILDING_D + 0.45, 0.25), M["roof"], 0.04, "ROOF")

    railing_x("Roof_Rail_Front", 0, -BUILDING_D / 2 - 0.15, ROOF_TOP, BUILDING_W + 0.25, 1.05, "ROOF")
    railing_x("Roof_Rail_Back", 0, BUILDING_D / 2 + 0.15, ROOF_TOP, BUILDING_W + 0.25, 1.05, "ROOF")
    railing_y("Roof_Rail_Left", -BUILDING_W / 2 - 0.15, 0, ROOF_TOP, BUILDING_D + 0.25, 1.05, "ROOF")
    railing_y("Roof_Rail_Right", BUILDING_W / 2 + 0.15, 0, ROOF_TOP, BUILDING_D + 0.25, 1.05, "ROOF")

    room_h = 1.55
    cube("Rooftop_Access_Room", (0.5, 0.45, ROOF_TOP + room_h / 2), (2.0, 1.75, room_h), M["yellow"], 0.04, "ROOF")
    cube("Rooftop_Access_Door", (0.5, 0.45 - 0.875, ROOF_TOP + 0.575), (0.85, 0.10, 1.15), M["door"], 0.02, "ROOF")


def build_corner_posts():
    off = 0.17                     # outside the wall face (posts used to be hidden inside the wall)
    for x in (-BUILDING_W / 2 - off, BUILDING_W / 2 + off):
        for y in (-BUILDING_D / 2 - off, BUILDING_D / 2 + off):
            beam_between("Corner_Post", (x, y, 0.0), (x, y, CORNICE_TOP), 0.14, M["dark"], "BUILDING")
            for f in range(FLOORS):
                cube("Corner_Decor", (x, y, floor_z(f) + 0.30), (0.32, 0.32, 0.42), M["dark2"], 0.02, "BUILDING")


def add_building_sign():
    add_text("Building_Sign", "APARTMENTS",
             (0.5, 0.45 - 0.875 - 0.02, ROOF_TOP + 1.40), 0.22, M["white"])


# ============================================================
# WORLD / CAMERA / LIGHTS / RENDER
# ============================================================

def setup_world():
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    if world.node_tree is None:
        world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.018, 0.022, 0.028, 1)
        bg.inputs["Strength"].default_value = 0.28


def point_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def setup_camera():
    cam_data = bpy.data.cameras.new("Main_Camera")
    cam_data.lens = 45
    cam_data.sensor_width = 36
    cam_data.clip_end = 200
    cam = bpy.data.objects.new("Main_Camera", cam_data)
    cam.location = (15.5, -18.0, 12.0)
    bpy.context.scene.collection.objects.link(cam)
    point_at(cam, (0.5, 0, 5.3))
    bpy.context.scene.camera = cam


def add_area_light(name, location, energy, size, target):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.shape = 'DISK'
    data.size = size
    obj = bpy.data.objects.new(name, data)
    obj.location = location
    COLS["LIGHTS"].objects.link(obj)
    point_at(obj, target)
    return obj


def setup_lights():
    add_area_light("Key_Light", (7, -10, 15), 1500, 7, (0, 0, 5))
    add_area_light("Fill_Light", (-9, -3, 9), 850, 6, (0, 0, 5))
    add_area_light("Rim_Light", (4, 8, 13), 1100, 5, (0, 0, 6))


def setup_render():
    scene = bpy.context.scene

    # Blender 5.x: 'BLENDER_EEVEE'; 4.2-4.5: 'BLENDER_EEVEE_NEXT'.
    for engine in ('BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT'):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue

    scene.render.resolution_x = 700
    scene.render.resolution_y = 850
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = False

    try:
        scene.view_settings.view_transform = 'AgX'
        scene.view_settings.look = 'AgX - Medium High Contrast'
    except TypeError:
        pass   # look names differ between versions; default look is fine

    scene.render.filepath = "//low_poly_building.png"


# ============================================================
# BUILD
# ============================================================

def build():
    clear_scene()
    init_collections()      # must come after clear_scene()
    init_materials()        # must come after clear_scene()

    setup_world()

    build_ground()
    build_walls()
    build_decorative_cornice()
    build_windows()
    build_front_door()
    build_corner_posts()

    # Balconies on the left (the fire escape occupies the right side).
    build_balcony("left", 1)
    build_balcony("left", 2)
    build_fire_escape()

    build_roof()
    if ADD_SIGN:
        add_building_sign()

    setup_camera()
    setup_lights()
    setup_render()

    if SAVE_BLEND and bpy.data.is_saved:
        bpy.ops.wm.save_mainfile()

    print("=" * 60)
    print("LOW-POLY BUILDING GENERATED")
    print("3 floors, windows, cornices, balconies, fire escape, roof")
    print("Render path: //low_poly_building.png")
    print("=" * 60)


build()