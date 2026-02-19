import bpy
import math
import bmesh
import random


def mesh_items(self, context):
    items = []
    for o in bpy.data.objects:
        if o.type == 'MESH':
            items.append((o.name, o.name, ""))
    if not items:
        items = [("NONE", "No mesh available", "")]
    return items


def create_thumbprint(context, location, size=1.0, thickness=0.2, noise=0.2, seed=0, segments=64, rings=24):
    """Create a procedural thumbprint-like mesh using bmesh and return the object.

    - location: Vector for the object origin
    - size: overall scale
    - thickness: depth of indentation
    - noise: amplitude of small random ridge noise
    - seed: random seed for reproducibility
    """
    name = "effect_thumb_{}_{}".format(seed, int(random.random()*1000))
    mesh = bpy.data.meshes.new(name + "_mesh")
    bm = bmesh.new()

    rng = random.Random(seed)
    # center vertex
    center_z = -thickness
    center_v = bm.verts.new((0.0, 0.0, center_z))

    two_pi = 2.0 * math.pi
    verts_rings = []
    for r in range(1, rings + 1):
        radius = r / rings
        ring_verts = []
        for s in range(segments):
            theta = two_pi * s / segments
            x = radius * math.cos(theta)
            y = radius * math.sin(theta)
            # base dome shape (deeper in center)
            base_z = -thickness * (1.0 - radius * radius)
            # radial ridge pattern + small random variation
            ridge = (math.sin(radius * 30.0 + seed) * 0.02 + (rng.random() - 0.5) * 0.01) * noise * thickness
            z = base_z + ridge
            v = bm.verts.new((x, y, z))
            ring_verts.append(v)
        verts_rings.append(ring_verts)

    bm.verts.ensure_lookup_table()

    # create faces: triangles for first ring, quads for others
    for s in range(segments):
        v1 = center_v
        v2 = verts_rings[0][s]
        v3 = verts_rings[0][(s + 1) % segments]
        try:
            bm.faces.new((v1, v2, v3))
        except Exception:
            pass

    for r in range(1, rings):
        prev = verts_rings[r - 1]
        cur = verts_rings[r]
        for s in range(segments):
            v1 = prev[s]
            v2 = prev[(s + 1) % segments]
            v3 = cur[(s + 1) % segments]
            v4 = cur[s]
            try:
                bm.faces.new((v1, v2, v3, v4))
            except Exception:
                pass

    # finish mesh
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    context.collection.objects.link(obj)

    # smooth shading
    for poly in obj.data.polygons:
        poly.use_smooth = True

    # scale to requested size
    obj.scale = (size, size, size)

    return obj


def apply_vertex_noise(obj, strength=0.1, seed=0):
    """Displace object vertices along their normals using a deterministic random seed."""
    if obj is None or obj.type != 'MESH':
        return
    mesh = obj.data
    # ensure up-to-date normals
    try:
        mesh.calc_normals()
    except Exception:
        pass
    rng = random.Random(seed)
    for i, v in enumerate(mesh.vertices):
        # small random offset along normal
        offset = (rng.random() - 0.5) * 2.0 * strength
        try:
            v.co = v.co + v.normal * offset
        except Exception:
            # if normals unavailable, apply small random in Z
            v.co = v.co + bpy.mathutils.Vector((0.0, 0.0, offset))


class EFFECTADDER_OT_apply_effect(bpy.types.Operator):
    """Apply a procedural effect (thumbprint, etc.) to a target mesh at the 3D cursor"""
    bl_idname = "effect_adder.apply_effect"
    bl_label = "Apply Effect"
    bl_options = {'REGISTER', 'UNDO'}

    mesh_name: bpy.props.EnumProperty(name="Target Mesh", items=mesh_items)
    effect_type: bpy.props.EnumProperty(
        name="Effect Type",
        items=[
            ('THUMB', 'Thumbprint', ''),
            ('EFFECT2', 'Effect 2', ''),
            ('EFFECT3', 'Effect 3', ''),
        ],
        default='THUMB'
    )
    noise: bpy.props.FloatProperty(name="Noise", min=0.0, max=1.0, default=0.2)
    rotation: bpy.props.FloatProperty(name="Rotation", min=0.0, max=360.0, default=0.0)
    size: bpy.props.FloatProperty(name="Size", min=0.1, max=10.0, default=1.0)
    thickness: bpy.props.FloatProperty(name="Thickness", min=0.0, max=2.0, default=0.2)
    seed: bpy.props.IntProperty(name="Seed", default=0)

    def execute(self, context):
        target = bpy.data.objects.get(self.mesh_name)
        if not target or target.type != 'MESH':
            self.report({'ERROR'}, "Target mesh not found or not a mesh")
            return {'CANCELLED'}

        # Ensure object mode
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass

        cursor_loc = context.scene.cursor.location.copy()

        # Create procedural thumbprint geometry
        effect_obj = create_thumbprint(context, cursor_loc, size=self.size, thickness=self.thickness, noise=self.noise, seed=self.seed)
        if effect_obj is None:
            self.report({'ERROR'}, "Failed to create effect object")
            return {'CANCELLED'}

        # rename and rotate
        effect_obj.name = "effect_{}_{}".format(self.effect_type, self.seed)
        effect_obj.rotation_euler[2] = math.radians(self.rotation)

        # Apply vertex noise (before solidify) - strength scaled by thickness
        noise_strength = max(0.0, min(1.0, self.noise)) * max(0.001, self.thickness) * 0.5
        apply_vertex_noise(effect_obj, strength=noise_strength, seed=self.seed)

        # Add Solidify for thickness (make it a solid for boolean)
        solid = effect_obj.modifiers.new(name="EffectSolidify", type='SOLIDIFY')
        solid.thickness = max(0.001, self.thickness)
        # Ensure effect object is active/selected and apply transforms
        context.view_layer.objects.active = effect_obj
        effect_obj.select_set(True)
        try:
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        except Exception:
            pass

        # Apply modifiers on the effect object (convert to final mesh)
        # (solidify already added)
        mod_names = [m.name for m in effect_obj.modifiers]
        for mname in mod_names:
            try:
                bpy.ops.object.modifier_apply(modifier=mname)
            except Exception:
                # continue even if a modifier fails to apply
                pass

        # Add Boolean modifier to target (difference)
        bpy.ops.object.select_all(action='DESELECT')
        target.select_set(True)
        context.view_layer.objects.active = target
        bool_mod = target.modifiers.new(name="EffectBoolean", type='BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.object = effect_obj

        # Try to apply boolean
        try:
            bpy.ops.object.modifier_apply(modifier=bool_mod.name)
        except Exception as e:
            self.report({'WARNING'}, "Boolean apply failed: {}".format(e))
            # keep effect object for inspection
            return {'CANCELLED'}

        # Remove the temporary effect object
        try:
            bpy.data.objects.remove(effect_obj, do_unlink=True)
        except Exception:
            pass

        self.report({'INFO'}, "Effect applied")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(EFFECTADDER_OT_apply_effect)


def unregister():
    bpy.utils.unregister_class(EFFECTADDER_OT_apply_effect)

