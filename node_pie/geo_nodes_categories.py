# from __future__ import annotations
# import ast
# import json
# from pprint import pprint
# import bpy
# from dataclasses import dataclass
# from pathlib import Path
# import re

# from .npie_ui import NodeCategory, NodeItem, Separator
# from .npie_constants import NODE_DEF_DIR

# geo_nodes_categories = {}
# geo_nodes_menus = {}
# all_geo_nodes = {}


# def main():
#     """Due to a change in the way geometry nodes generates the add menu in 3.4, the old method of using
#     noditems_utils to get the node categories and items will no longer work
#     (which I'm not too happy about, as there's no other official way to get the same information).
#     I made a devtalk post, but that hasn't really gone anywhere unfortunately:
#     https://devtalk.blender.org/t/nodeitems-utils-module-deprecated-in-3-4-with-no-obvious-alternative.
#     So as a kinda shitty workaround, this parses the python file that defines the menu,
#     and extracts the node items and categories. This isn't ideal, as it's likely to be broken if the file is changed,
#     but it's the best solution I have :(
        
#     Update: I have given up trying to parse the files, as it keeps changing each time making things more difficult.
#     Instead this now just uses a config file to store the layout of the pie menu. This is stable, but has the downside
#     of needing to be updated manually to include new nodes with every blender version. Oh well, can't say I didn't try."""

#     scripts_path = bpy.utils.resource_path("LOCAL")
#     script_path = Path(scripts_path) / "scripts" / "startup" / "bl_ui" / "node_add_menu_geometry.py"

#     with open(script_path, "r") as f:
#         text = f.readlines()

#     bl_version = bpy.app.version

#     if bl_version >= (3, 5, 0):
#         return

#         # Load config file
#         files = {}
#         for file in (NODE_DEF_DIR).iterdir():
#             if file.is_file() and file.suffix == ".jsonc" and file.name.startswith("GeometryNodeTree_"):
#                 files[file.stem.split("_")[-1]] = file

#         # Load the latest version
#         version = int(f"{bl_version[0]}{bl_version[1]}")
#         while True:
#             try:
#                 def_path = files[str(version)]
#                 break
#             except KeyError:
#                 version -= 1
#                 if version < 0:
#                     break
#                 continue

#         with open(def_path, "r") as f:
#             data = json.load(f)

#         for cat_idname, cat in data.items():
#             items = []
#             for nodeitem in cat["items"]:
#                 if nodeitem["name"] == "sep":
#                     items.append(Separator())
#                     continue
#                 item = NodeItem(nodeitem["name"], nodeitem["identifier"])
#                 if settings := nodeitem.get("settings"):
#                     item.settings = settings
#                 items.append(item)
#                 all_geo_nodes[nodeitem["identifier"]] = item
#             category = NodeCategory(cat["name"], items)

#             geo_nodes_categories[cat["name"]] = category

#         # Check to see if there are any new nodes not in pie menu. NOT FOOLPROOF!
#         excluded = {"GeometryNodeViewer", "GeometryNodeGroup", "GeometryNodeCustomGroup"}

#         available_nodes = {node.bl_rna.identifier for node in bpy.types.GeometryNode.__subclasses__()}
#         available_nodes |= {node.bl_rna.identifier for node in bpy.types.FunctionNode.__subclasses__()}
#         missing_nodes = available_nodes - set(all_geo_nodes.keys()) - excluded
#         if missing_nodes:
#             print()
#             print(
#                 f"Node Pie Warning! There are {len(missing_nodes)} new nodes available that are not displayed in the Node Pie Menu:"
#             )
#             pprint(missing_nodes)
#             print()

#     elif False:
#         # Horrible code to try and parse the menu definition file.
#         # Keeping it around just in case

#         menus = {}

#         @dataclass
#         class Menu():

#             idname: str
#             label: str
#             children: list
#             nodes: list

