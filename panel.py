import bpy

class MYADDON_PT_main_panel(bpy.types.Panel):
    bl_label = "Mon Addon"
    bl_idname = "MYADDON_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Mon Addon'

    def draw(self, context):
        layout = self.layout
        layout.operator("myaddon.do_something")

def register():
    bpy.utils.register_class(MYADDON_PT_main_panel)

def unregister():
    bpy.utils.unregister_class(MYADDON_PT_main_panel)
