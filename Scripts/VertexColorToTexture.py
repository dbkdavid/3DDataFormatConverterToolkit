import bpy
import math

#######################################
# Import Mesh
#######################################

# Set the file path to your PLY file
ply_file_path = 'D:\\DavidBK\\WORKSPACE\\Projects\\TheGardenUnityDevelopment\\GYMS\\GardenPsdTerrain\\Meshes\\GardenPsdTerrain_VertexColors.ply'

# Clear existing mesh objects from the scene (optional)
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete()

# Import the PLY file
bpy.ops.import_mesh.ply(filepath=ply_file_path)

# Select the imported object (the last created mesh)
obj = bpy.context.active_object
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

# Rotate the mesh 90 degrees
bpy.context.object.rotation_euler[0] = 90 * (math.pi / 180)


#######################################
# Create Material and Texture
#######################################

# Create a new material
new_material = bpy.data.materials.new(name="New_Material")

# Add the material to the current blend file
#bpy.context.collection.materials.link(new_material)

# Enable the use of shader nodes for the material
new_material.use_nodes = True

# Get the material's node tree
node_tree = new_material.node_tree

# Clear all nodes from the node tree
for node in node_tree.nodes:
	node_tree.nodes.remove(node)

# Add an Emission shader node
emission_node = node_tree.nodes.new(type='ShaderNodeEmission')
emission_node.location = (0, 0)

# Add a Material Output node
material_output_node = node_tree.nodes.new(type='ShaderNodeOutputMaterial')
material_output_node.location = (200, 0)

# Connect the Emission shader to the Material Output node
new_material.node_tree.links.new(emission_node.outputs["Emission"], material_output_node.inputs["Surface"])

# Create a new Color Attribute node
attribute_node = node_tree.nodes.new(type='ShaderNodeAttribute')
attribute_node.attribute_name = "Col"  # Replace with your desired attribute name
attribute_node.location = (-200, 0)

# Connect the Color Attribute to the Emission shader node
new_material.node_tree.links.new(attribute_node.outputs["Color"], emission_node.inputs["Color"])

# Create a new Texture node
texture_node = node_tree.nodes.new(type='ShaderNodeTexImage')
texture_node.location = (0, 300)

# Create a new image to store the baked texture
image_width = 1024  # Adjust as needed
image_height = 1024  # Adjust as needed
image_name = "Baked_Texture"  # Name of the image
image = bpy.data.images.new(image_name, width=image_width, height=image_height)

# Set the colorspace
image.colorspace_settings.name = 'sRGB' # 'Non-Color' 'Raw' 'Linear' 'sRGB' 'XYZ'


# Assign the image to the Texture node
texture_node.image = image


#######################################
# Assign the Material
#######################################

# Create a new material slot for baking
bpy.ops.object.material_slot_add()
material_slot = obj.material_slots[0]

# Assign the material to the first slot
material_slot.material = new_material


#######################################
# Set Render Settings
#######################################

# Set render engine, device and bake type
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'GPU'
bpy.context.scene.cycles.samples = 16
bpy.context.scene.cycles.bake_type = 'EMIT'
#bpy.context.scene.sequencer_colorspace_settings.name = "sRGB"
bpy.context.scene.view_settings.view_transform = 'Standard'

#######################################
# Bake the Texture
#######################################

# Make the Texture node active
node_tree.nodes.active = texture_node

# Bake
bpy.ops.object.bake(save_mode='EXTERNAL')

# Save to File
image.save_render(filepath='D:\\DavidBK\\WORKSPACE\\Projects\\TheGardenUnityDevelopment\\GYMS\\GardenPsdTerrain\\Textures\\PythonBake.png')