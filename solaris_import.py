
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

# ---------- CREATE VARIABLES FROM INPUT ----------

# get full path of selected node
obj_path = selected[0].path()

# get name of selected node
obj_name = selected[0].name()

# ---------- MODIFY AND SETUP ----------

subdiv, input_strings = hou.ui.readMultiInput("Solaris Import", ("Name",), (), 
('Cancel', 'Import as Subdiv', 'Import',), hou.severityType.Message, 2, 
0, None, None, initial_contents=(obj_name,))

# if cancel or x are pressed, do not create the node
if subdiv == 0:
    exit()

# ---------- CREATE NEW NODE ----------

# create new node in solaris to hold geometry
sop_import = hou.node('/stage').createNode('sopimport', input_strings[0])

# variables for relevant parameters
sop_import.parm('soppath').set(obj_path)

# set subdiv values if enabled
if subdiv == 1:
    sop_import.parm('enable_polygonsassubd').set(1)
    sop_import.parm('polygonsassubd').set(1)

# print confirmation that the import worked
hou.ui.displayMessage("Geometry successfuly imported into Solaris.") 