#         # category_idname_pattern = re.compile("bl_idname\s*=\s*\"([^\"]*)\"")
#         file = ast.parse("\n".join(text))
#         for node in file.body:

#             # Find all of the menu class definitions
#             if isinstance(node, ast.ClassDef) and node.bases and "Menu" in node.bases[0].id:
#                 idname = ""
#                 label = ""
#                 nodes = []
#                 children = []

#                 for class_node in node.body:

#                     # Find the label and idname
#                     if isinstance(class_node, ast.Assign):
#                         var_name = class_node.targets[0].id
#                         if var_name == "bl_idname":
#                             idname = class_node.value.value
#                         elif var_name == "bl_label":
#                             label = class_node.value.value

#                 if not label:
#                     continue

#                 for class_node in node.body:
#                     if isinstance(class_node, ast.FunctionDef) and class_node.name == "draw":
#                         for draw_node in class_node.body:
#                             if isinstance(draw_node, ast.Expr) and isinstance(draw_node.value, ast.Call):
#                                 call = draw_node.value
#                                 call_name = call.func.attr  # The name of the function being called
#                                 # print(call_name)
#                                 if call_name == "add_node_type":
#                                     node_idname = call.args[1].value
#                                     node_label = getattr(bpy.types, node_idname).bl_rna.name
#                                     nodes.append(NodeItem(node_label, node_idname))
#                                 if call_name == "menu":
#                                     child_name = call.args[0].value
#                                     # print(label, child_name)
#                                     children.append(child_name)
#                                     # print(call.args[0].value)

#                 # cat = geo_nodes_categories.get(label, NodeCategory(label, []))
#                 # cat.nodeitems.extend(nodes)
#                 # geo_nodes_categories[label] = cat

#                 all_geo_nodes.update({n.nodetype: n for n in nodes})
#                 menu = Menu(idname, label, children, nodes)
#                 geo_nodes_menus[idname] = menu

#                 # print(label, idname)
#                 # pprint(nodes)

#         exclude = {}

#         geo_nodes_categories.clear()
#         # print(geo_nodes_menus.keys())
#         for menu in geo_nodes_menus.values():
#             # if menu.children:
#             # print(menu.label)
#             # print(menu.children)
#             # if menu.label in exclude:
#             # print(menu.label)
#             # continue

#             children = []
#             for m in menu.children:
#                 m = geo_nodes_menus[m]
#                 children.append(NodeCategory(m.label, m.nodes))

#             #     # print(m)
#             #     # if m.label in exclude:
#             #     # continue
#             #     nodes.extend(m.nodes)

#             # print(nodes)
#             # geo_nodes_categories[menu.label] = NodeCategory(menu.label, nodes)
#             # nodes = [n for m in menu.children for n in geo_nodes_menus[m].nodes]
#             # print(nodes)
#             nodes.extend(menu.nodes)
#             geo_nodes_categories[menu.label] = NodeCategory(menu.label, menu.nodes, children)

#         # pprint(geo_nodes_categories)

#     else:

#         # https://regex101.com/r/cVXk6l/1
#         category_label_pattern = re.compile("bl_label\s*=\s*\"([^\"]*)\"")
#         node_type_pattern = re.compile("node_add_menu\.add_node_type\(.*, \"([^\"]*)\"")

#         category = ""
#         for line in text:
#             match = re.findall(category_label_pattern, line)
#             if match and match[0] != '':
#                 category = match[0]
#                 continue
#             match = re.findall(node_type_pattern, line)
#             if match:
#                 cat = geo_nodes_categories.get(category, NodeCategory(category, []))
#                 node_idname = match[0]
#                 label = getattr(bpy.types, node_idname).bl_rna.name
#                 cat.nodes.append(NodeItem(label, node_idname))
#                 geo_nodes_categories[category] = cat


# if bpy.app.version >= (3, 4, 0):
#     bpy.app.timers.register(main)
#     # main()
