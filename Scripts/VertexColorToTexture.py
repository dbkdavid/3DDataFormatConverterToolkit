import customtkinter as ctk
from tkinter import Tk
from tkinter.filedialog import askopenfilenames
import math
import os
import bpy

# configure appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")   

# configure window
root = ctk.CTk()
root.title("DBKTools :: VertexColorToTexture")

# define input and output file extensions
input_file_ext = "ply"
output_file_ext = "png"

def displaymessage(message):
	
	print(message)
	
	# update the message entry box
	prefix = ">>> "
	entry_message.delete(0, len(entry_message.get()))
	entry_message.insert(0, prefix + message)
	
	# update the UI
	root.update()

def selectfile():
	
	# display an open file dialog
	filename = askopenfilenames(filetypes=[("All Formats","*.*"), (input_file_ext.upper(),"*." + input_file_ext.upper())])
		
	# don't proceed if the file doesn't exist
	if not filename:
		return -1
	
	# format the list of file names as a comma-separated string
	parsed_filename = ""
	if len(filename) > 1:
		for file in filename:
			parsed_filename = parsed_filename + file + ", "
		parsed_filename = parsed_filename[:-2]
	else:
		parsed_filename = filename
	
	# set the entry box text to the file path
	entry_file.delete(0, len(entry_file.get()))
	entry_file.insert(0, parsed_filename)
	
	# display message
	displaymessage("Files selected: " + str(len(filename)))

def processfiles():
	
	# get the file path from the entry box
	input_filelist = entry_file.get()
	
	# remove the spaces
	input_filelist = input_filelist.replace(' ', '')
	
	# use the commas to convert the string to a list
	input_filelist = input_filelist.split(',')
	
	# check that the input file exists
	for input_file in input_filelist:
		if not (os.path.exists(input_file)):
			filename = input_file.split("/")[-1]
			displaymessage("The file '" + filename + "' does not exist.")
			return -1
		
	# check that the file is the correct type
	for input_file in input_filelist:
		file_ext = input_file.split(".")[-1]
		if file_ext.casefold() != input_file_ext.casefold():
			filename = input_file.split("/")[-1]
			displaymessage("The file '" + filename + "' is not a " + input_file_ext.upper() + " file.")
			return -1
	
	# check that the output file doesn't already exist
	for input_file in input_filelist:
		output_file = input_file.replace(input_file_ext, output_file_ext)
		if (os.path.exists(output_file)):
			filename = output_file.split("/")[-1]
			displaymessage("The file '" + filename + "' already exists.")
			return -1

	# convert the files
	for input_file in input_filelist:
		displaymessage("Converting files... " + str(input_filelist.index(input_file) + 1) + "/" + str(len(input_filelist)))
		convertfile(input_file)
	
	# display message
	output_path = '/'.join(input_filelist[0].split("/")[:-1])
	displaymessage("Files converted: " + output_path)

def convertfile(input_file):

	# Import Mesh
	# -----------------------------------------------

	# Set the file path to your PLY file
	#input_file = 'D:\\DavidBK\\WORKSPACE\\Projects\\TheGardenUnityDevelopment\\GYMS\\GardenPsdTerrain\\Meshes\\GardenPsdTerrain_VertexColors.ply'

	# Clear existing mesh objects from the scene (optional)
	bpy.ops.object.select_all(action='DESELECT')
	bpy.ops.object.select_by_type(type='MESH')
	bpy.ops.object.delete()

	# Import the PLY file
	bpy.ops.import_mesh.ply(filepath=input_file)

	# Select the imported object (the last created mesh)
	obj = bpy.context.active_object
	obj.select_set(True)
	bpy.context.view_layer.objects.active = obj

	# Rotate the mesh 90 degrees
	bpy.context.object.rotation_euler[0] = 90 * (math.pi / 180)
	
	
	# Create Material and Texture
	# -----------------------------------------------

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
	
	
	# Assign the Material
	# -----------------------------------------------

	# Create a new material slot for baking
	bpy.ops.object.material_slot_add()
	material_slot = obj.material_slots[0]

	# Assign the material to the first slot
	material_slot.material = new_material


	# Set Render Settings
	# -----------------------------------------------

	# Set render engine, device and bake type
	bpy.context.scene.render.engine = 'CYCLES'
	bpy.context.scene.cycles.device = 'GPU'
	bpy.context.scene.cycles.samples = 16
	bpy.context.scene.cycles.bake_type = 'EMIT'
	#bpy.context.scene.sequencer_colorspace_settings.name = "sRGB"
	bpy.context.scene.view_settings.view_transform = 'Standard'
	
	# Bake the Texture
	# -----------------------------------------------

	# Make the Texture node active
	node_tree.nodes.active = texture_node

	# Bake
	bpy.ops.object.bake(save_mode='EXTERNAL')
	
	# Make the output file path
	output_file = input_file.replace(input_file_ext, output_file_ext)
	
	# Save to File
	#image.save_render(filepath='D:\\DavidBK\\WORKSPACE\\Projects\\TheGardenUnityDevelopment\\GYMS\\GardenPsdTerrain\\Textures\\PythonBake.png')
	image.save_render(filepath=output_file)

# create main frame
frame = ctk.CTkFrame(master=root)
frame.pack(pady=20, padx=20, fill="both", expand=True)

# create title text
title = ctk.CTkLabel(master=frame, text="DBKTools :: VertexColorToTexture", font=("Cascadia Code", 24))
title.pack(pady=20, padx=10)

# define widget width
widget_width=500

# create open file button
button_open = ctk.CTkButton(master=frame, text="Open", command=selectfile, anchor="w", width=widget_width)
button_open.pack(pady=5, padx=10)

# create file path text field
entry_file = ctk.CTkEntry(master=frame, placeholder_text="File Path", width=widget_width)
entry_file.pack(pady=5, padx=10)

# create resolution option menu
option_menu = ctk.CTkOptionMenu(master=frame, values=["512", "1024", "2048", "4096"])
option_menu.pack(pady=5, padx=10)
option_menu.set("Resolution")

# create convert button
button_convert = ctk.CTkButton(master=frame, text="Convert", command=processfiles)
button_convert.pack(pady=20, padx=10)

# create console message text field
entry_message = ctk.CTkEntry(master=frame, fg_color="black", placeholder_text=">>>", placeholder_text_color="white", font=("Lucida Console", 10), width=widget_width)
entry_message.pack(pady=5, padx=10)

# execute the application
root.mainloop()