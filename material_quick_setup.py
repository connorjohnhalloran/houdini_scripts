
# get current selection
selected = hou.selectedNodes()

# ---------- CHECK IF INPUT IS VALID ----------

# make sure a node is selected
if selected.__len__() == 0:
    hou.ui.displayMessage("ERROR: No node selected.")
    exit()

# make sure no more than one node is selected
if selected.__len__() > 1:
    hou.ui.displayMessage("ERROR: Too many nodes selected. Select a single node.")
    exit()

# get full path of selected node
mat_path = selected[0].path()

# ---------------------- INITIAL PROCESSING ------------------------

# regular expression library, needed for regular expression check for UDIM tile number
import re

# file select
files = hou.ui.selectFile(None, 'Select textures', True, hou.fileType.Any, None, None, True, False, hou.fileChooserMode.Read)

if len(files) == 0:
    exit()

# split file selection into array of separate file paths
strings = files.split(" ; ")


# ---------------------- ISOLATE FILE NAMES ------------------------

# go through a string backward to find the first /, which is where the file name stops
name_base = ""
for char in reversed(strings[0]):
    if char == '/':
        break
    name_base += char

    
# reverse string to correct order
name_base = name_base[::-1]

# get base path (ie D:/3D/Projects ...)
# needed for getting all file names due to variable length
base_path = strings[0][:-(len(name_base))]

# create new list with just file names in it
file_names = []
for string in strings:
    file_names.append(string[len(base_path):])


# ----------------- CHECK FOR UDIM SIGNIFIERS ---------------------- 

final_file_names = []

# find ${F} style UDIM signifier
uses_udims = False
for string in file_names:
    index = string.find('${F}')
    if index != -1:
        uses_udims = True
        before = string[:index]
        after = string[index + 4:]
        string = before + "<UDIM>" + after
        final_file_names.append(string)

# if it couldn't find ${F} style, check for 1001, 1002 setup in name
if uses_udims == False:
    for string in file_names:
        result = re.search(r'1[0-9][0-9][0-9]', string)
        if result != None:
            uses_udims = True
            before = string[:result.start()]
            after = string[result.start() + 4:]
            string = before + "<UDIM>" + after
            final_file_names.append(string)

# if both UDIM checks don't find anything, just copy the file names into the final list.
if uses_udims == False:
    for string in file_names:
        final_file_names.append(string)

# ----------------- CHECK FOR SHADER MAPS ----------------------        

# potential different names that are checked
diffuse_strings = { 'diffuse', 'basecolor', 'base_color', 'albedo', 'color', 'diffusecolor', 'diffuse_color' }
rough_strings = { 'roughness', 'rough' }
spec_strings = { 'specular', 'spec' }
normal_strings = { 'normal', 'norm' }
height_strings = { 'height', 'bump', 'displacement', 'disp', 'disp' }

diffuse_path = ''
rough_path = ''
spec_path = ''
normal_path = ''
height_path = ''

for string in final_file_names:
    for diff in diffuse_strings:
        index = string.lower().find(diff)
        if index != -1:
            diffuse_path = base_path + string
            break

for string in final_file_names:
    for rough in rough_strings:
        index = string.lower().find(rough)
        if index != -1:
            rough_path = base_path + string
            break

for string in final_file_names:
    for spec in spec_strings:
        index = string.lower().find(spec)
        if index != -1:
            spec_path = base_path + string
            break
            
for string in final_file_names:
    for norm in normal_strings:
        index = string.lower().find(norm)
        if index != -1:
            normal_path = base_path + string
            break

for string in final_file_names:
    for height in height_strings:
        index = string.lower().find(height)
        if index != -1:
            height_path = base_path + string
            break

# ---------------- SHADER CREATION AND CONFIGURATION ------------------

#mat_path = '/stage/materiallibrary1'
#mat_path = '/mat'

# create subnet
subnet_node = hou.node(mat_path).createNode('subnet', 'material_quick_setup')

# create reference to inside the subnet
inside_subnet_path = mat_path + '/' + subnet_node.name()

# create reference to output node for connection purposes
output_node_path = inside_subnet_path + '/suboutput1'
output_node = hou.node(output_node_path)

# create and connect main shader to output
shader_node = hou.node(inside_subnet_path).createNode('pxrsurface::22')
output_node.setInput(0, shader_node)

# create and connect displace node to output
disp_node = hou.node(inside_subnet_path).createNode('pxrdisplace::22')
disp_node.parm('dispAmount').set(0.1)
output_node.setInput(1, disp_node)


# ----- DIFFUSE -----
if len(diffuse_path) > 0:
    diffuse_tex_node = hou.node(inside_subnet_path).createNode('pxrtexture::22', 'diffuse')
    diffuse_tex_node.parm('filename').set(diffuse_path)
    diffuse_tex_node.parm('linearize').set(1)
    if uses_udims:
        diffuse_tex_node.parm('atlasStyle').set(1)
    shader_node.setInput(2, diffuse_tex_node)

# ----- ROUGHNESS -----
if len(rough_path) > 0:
    rough_tex_node = hou.node(inside_subnet_path).createNode('pxrtexture::22', 'roughness')
    rough_tex_node.parm('filename').set(rough_path)
    if uses_udims:
        rough_tex_node.parm('atlasStyle').set(1)
    shader_node.setInput(14, rough_tex_node, 1)

# ----- SPECULAR -----
if len(rough_path) > 0:
    spec_tex_node = hou.node(inside_subnet_path).createNode('pxrtexture::22', 'specular')
    spec_tex_node.parm('filename').set(spec_path)
    spec_tex_node.parm('linearize').set(1)
    if uses_udims:
        spec_tex_node.parm('atlasStyle').set(1)
    shader_node.setInput(9, spec_tex_node)
    
# ----- NORMAL -----
if len(normal_path) > 0:
    normal_tex_node = hou.node(inside_subnet_path).createNode('pxrnormalmap::22', 'normal')
    normal_tex_node.parm('filename').set(normal_path)
    normal_tex_node.parm('bumpScale').set(.3)
    normal_tex_node.parm('orientation').set(1)
    if uses_udims:
        normal_tex_node.parm('atlasStyle').set(1)
    shader_node.setInput(94, normal_tex_node)
    
# ----- HEIGHT -----
if len(height_path) > 0:
    height_tex_node = hou.node(inside_subnet_path).createNode('pxrtexture::22', 'height')
    height_tex_node.parm('filename').set(height_path)
    if uses_udims:
        height_tex_node.parm('atlasStyle').set(1)
    disp_node.setInput(1, height_tex_node, 1)

# clean up node layout
subnet_node.layoutChildren()
