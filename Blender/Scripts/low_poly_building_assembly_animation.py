import bpy
import math
from mathutils import Vector

# ================================================================
# CONFIGURATION
# ================================================================

FPS = 24

FRAME_START = 1
FRAME_END = 240

# How far objects travel before entering their final position.
FLOOR_DROP = 5.0
ROOF_DROP = 3.5
SIDE_SLIDE = 5.0

# Stagger individual objects within a floor.
OBJECT_STAGGER = 1.2

# Animation duration for each major building stage.
FOUNDATION_START = 1
FOUNDATION_END = 24

FLOOR1_START = 25
FLOOR1_END = 65

FLOOR2_START = 66
FLOOR2_END = 106

FLOOR3_START = 107
FLOOR3_END = 147

ROOF_START = 148
ROOF_END = 178

FIRE_ESCAPE_START = 179
FIRE_ESCAPE_END = 218

FINAL_START = 219
FINAL_END = 240

# ================================================================
# SCENE SETUP
# ================================================================

scene = bpy.context.scene

scene.render.fps = FPS
scene.frame_start = FRAME_START
scene.frame_end = FRAME_END

# ================================================================
# HELPERS
# ================================================================

def world_bbox_center(obj):
    """Return the object's world-space bounding-box center."""
    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return sum(corners, Vector()) / 8.0


def world_bbox_min_z(obj):
    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return min(v.z for v in corners)


def world_bbox_max_z(obj):
    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return max(v.z for v in corners)


def collection_names(obj):
    return {c.name.upper() for c in obj.users_collection}


def has_collection(obj, keyword):
    keyword = keyword.upper()
    return any(keyword in name for name in collection_names(obj))


def is_animatable(obj):
    if obj.type in {'CAMERA', 'LIGHT'}:
        return False

    # Do not animate empties unless explicitly requested.
    if obj.type == 'EMPTY':
        return False

    # Only objects with a location can be animated.
    return hasattr(obj, "location")


def clear_existing_animation(obj):
    """Remove old location animation only, leaving other animation intact."""
    if not obj.animation_data or not obj.animation_data.action:
        return

    action = obj.animation_data.action

    for fc in list(action.fcurves):
        if fc.data_path == "location":
            action.fcurves.remove(fc)


def set_interpolation(obj, mode='BEZIER'):
    if not obj.animation_data or not obj.animation_data.action:
        return

    for fc in obj.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = mode


def key_location(obj, frame, location):
    obj.location = location
    obj.keyframe_insert(
        data_path="location",
        frame=frame,
        group="Assembly Animation"
    )


def animate_slide_vertical(
    obj,
    start_frame,
    end_frame,
    distance,
    stagger=0
):
    """
    Object begins below its final position and slides vertically upward.
    """

    final_location = obj.location.copy()

    start = start_frame + stagger
    end = end_frame + stagger

    # If animation exceeds timeline, clamp it.
    if end > FRAME_END:
        end = FRAME_END

    start_location = final_location.copy()
    start_location.z -= distance

    key_location(obj, start, start_location)
    key_location(obj, end, final_location)

    set_interpolation(obj, 'BEZIER')


def animate_slide_side(
    obj,
    start_frame,
    end_frame,
    distance,
    direction=1,
    stagger=0
):
    """
    Object slides horizontally from the side into its final position.
    """

    final_location = obj.location.copy()

    start = start_frame + stagger
    end = end_frame + stagger

    if end > FRAME_END:
        end = FRAME_END

    start_location = final_location.copy()
    start_location.x += distance * direction

    key_location(obj, start, start_location)
    key_location(obj, end, final_location)

    set_interpolation(obj, 'BEZIER')


def animate_scale_pop(obj, start_frame, end_frame, stagger=0):
    """
    Small scale-in effect for tiny decorative elements.
    Disabled by default for major architectural geometry.
    """

    original_scale = obj.scale.copy()

    start = start_frame + stagger
    end = end_frame + stagger

    if end > FRAME_END:
        end = FRAME_END

    obj.scale = (0.001, 0.001, 0.001)
    obj.keyframe_insert(
        data_path="scale",
        frame=start,
        group="Assembly Accent"
    )

    obj.scale = original_scale
    obj.keyframe_insert(
        data_path="scale",
        frame=end,
        group="Assembly Accent"
    )

    set_interpolation(obj, 'BEZIER')


