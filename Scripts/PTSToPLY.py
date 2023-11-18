#exec(open('E:\\ASSETS\\Tools\\PTSToPLY\PTSToPLY.py').read())

import customtkinter as ctk
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import math
import os

# configure appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")   

# configure window
root = ctk.CTk()
#root.geometry("500x300")
root.title("DBKTools :: PTStoPLY")

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
	filename = askopenfilename()
		
	# if a file is selected
	if filename:
		
		# set the entry box text to the file path
		entry_file.delete(0, len(entry_file.get()))
		entry_file.insert(0, filename)
		
		# display message
		displaymessage("File selected.")

def convertfile():
	
	# get the file path from the entry box
	filepath = entry_file.get()
	
	# get the file directory
	filedirectory = ""
	filepathsplit = filepath.split("/")
	for i in range(len(filepathsplit)-1):
		filedirectory = filedirectory + filepathsplit[i] + "/"
	
	# get the file name and extension
	pts_filename = filepath.split("/")[-1]
	filename = pts_filename.split(".")[0]
	file_ext = pts_filename.split(".")[-1]
	
	# store the name of the new ply file
	ply_file = filedirectory + filename + ".ply"
	
	# check if the pts file exists
	if not (os.path.exists(filepath)):
		displaymessage("The selected file does not exist.")
		return -1
	
	# check if the pts file is a pts file
	pts_ext = "pts"
	if file_ext.casefold() != pts_ext.casefold():
		displaymessage("The selected file is not a PTS file.")
		return -1
	
	# check if the ply file exists
	if (os.path.exists(ply_file)):
		displaymessage("A PLY file already exists.")
		return -1
	
	# proceed to open the file
	displaymessage("Reading file...")
	
	# open the file and store each line in a new list
	open_file = list()
	with open(filepath, "r")as reader:
		for line in reader.readlines():
			open_file.append(line)
	
	# get the first line
	first_line = open_file[0]

	# split it based on the number of spaces and store each element in a new list
	x = first_line.split(" ")

	# if there is only one element in the first line
	if len(x) <= 1:
		# remove it from the list of lines
		open_file.pop(0)

	# print the number of lines in the file
	displaymessage("Vertex count: " + str(len(open_file)))

	# store the vertex count
	vertex_count = len(open_file)
	
	# define the header
	header_start = (
		"ply\n"
		+ "format ascii 1.0\n"
		+ "element vertex "
	)
	header_end = (
		"\n"
		+ "property float x\n"
		+ "property float y\n"
		+ "property float z\n"
		+ "property uchar intensity\n"
		+ "property uchar red\n"
		+ "property uchar green\n"
		+ "property uchar blue\n"
		+ "end_header\n\n"
	)
	
	# write the new file
	with open(ply_file, "x")as f:
		
		# write the header
		f.write(header_start + str(vertex_count) + header_end)
		
		# initialize a counter
		counter = 0
		
		# write the remaining lines
		for i in range(len(open_file)):
			
			# write the line
			f.write(open_file[i])
			
			# calculate progress in normalized range
			progress = i / len(open_file)
			
			# display progress
			if counter == 0:
				displaymessage("Writing file: " + str(math.floor(progress*100)) + " %...")
			
			# increment the counter
			counter += 1/len(open_file)
			
			# progress display frequency
			if counter >= 0.05:
				counter = 0

	displaymessage("File saved: " + ply_file)

# create main frame
frame = ctk.CTkFrame(master=root)
frame.pack(pady=20, padx=20, fill="both", expand=True)

# create title text
title = ctk.CTkLabel(master=frame, text="DBKTools :: PTStoPLY", font=("Cascadia Code", 24))
title.pack(pady=20, padx=10)

# define widget width
widget_width=500

# create open file button and file path text field
button_open = ctk.CTkButton(master=frame, text="Open", command=selectfile, anchor="w", width=widget_width)
button_open.pack(pady=5, padx=10)

entry_file = ctk.CTkEntry(master=frame, placeholder_text="File Path", width=widget_width)
entry_file.pack(pady=5, padx=10)

# create convert button
button_convert = ctk.CTkButton(master=frame, text="Convert", command=convertfile)
button_convert.pack(pady=20, padx=10)

# create console message text field
entry_message = ctk.CTkEntry(master=frame, fg_color="black", placeholder_text=">>>", placeholder_text_color="white", font=("Lucida Console", 10), width=widget_width)
entry_message.pack(pady=5, padx=10)

# execute the application
root.mainloop()