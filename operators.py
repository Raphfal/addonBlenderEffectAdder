import bpy

class MYADDON_OT_do_something(bpy.types.Operator):
    bl_idname = "myaddon.do_something"
    bl_label = "Do Something"

    def execute(self, context):
        print("Hello")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MYADDON_OT_do_something)

def unregister():
    bpy.utils.unregister_class(MYADDON_OT_do_something)