# ================================================================
# OBJECT CLASSIFICATION
# ================================================================

def classify_object(obj):
    """
    Classify an existing building object.

    Returns:
        foundation
        floor1
        floor2
        floor3
        roof
        fire_escape
        ground
        other
    """

    names = obj.name.upper()
    cols = collection_names(obj)

    # Explicit collections have priority.
    if any("FIRE" in c or "ESCAPE" in c for c in cols):
        return "fire_escape"

    if any("ROOF" in c for c in cols):
        return "roof"

    # Ground objects.
    if "GROUND" in names:
        return "ground"

    # Foundation.
    if "FOUNDATION" in names:
        return "foundation"

    # Determine floor using world-space Z.
    center_z = world_bbox_center(obj).z

    # Objects below the first floor.
    if center_z < 3.4:
        return "floor1"

    if center_z < 6.6:
        return "floor2"

    if center_z < 9.8:
        return "floor3"

    # Rooftop and very high objects.
    return "roof"


# ================================================================
# BUILD OBJECT LIST
# ================================================================

objects = [
    obj for obj in scene.objects
    if is_animatable(obj)
]

# Exclude obvious non-building helpers.
excluded_names = {
    "MAIN_CAMERA",
    "PEEPHOLE_CAMERA",
}

objects = [
    obj for obj in objects
    if obj.name.upper() not in excluded_names
]

groups = {
    "ground": [],
    "foundation": [],
    "floor1": [],
    "floor2": [],
    "floor3": [],
    "roof": [],
    "fire_escape": [],
    "other": [],
}

for obj in objects:
    category = classify_object(obj)

    if category not in groups:
        category = "other"

    groups[category].append(obj)


# ================================================================
# SORT OBJECTS
# ================================================================

# Sorting by height makes the assembly visually coherent.
for group in groups.values():
    group.sort(
        key=lambda o: (
            world_bbox_center(o).z,
            world_bbox_center(o).x,
            world_bbox_center(o).y,
            o.name
        )
    )


# ================================================================
# REMOVE OLD LOCATION ANIMATION
# ================================================================

for obj in objects:
    clear_existing_animation(obj)


# ================================================================
# GROUND / FOUNDATION
# ================================================================

# Ground stays mostly static.
for i, obj in enumerate(groups["ground"]):
    animate_scale_pop(
        obj,
        FRAME_START,
        FOUNDATION_END,
        stagger=min(i * 0.5, 8)
    )


# Foundation rises first.
for i, obj in enumerate(groups["foundation"]):
    animate_slide_vertical(
        obj,
        FOUNDATION_START,
        FOUNDATION_END,
        FLOOR_DROP,
        stagger=min(i * OBJECT_STAGGER, 8)
    )


# ================================================================
# FLOOR 1
# ================================================================

for i, obj in enumerate(groups["floor1"]):
    animate_slide_vertical(
        obj,
        FLOOR1_START,
        FLOOR1_END,
        FLOOR_DROP,
        stagger=min(i * OBJECT_STAGGER, 14)
    )


# ================================================================
# FLOOR 2
# ================================================================

for i, obj in enumerate(groups["floor2"]):
    animate_slide_vertical(
        obj,
        FLOOR2_START,
        FLOOR2_END,
        FLOOR_DROP,
        stagger=min(i * OBJECT_STAGGER, 14)
    )


# ================================================================
# FLOOR 3
# ================================================================

for i, obj in enumerate(groups["floor3"]):
    animate_slide_vertical(
        obj,
        FLOOR3_START,
        FLOOR3_END,
        FLOOR_DROP,
        stagger=min(i * OBJECT_STAGGER, 14)
    )


# ================================================================
# ROOF
# ================================================================

for i, obj in enumerate(groups["roof"]):
    animate_slide_vertical(
        obj,
        ROOF_START,
        ROOF_END,
        ROOF_DROP,
        stagger=min(i * OBJECT_STAGGER, 12)
    )


# ================================================================
# FIRE ESCAPE / BALCONIES
# ================================================================

