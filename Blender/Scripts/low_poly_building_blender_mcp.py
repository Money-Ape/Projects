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

# ============================================================
# SCENE / COLLECTION HELPERS
# ============================================================

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        # Keep datablocks that Blender may require internally.
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)

def collection(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c

COL_BUILDING = collection("BUILDING")
COL_WINDOWS = collection("WINDOWS")
COL_BALCONIES = collection("BALCONIES")
COL_FIRE_ESCAPE = collection("FIRE_ESCAPE")
COL_ROOF = collection("ROOF")
COL_LIGHTS = collection("LIGHTS")

def move_to_collection(obj, target):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    target.objects.link(obj)

# ============================================================
# MATERIALS
# ============================================================

def mat(name, color, roughness=0.7, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True

    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return m

YELLOW = mat("Wall_Yellow", (0.70, 0.46, 0.035), 0.78)
YELLOW_LIGHT = mat("Wall_Yellow_Light", (0.95, 0.68, 0.055), 0.75)
WHITE = mat("Cornice_White", (0.82, 0.82, 0.77), 0.65)
DARK = mat("Iron_Dark", (0.075, 0.085, 0.095), 0.65, 0.05)
DARK2 = mat("Iron_Dark2", (0.12, 0.13, 0.14), 0.72)
GLASS = mat("Window_Glass", (0.65, 0.82, 0.85), 0.18, 0.0)
WOOD = mat("Door_Red", (0.34, 0.055, 0.045), 0.72)
WINDOW_FRAME = mat("Window_Frame", (0.23, 0.20, 0.14), 0.72)
WINDOW_LIGHT = mat("Window_Lit", (1.0, 0.78, 0.38), 0.30)
ROOF = mat("Roof", (0.16, 0.17, 0.18), 0.82)
GROUND = mat("Ground", (0.055, 0.06, 0.065), 0.95)

# ============================================================
# PRIMITIVE HELPERS
# ============================================================

def cube(name, loc, scale, material, bevel=0.0, coll=COL_BUILDING):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = (scale[0] / 2, scale[1] / 2, scale[2] / 2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    if material:
        o.data.materials.append(material)

    if bevel > 0:
        mod = o.modifiers.new("Small_Bevel", 'BEVEL')
        mod.width = bevel
        mod.segments = 1

    move_to_collection(o, coll)
    return o

def cylinder(name, loc, radius, depth, material, vertices=8, rotation=None, coll=COL_BUILDING):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=loc,
        rotation=rotation or (0, 0, 0),
    )
    o = bpy.context.object
    o.name = name
    if material:
        o.data.materials.append(material)
    move_to_collection(o, coll)
    return o

def beam_between(name, a, b, thickness, material, coll=COL_BUILDING):
    a = Vector(a)
    b = Vector(b)
    d = b - a
    length = d.length
    mid = (a + b) / 2

    o = cube(
        name,
        mid,
        (thickness, thickness, length),
        material,
        0.02,
        coll
    )

    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    return o

def add_text(name, text, loc, size, material, rotation=(math.pi/2, 0, 0)):
    bpy.ops.object.text_add(location=loc, rotation=rotation)
    o = bpy.context.object
    o.name = name
    o.data.body = text
    o.data.align_x = 'CENTER'
    o.data.align_y = 'CENTER'
    o.data.size = size
    o.data.extrude = 0.015
    o.data.materials.append(material)
    return o

# ============================================================
# BUILDING CORE
# ============================================================

def build_walls():
    for floor in range(FLOORS):
        z = WALL_Z0 + floor * FLOOR_H + WALL_H / 2

        # Main four walls. Openings are represented by darker window
        # assemblies placed over the wall surface; this keeps the model
        # lightweight and very stable.
        cube(
            f"Wall_F{floor+1}_Front",
            (0, -BUILDING_D/2, z),
            (BUILDING_W, 0.30, WALL_H),
            YELLOW,
            0.04
        )

        cube(
            f"Wall_F{floor+1}_Back",
            (0, BUILDING_D/2, z),
            (BUILDING_W, 0.30, WALL_H),
            YELLOW,
            0.04
        )

        cube(
            f"Wall_F{floor+1}_Left",
            (-BUILDING_W/2, 0, z),
            (0.30, BUILDING_D, WALL_H),
            YELLOW,
            0.04
        )

        cube(
            f"Wall_F{floor+1}_Right",
            (BUILDING_W/2, 0, z),
            (0.30, BUILDING_D, WALL_H),
            YELLOW,
            0.04
        )

        # Floor separator / white cornice.
        z_band = WALL_Z0 + floor * FLOOR_H + WALL_H + 0.04
        cube(
            f"Cornice_F{floor+1}",
            (0, 0, z_band),
            (BUILDING_W + 0.55, BUILDING_D + 0.55, 0.22),
            WHITE,
            0.035
        )

        # Dark foundation strip.
        cube(
            f"Foundation_F{floor+1}",
            (0, 0, WALL_Z0 + floor * FLOOR_H - 0.05),
            (BUILDING_W + 0.35, BUILDING_D + 0.35, 0.22),
            DARK,
            0.03
        )

def build_decorative_cornice():
    # Repeated white triangular/rectangular teeth under every floor band.
    for floor in range(FLOORS):
        z = WALL_Z0 + floor * FLOOR_H + WALL_H - 0.20

        # Front + back.
        for y in (-BUILDING_D/2 - 0.18, BUILDING_D/2 + 0.18):
            for i in range(14):
                x = -BUILDING_W/2 + 0.35 + i * (BUILDING_W - 0.7) / 13
                cube(
                    f"F{floor+1}_Dentil_FrontBack_{i}",
                    (x, y, z),
                    (0.28, 0.24, 0.45),
                    WHITE,
                    0.015
                )

        # Sides.
        for x in (-BUILDING_W/2 - 0.18, BUILDING_W/2 + 0.18):
            for i in range(10):
                y = -BUILDING_D/2 + 0.30 + i * (BUILDING_D - 0.60) / 9
                cube(
                    f"F{floor+1}_Dentil_Side_{i}",
                    (x, y, z),
                    (0.24, 0.28, 0.45),
                    WHITE,
                    0.015
                )

# ============================================================
# WINDOWS
# ============================================================

def build_window(name, x, y, z, facing="front"):
    # Window is a shallow framed assembly.
    if facing in ("front", "back"):
        depth_axis = 0.16
        frame_depth = 0.12
        glass = cube(
            name + "_Glass",
            (x, y, z),
            (WINDOW_W, frame_depth, WINDOW_H),
            WINDOW_LIGHT,
            0.015,
            COL_WINDOWS
        )

        # Outer frame.
        for sx in (-1, 1):
            cube(
                name + "_FrameV",
                (x + sx*(WINDOW_W/2 + 0.075), y, z),
                (0.13, 0.20, WINDOW_H + 0.18),
                WINDOW_FRAME,
                0.02,
                COL_WINDOWS
            )

        for sz in (-1, 1):
            cube(
                name + "_FrameH",
                (x, y, z + sz*(WINDOW_H/2 + 0.075)),
                (WINDOW_W + 0.28, 0.20, 0.13),
                WINDOW_FRAME,
                0.02,
                COL_WINDOWS
            )

        # Mullions.
        for col in (-0.22, 0.22):
            cube(
                name + "_MullionV",
                (x + col, y - 0.015, z),
                (0.055, 0.22, WINDOW_H),
                WINDOW_FRAME,
                0.01,
                COL_WINDOWS
            )

        for row in (-0.30, 0.0, 0.30):
            cube(
                name + "_MullionH",
                (x, y - 0.015, z + row),
                (WINDOW_W, 0.22, 0.055),
                WINDOW_FRAME,
                0.01,
                COL_WINDOWS
            )

        # Window sill.
        cube(
            name + "_Sill",
            (x, y - 0.05, z - WINDOW_H/2 - 0.14),
            (WINDOW_W + 0.35, 0.32, 0.13),
            WHITE,
            0.02,
            COL_WINDOWS
        )

    else:
        # Rotate the same visual system for left/right walls.
        cube(
            name + "_Glass",
            (x, y, z),
            (0.16, WINDOW_W, WINDOW_H),
            WINDOW_LIGHT,
            0.015,
            COL_WINDOWS
        )

        for sy in (-1, 1):
            cube(
                name + "_FrameH",
                (x, y + sy*(WINDOW_W/2 + 0.075), z),
                (0.20, 0.13, WINDOW_H + 0.18),
                WINDOW_FRAME,
                0.02,
                COL_WINDOWS
            )

        for sz in (-1, 1):
            cube(
                name + "_FrameV",
                (x, y, z + sz*(WINDOW_H/2 + 0.075)),
                (0.20, WINDOW_W + 0.28, 0.13),
                WINDOW_FRAME,
                0.02,
                COL_WINDOWS
            )

        # Mullions.
        for col in (-0.22, 0.22):
            cube(
                name + "_Mullion",
                (x + 0.015, y + col, z),
                (0.22, 0.055, WINDOW_H),
                WINDOW_FRAME,
                0.01,
                COL_WINDOWS
            )

        for row in (-0.30, 0.0, 0.30):
            cube(
                name + "_Mullion",
                (x + 0.015, y, z + row),
                (0.22, WINDOW_W, 0.055),
                WINDOW_FRAME,
                0.01,
                COL_WINDOWS
            )

def build_windows():
    x_positions = (-2.65, 0.0, 2.65)
    y_positions = (-1.75, 0.0, 1.75)

    for floor in range(FLOORS):
        z = WALL_Z0 + floor * FLOOR_H + 1.72

        # Front: ground floor gets a door in the center.
        for i, x in enumerate(x_positions):
            if floor == 0 and i == 0:
                continue
            build_window(
                f"Front_F{floor+1}_{i+1}",
                x,
                -BUILDING_D/2 - 0.17,
                z,
                "front"
            )

        # Back.
        for i, x in enumerate(x_positions):
            build_window(
                f"Back_F{floor+1}_{i+1}",
                x,
                BUILDING_D/2 + 0.17,
                z,
                "back"
            )

        # Left/right.
        for i, y in enumerate(y_positions):
            build_window(
                f"Left_F{floor+1}_{i+1}",
                -BUILDING_W/2 - 0.17,
                y,
                z,
                "left"
            )

            build_window(
                f"Right_F{floor+1}_{i+1}",
                BUILDING_W/2 + 0.17,
                y,
                z,
                "right"
            )

def build_front_door():
    z = WALL_Z0 + 1.55
    x = -2.65
    y = -BUILDING_D/2 - 0.18

    cube(
        "Main_Door",
        (x, y, z),
        (1.05, 0.22, 2.15),
        WOOD,
        0.04,
        COL_WINDOWS
    )

    cube(
        "Door_Frame_L",
        (x - 0.60, y, z),
        (0.14, 0.28, 2.35),
        WINDOW_FRAME,
        0.02,
        COL_WINDOWS
    )
    cube(
        "Door_Frame_R",
        (x + 0.60, y, z),
        (0.14, 0.28, 2.35),
        WINDOW_FRAME,
        0.02,
        COL_WINDOWS
    )

    cylinder(
        "Door_Handle",
        (x + 0.31, y - 0.15, z),
        0.055,
        0.08,
        WHITE,
        8,
        rotation=(math.pi/2, 0, 0),
        coll=COL_WINDOWS
    )

# ============================================================
# BALCONIES + RAILINGS
# ============================================================

def railing_x(name_prefix, y, z, width, height=1.0):
    # horizontal top and bottom
    beam_between(
        name_prefix + "_Top",
        (-width/2, y, z + height),
        (width/2, y, z + height),
        0.12, DARK, COL_BALCONIES
    )
    beam_between(
        name_prefix + "_Bottom",
        (-width/2, y, z),
        (width/2, y, z),
        0.10, DARK, COL_BALCONIES
    )

    count = max(2, int(width / 0.38))
    for i in range(count + 1):
        x = -width/2 + i * width/count
        beam_between(
            name_prefix + f"_Post_{i}",
            (x, y, z),
            (x, y, z + height),
            0.075, DARK, COL_BALCONIES
        )

def railing_y(name_prefix, x, z, depth, height=1.0):
    beam_between(
        name_prefix + "_Top",
        (x, -depth/2, z + height),
        (x, depth/2, z + height),
        0.12, DARK, COL_BALCONIES
    )
    beam_between(
        name_prefix + "_Bottom",
        (x, -depth/2, z),
        (x, depth/2, z),
        0.10, DARK, COL_BALCONIES
    )

    count = max(2, int(depth / 0.38))
    for i in range(count + 1):
        y = -depth/2 + i * depth/count
        beam_between(
            name_prefix + f"_Post_{i}",
            (x, y, z),
            (x, y, z + height),
            0.075, DARK, COL_BALCONIES
        )

def build_balcony(side="right", floor=1):
    # floor is zero based. Main balconies on upper floors.
    z = WALL_Z0 + floor * FLOOR_H + 0.25
    if side == "right":
        x = BUILDING_W/2 + 1.25
        y = 0.55
    else:
        x = -BUILDING_W/2 - 1.25
        y = 0.55

    # Platform.
    cube(
        f"Balcony_F{floor+1}_Platform",
        (x, y, z),
        (2.45, 3.15, 0.18),
        DARK2,
        0.03,
        COL_BALCONIES
    )

    # Brackets underneath.
    for yy in (y - 1.0, y + 1.0):
        beam_between(
            f"Balcony_F{floor+1}_Bracket",
            (BUILDING_W/2 if side == "right" else -BUILDING_W/2, yy, z - 0.05),
            (x, yy, z - 0.80),
            0.13, DARK, COL_BALCONIES
        )

    if side == "right":
        railing_x(
            f"Balcony_F{floor+1}_Front",
            y - 1.52,
            z,
            2.45,
            1.0
        )
        railing_y(
            f"Balcony_F{floor+1}_Outer",
            x + 1.20,
            z,
            3.05,
            1.0
        )
        railing_x(
            f"Balcony_F{floor+1}_Back",
            y + 1.52,
            z,
            2.45,
            1.0
        )
    else:
        railing_x(
            f"Balcony_F{floor+1}_Front",
            y - 1.52,
            z,
            2.45,
            1.0
        )
        railing_y(
            f"Balcony_F{floor+1}_Outer",
            x - 1.20,
            z,
            3.05,
            1.0
        )

# ============================================================
# FIRE ESCAPE / EXTERNAL STAIRS
# ============================================================

def stair_flight(name, start, end, steps=10, width=1.25):
    start = Vector(start)
    end = Vector(end)

    for i in range(steps):
        t = i / max(1, steps - 1)
        p = start.lerp(end, t)

        # Each step is a thin metal slab.
        cube(
            f"{name}_Step_{i+1}",
            p,
            (width, 0.34, 0.12),
            DARK2,
            0.015,
            COL_FIRE_ESCAPE
        )

        # Side stringers.
        if i < steps - 1:
            p2 = start.lerp(end, (i + 1) / max(1, steps - 1))
            for sx in (-width/2 + 0.08, width/2 - 0.08):
                beam_between(
                    f"{name}_Stringer_{i}_{sx}",
                    (p.x + sx, p.y, p.z - 0.12),
                    (p2.x + sx, p2.y, p2.z - 0.12),
                    0.075, DARK, COL_FIRE_ESCAPE
                )

def build_fire_escape():
    # Fire escape on the right/back side, matching the reference silhouette.
    for floor in (0, 1, 2):
        z = WALL_Z0 + floor * FLOOR_H + 0.28
        x = BUILDING_W/2 + 1.25
        y = 0.55

        # Platform.
        cube(
            f"FireEscape_Platform_F{floor+1}",
            (x, y, z),
            (2.40, 3.0, 0.16),
            DARK2,
            0.025,
            COL_FIRE_ESCAPE
        )

        # Platform railings.
        railing_x(
            f"FireEscape_Railing_F{floor+1}_Front",
            y - 1.45,
            z,
            2.40,
            1.05
        )
        railing_y(
            f"FireEscape_Railing_F{floor+1}_Outer",
            x + 1.17,
            z,
            2.9,
            1.05
        )
        railing_x(
            f"FireEscape_Railing_F{floor+1}_Back",
            y + 1.45,
            z,
            2.40,
            1.05
        )

    # Zig-zag stair flights between platforms.
    for floor in (0, 1):
        z0 = WALL_Z0 + floor * FLOOR_H + 0.40
        z1 = WALL_Z0 + (floor + 1) * FLOOR_H + 0.40

        if floor % 2 == 0:
            stair_flight(
                f"Stairs_{floor+1}_to_{floor+2}",
                (BUILDING_W/2 + 0.15, -0.95, z0),
                (BUILDING_W/2 + 2.25, 0.95, z1),
                11,
                1.25
            )
        else:
            stair_flight(
                f"Stairs_{floor+1}_to_{floor+2}",
                (BUILDING_W/2 + 2.25, 0.95, z0),
                (BUILDING_W/2 + 0.15, -0.95, z1),
                11,
                1.25
            )

    # Vertical support posts.
    for x in (BUILDING_W/2 + 0.15, BUILDING_W/2 + 2.35):
        beam_between(
            "FireEscape_VerticalSupport",
            (x, 0.55, 0.15),
            (x, 0.55, WALL_Z0 + FLOORS*FLOOR_H),
            0.10, DARK, COL_FIRE_ESCAPE
        )

# ============================================================
# ROOFTOP
# ============================================================

def build_roof():
    roof_z = WALL_Z0 + FLOORS * FLOOR_H + 0.20

    cube(
        "Roof_Slab",
        (0, 0, roof_z),
        (BUILDING_W + 0.45, BUILDING_D + 0.45, 0.25),
        ROOF,
        0.04,
        COL_ROOF
    )

    # Roof perimeter railings.
    railing_x(
        "Roof_Railing_Front",
        -BUILDING_D/2 - 0.15,
        roof_z,
        BUILDING_W + 0.25,
        1.05
    )
    railing_x(
        "Roof_Railing_Back",
        BUILDING_D/2 + 0.15,
        roof_z,
        BUILDING_W + 0.25,
        1.05
    )
    railing_y(
        "Roof_Railing_Left",
        -BUILDING_W/2 - 0.15,
        roof_z,
        BUILDING_D + 0.25,
        1.05
    )
    railing_y(
        "Roof_Railing_Right",
        BUILDING_W/2 + 0.15,
        roof_z,
        BUILDING_D + 0.25,
        1.05
    )

    # Small rooftop access room.
    cube(
        "Rooftop_Access_Room",
        (0.5, 0.45, roof_z + 0.90),
        (2.0, 1.75, 1.55),
        YELLOW,
        0.04,
        COL_ROOF
    )

    cube(
        "Rooftop_Access_Door",
        (0.5, -0.445, roof_z + 0.82),
        (0.85, 0.10, 1.15),
        WOOD,
        0.02,
        COL_ROOF
    )

# ============================================================
# CORNER POSTS / ARCHITECTURAL DETAILS
# ============================================================

def build_corner_posts():
    total_top = WALL_Z0 + FLOORS * FLOOR_H

    for x in (-BUILDING_W/2 - 0.05, BUILDING_W/2 + 0.05):
        for y in (-BUILDING_D/2 - 0.05, BUILDING_D/2 + 0.05):
            beam_between(
                "Corner_Post",
                (x, y, 0.18),
                (x, y, total_top),
                0.14, DARK, COL_BUILDING
            )

            # Small square decorative blocks at floor levels.
            for floor in range(FLOORS):
                z = WALL_Z0 + floor * FLOOR_H + 0.30
                cube(
                    "Corner_Decor",
                    (x, y, z),
                    (0.32, 0.32, 0.42),
                    DARK2,
                    0.02,
                    COL_BUILDING
                )

# ============================================================
# GROUND
# ============================================================

def build_ground():
    cube(
        "Ground",
        (0, 0, -0.22),
        (20, 18, 0.35),
        GROUND,
        0.05,
        COL_BUILDING
    )

    # Simple front pavement.
    cube(
        "Front_Pavement",
        (0, -5.0, -0.01),
        (12, 4.0, 0.12),
        DARK2,
        0.03,
        COL_BUILDING
    )

# ============================================================
# LIGHTING / CAMERA
# ============================================================

def setup_world():
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world

    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.018, 0.022, 0.028, 1)
        bg.inputs["Strength"].default_value = 0.28

def add_area_light(name, location, energy, size):
    bpy.ops.object.light_add(type='AREA', location=location)
    light = bpy.context.object
    light.name = name
    light.data.energy = energy
    light.data.shape = 'DISK'
    light.data.size = size
    move_to_collection(light, COL_LIGHTS)
    return light

def point_camera(camera, target):
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

def setup_camera():
    bpy.ops.object.camera_add(
        location=(15.5, -18.0, 12.0)
    )
    cam = bpy.context.object
    cam.name = "Main_Camera"
    cam.data.lens = 52
    cam.data.sensor_width = 36
    point_camera(cam, (0, 0, 5.3))
    bpy.context.scene.camera = cam

def setup_lights():
    add_area_light(
        "Key_Light",
        (7, -10, 15),
        1500,
        7
    )
    key = bpy.context.object
    point_camera(key, (0, 0, 5))

    add_area_light(
        "Fill_Light",
        (-9, -3, 9),
        850,
        6
    )
    fill = bpy.context.object
    point_camera(fill, (0, 0, 5))

    add_area_light(
        "Rim_Light",
        (4, 8, 13),
        1100,
        5
    )
    rim = bpy.context.object
    point_camera(rim, (0, 0, 6))

# ============================================================
# RENDER SETTINGS
# ============================================================

def setup_render():
    scene = bpy.context.scene

    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.render.resolution_x = 700
    scene.render.resolution_y = 850
    scene.render.resolution_percentage = 100

    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = False

    # Ambient occlusion/contact-like shading is naturally handled by Eevee.
    scene.view_settings.look = 'AgX - Medium High Contrast'

    scene.render.filepath = "//low_poly_building.png"

# ============================================================
# OPTIONAL SIGN
# ============================================================

def add_building_sign():
    add_text(
        "Building_Sign",
        "APARTMENTS",
        (0, -BUILDING_D/2 - 0.22, WALL_Z0 + FLOORS*FLOOR_H + 1.7),
        0.42,
        WHITE,
        rotation=(math.pi/2, 0, 0)
    )

# ============================================================
# BUILD
# ============================================================

def build():
    clear_scene()

    setup_world()

    build_ground()
    build_walls()
    build_decorative_cornice()
    build_windows()
    build_front_door()
    build_corner_posts()

    # Upper-floor exterior balconies / fire escape.
    build_balcony("right", 1)
    build_balcony("right", 2)
    build_fire_escape()

    build_roof()

    setup_camera()
    setup_lights()
    setup_render()

    # Select the building root-ish objects for convenience.
    bpy.ops.object.select_all(action='DESELECT')

    # Save a .blend beside the script if Blender has a known file path.
    try:
        bpy.ops.wm.save_as_mainfile(filepath="//low_poly_building.blend")
    except Exception:
        pass

    print("=" * 60)
    print("LOW-POLY BUILDING GENERATED")
    print("3 floors, windows, cornices, balconies, fire escape, roof")
    print("Render path: //low_poly_building.png")
    print("=" * 60)

build()
