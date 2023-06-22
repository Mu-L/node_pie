import bpy
from bpy.types import UILayout
from .npie_constants import NODE_DEF_DIR
from .npie_helpers import get_prefs


def context_menu_draw(self, context):
    prefs = get_prefs(context)
    if not prefs.npie_dev_extras:
        return
    layout: UILayout = self.layout
    layout.separator()
    layout.label(text="Node Pie Utiltities:", icon="NODE")
    op = layout.operator("node_pie.open_definition_file", text="Open example definition file")
    op.example = True

    file = NODE_DEF_DIR / f"{context.space_data.tree_type}.jsonc"
    word = "Open" if file.exists() else "Create"
    op = layout.operator("node_pie.open_definition_file", text=f"{word} definition file for this node tree type")
    op.example = False
    layout.operator("node_pie.copy_nodes_as_json")


def register():
    bpy.types.NODE_MT_context_menu.append(context_menu_draw)


def unregister():
    bpy.types.NODE_MT_context_menu.remove(context_menu_draw)