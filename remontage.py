"""

remontage.py

Some of the PIL code stolen from @dting on StackExchange.
https://stackoverflow.com/questions/30227466/combine-several-images-horizontally-with-python

"""


import sys
import os
import numpy as np
from PIL import Image


def main(tif_prefix):
	# Get all tif files in current directory
	cwd = os.getcwd()
	file_counter = 0
	names = []
	mdoc_file = ""
	for root, dirs, files in os.walk("."):
		for filename in files:
			if filename[-4:] == ".tif":
				if os.path.isfile(os.path.join(cwd, filename)):
					names.append(filename)
					file_counter += 1
			if filename.endswith(".st.mdoc"):
				if os.path.isfile(os.path.join(cwd, filename)):
					if len(mdoc_file) != 0:
						print("Multiple mdoc files found in this directory - please only have the tiff and mdoc files for one atlas in this directory.  Exiting...")
						exit()
					else:
						mdoc_file += filename
	
	# Read in the metadata file and parse -> hashmap of ID: x, y
	with open(mdoc_file, "r") as f:
		z_lines = f.readlines()
		z_map = parse_mdoc(z_lines, tif_prefix)

	# Interrogate
	xs = []
	ys = []
	for z in z_map:
		xs.append(z_map[z]["x"])
		ys.append(z_map[z]["y"])
	
	# Organize this into a montage pattern
	unique_x = list(sorted(set(xs)))
	unique_y = list(sorted(set(ys)))

	montage_pattern = np.zeros([len(unique_x), len(unique_y)], dtype=np.int32)
	
	for (ix, xval) in enumerate(unique_x):
		for (iy, yval) in enumerate(unique_y):
			found_flag = False
			for z in z_map:
				if (xval == z_map[z]["x"]) and (yval == z_map[z]["y"]):
					montage_pattern[ix, iy] = z
					found_flag = True
					break
			if found_flag == False:
				montage_pattern[ix, iy] = -1

	# I need a check for if a -1 if present in the montage pattern.  If so, I need to create a dummy image of same size
	# to populate this spot via np.zeros
	if -1 in montage_pattern:
		max_val = np.max(montage_pattern)
		with Image.open(z_map[max_val]["filename"]) as test_img:
			dummy_shape = test_img.size
			img_max_intensity = np.min(test_img)
		dummy_obj = np.ones([dummy_shape[1], dummy_shape[0]], dtype=np.uint32)
		dummy_obj[:] = img_max_intensity
		dummy_im = Image.fromarray(dummy_obj)
		dummy_im.save("dummy.tif")
	
	# Montage all the images together based on defined pattern
	# Build together into column strips
	column_strip_images = []
	for i in range(montage_pattern.shape[0]):
		files = []
		for idx in np.flip(montage_pattern[i, :]):
			if idx == -1:
				files.append(Image.open("dummy.tif"))
			else:
				files.append(Image.open(z_map[idx]["filename"]))
		widths, heights = zip(*(isize.size for isize in files))

		# Calculate appropriate offset
		raw_img_size = heights[0]
		montage_img_size = unique_y[1]
		montage_offset = raw_img_size - montage_img_size

		total_width = max(widths)
		max_height = sum(heights) - ((len(heights) - 1) * montage_offset)
		new_img = Image.new('I', (total_width, max_height))
		y_offset = 0
		for each_img in files:
			new_img.paste(each_img, (0, y_offset))
			y_offset += each_img.size[1] - montage_offset
		column_strip_images.append(new_img)

	# Join the column strips into a big image
	widths, heights = zip(*(isize.size for isize in column_strip_images))
	raw_img_width = widths[0]
	montage_img_size = unique_x[1]
	montage_offset = raw_img_width - montage_img_size
	total_width = sum(widths) - ((len(widths) - 1) * montage_offset)
	max_height = max(heights)
	new_img = Image.new('I', (total_width, max_height))
	x_offset = 0
	for csi in column_strip_images:
		new_img.paste(csi, (x_offset, 0))
		x_offset += csi.size[0] - montage_offset
	print("Saving montage out as jpg...")
	new_img.save("final_montage.tif")
	new_img_jpg = new_img.convert("RGB")
	new_img_jpg.save("final_montage.jpg")
	print("...done")


def parse_mdoc(lines, tif_prefix):
	""" Parses piece coordinates out of .st.mdoc file lines. """
	out_dict = dict()
	current_z_slice = -1

	for (i, line) in enumerate(lines):
		# Find a new zvalue and update the current z slice
		if line.startswith("[ZValue = "):
			idx = line.find("=") + 2
			back_idx = line.find("]", idx)
			substr = line[idx:back_idx]
			out_dict[int(substr)] = {}
			out_dict[int(substr)]["filename"] = tif_prefix+"."+pad_arb(int(substr), 3)+".tif"
			current_z_slice = int(substr)

		# If it's not a new z slice, look for PieceCoordinates and add to dictionary
		if line.startswith("PieceCoordinates = "): 
			idx = line.find("=") + 2
			vals = line[idx:].split(" ")
			out_dict[int(substr)]["x"] = int(vals[0])
			out_dict[int(substr)]["y"] = int(vals[1])

	return out_dict


def pad_arb(in_num, pad_len):
	""" Pads an integer to an arbitrary length for consistent string formatting. """
	in_str = str(in_num)
	while len(in_str) < pad_len:
		in_str = "0" + in_str
	return(in_str)


if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Check usage: foo.py tif_file_prefix")
		exit()
	else:
		main(sys.argv[1])