# Fire escape enters from the right side.
for i, obj in enumerate(groups["fire_escape"]):

    # Alternate tiny offsets to make the assembly less mechanical.
    direction = 1

    animate_slide_side(
        obj,
        FIRE_ESCAPE_START,
        FIRE_ESCAPE_END,
        SIDE_SLIDE,
        direction=direction,
        stagger=min(i * 0.7, 15)
    )


# ================================================================
# ACCENT DETAILS
# ================================================================

# Small decorative details appear shortly after their floor arrives.
accent_keywords = (
    "DENTIL",
    "DECOR",
    "MULLION",
    "HANDLE",
)

for obj in objects:

    if not any(k in obj.name.upper() for k in accent_keywords):
        continue

    category = classify_object(obj)

    if category == "floor1":
        animate_scale_pop(obj, FLOOR1_END - 8, FLOOR1_END)
    elif category == "floor2":
        animate_scale_pop(obj, FLOOR2_END - 8, FLOOR2_END)
    elif category == "floor3":
        animate_scale_pop(obj, FLOOR3_END - 8, FLOOR3_END)
    elif category == "roof":
        animate_scale_pop(obj, ROOF_END - 8, ROOF_END)


# ================================================================
# FINAL FRAME
# ================================================================

scene.frame_set(FRAME_START)

# ================================================================
# OPTIONAL
# ================================================================
#
# The existing camera remains static by default.
#
# If a subtle cinematic push-in, uncomment this section.
#
# camera = scene.camera
# if camera:
#     original_location = camera.location.copy()
#     camera.location = original_location + Vector((0, -2.0, 0))
#     camera.keyframe_insert(
#         data_path="location",
#         frame=FRAME_START
#     )
#     camera.location = original_location
#     camera.keyframe_insert(
#         data_path="location",
#         frame=FINAL_END
#     )


# ================================================================
# SET EASING
# ================================================================

for obj in objects:
    if not obj.animation_data or not obj.animation_data.action:
        continue

    for fc in obj.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'BEZIER'

            # Smooth automatic handles.
            kp.handle_left_type = 'AUTO'
            kp.handle_right_type = 'AUTO'


# ================================================================
# MARK IMPORTANT FRAMES
# ================================================================

markers = [
    ("Foundation", FOUNDATION_START),
    ("Floor_1", FLOOR1_START),
    ("Floor_2", FLOOR2_START),
    ("Floor_3", FLOOR3_START),
    ("Roof", ROOF_START),
    ("Fire_Escape", FIRE_ESCAPE_START),
    ("Complete", FINAL_START),
]

# Remove duplicate markers with these names.
for marker in list(scene.timeline_markers):
    if marker.name in {m[0] for m in markers}:
        scene.timeline_markers.remove(marker)

for name, frame in markers:
    scene.timeline_markers.new(name, frame=frame)


# ================================================================
# OPTIONAL RENDER SETTINGS
# ================================================================

scene.render.fps = 24
scene.frame_start = FRAME_START
scene.frame_end = FRAME_END

# Animation output:
# Change this path if you want a different location.
scene.render.filepath = "//building_assembly_"

# Use PNG frames.
scene.render.image_settings.file_format = 'PNG'


# ================================================================
# SAVE
# ================================================================

try:
    bpy.ops.wm.save_as_mainfile(
        filepath="//low_poly_building_animated.blend"
    )
except Exception as e:
    print("Could not automatically save animation file:", e)


# ================================================================
# REPORT
# ================================================================

print("\n" + "=" * 70)
print("LOW-POLY BUILDING ASSEMBLY ANIMATION CREATED")
print("=" * 70)

for name, group in groups.items():
    print(f"{name:15s}: {len(group):4d} objects")

print("-" * 70)
print("Timeline: 1 - 240")
print("FPS:      24")
print("Duration: 10 seconds")
print("-" * 70)
print("Stages:")
print("  1-24    Foundation / ground")
print("  25-65   Floor 1")
print("  66-106  Floor 2")
print("  107-147 Floor 3")
print("  148-178 Roof")
print("  179-218 Fire escape / balconies")
print("  219-240 Completed building")
print("-" * 70)
print("Saved as: low_poly_building_animated.blend")
print("=" * 70)

# Return to frame 1.
scene.frame_set(FRAME_START)
