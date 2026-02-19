import bpy


def scene_mesh_items(self, context):
    items = []
    for o in bpy.data.objects:
        if o.type == 'MESH':
            items.append((o.name, o.name, ""))
    if not items:
        items = [("NONE", "No mesh available", "")]
    return items


class EFFECTADDER_PT_main_panel(bpy.types.Panel):
    bl_label = "Effect Adder"
    bl_idname = "EFFECTADDER_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Effect Adder'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Target and Effect")
        layout.prop(scene, "ea_mesh_name", text="Mesh")
        layout.prop(scene, "ea_effect_type", text="Effect")

        layout.separator()
        layout.label(text="Parameters")
        layout.prop(scene, "ea_noise", slider=True)
        layout.prop(scene, "ea_rotation")
        layout.prop(scene, "ea_size")
        layout.prop(scene, "ea_thickness")

        layout.separator()
        op = layout.operator("effect_adder.apply_effect", text="Apply Effect")
        op.mesh_name = scene.ea_mesh_name
        op.effect_type = scene.ea_effect_type
        op.noise = scene.ea_noise
        op.rotation = scene.ea_rotation
        op.size = scene.ea_size
        op.thickness = scene.ea_thickness
        op.seed = scene.ea_seed


def register():
    bpy.types.Scene.ea_mesh_name = bpy.props.EnumProperty(
        name="Target Mesh",
        items=scene_mesh_items
    )
    bpy.types.Scene.ea_effect_type = bpy.props.EnumProperty(
        name="Effect Type",
        items=[('THUMB', 'Thumbprint', ''), ('EFFECT2', 'Effect 2', ''), ('EFFECT3', 'Effect 3', '')],
        default='THUMB'
    )
    bpy.types.Scene.ea_noise = bpy.props.FloatProperty(name="Noise", min=0.0, max=1.0, default=0.2)
    bpy.types.Scene.ea_rotation = bpy.props.FloatProperty(name="Rotation", min=0.0, max=360.0, default=0.0)
    bpy.types.Scene.ea_size = bpy.props.FloatProperty(name="Size", min=0.1, max=10.0, default=1.0)
    bpy.types.Scene.ea_thickness = bpy.props.FloatProperty(name="Thickness", min=0.0, max=2.0, default=0.2)
    bpy.types.Scene.ea_seed = bpy.props.IntProperty(name="Seed", default=0)

    bpy.utils.register_class(EFFECTADDER_PT_main_panel)


def unregister():
    bpy.utils.unregister_class(EFFECTADDER_PT_main_panel)

    del bpy.types.Scene.ea_mesh_name
    del bpy.types.Scene.ea_effect_type
    del bpy.types.Scene.ea_noise
    del bpy.types.Scene.ea_rotation
    del bpy.types.Scene.ea_size
    del bpy.types.Scene.ea_thickness
    del bpy.types.Scene.ea_seed

