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
root.title("DBKTools :: OBJToFBX")

# define input and output file extensions
input_file_ext = "obj"
output_file_ext = "fbx"

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

	# Clear existing objects from the scene
	bpy.ops.object.select_all(action='DESELECT')
	bpy.ops.object.select_by_type(type='MESH')
	bpy.ops.object.delete()

	# Import the file
	bpy.ops.wm.obj_import(filepath=input_file)

	# Rotate the object 90 degrees in the X-axis
	bpy.context.object.rotation_euler = (math.radians(90), 0, 0)
	
	# Select the imported mesh object
	obj = bpy.context.selected_objects[0]
	obj.select_set(True)
	bpy.context.view_layer.objects.active = obj
	
	# Make the output file path
	output_file = input_file.replace(input_file_ext, output_file_ext)
	
	# Export the selected object as FBX
	bpy.ops.export_scene.fbx(filepath=output_file, use_selection=True, global_scale=0.01)

# create main frame
frame = ctk.CTkFrame(master=root)
frame.pack(pady=20, padx=20, fill="both", expand=True)

# create title text
title = ctk.CTkLabel(master=frame, text="DBKTools :: OBJToFBX", font=("Cascadia Code", 24))
title.pack(pady=20, padx=10)

# define widget width
widget_width=500

# create open file button and file path text field
button_open = ctk.CTkButton(master=frame, text="Open", command=selectfile, anchor="w", width=widget_width)
button_open.pack(pady=5, padx=10)

entry_file = ctk.CTkEntry(master=frame, placeholder_text="File Path", width=widget_width)
entry_file.pack(pady=5, padx=10)

# create convert button
button_convert = ctk.CTkButton(master=frame, text="Convert", command=processfiles)
button_convert.pack(pady=20, padx=10)

# create console message text field
entry_message = ctk.CTkEntry(master=frame, fg_color="black", placeholder_text=">>>", placeholder_text_color="white", font=("Lucida Console", 10), width=widget_width)
entry_message.pack(pady=5, padx=10)

# execute the application
root.mainloop()