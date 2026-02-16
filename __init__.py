bl_info = {
    "name": "Mon Addon",
    "blender": (3, 0, 0),
    "category": "Object",
}

from . import operators
from . import panel

def register():
    operators.register()
    panel.register()

def unregister():
    panel.unregister()
    operators.unregister()
