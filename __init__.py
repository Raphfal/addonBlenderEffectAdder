bl_info = {
    "name": "Effect Adder",
    "blender": (3, 0, 0),
    "category": "Modeling",
}

from . import operators
from . import panel

def register():
    operators.register()
    panel.register()

def unregister():
    panel.unregister()
    operators.unregister()
