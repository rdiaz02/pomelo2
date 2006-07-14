#!/usr/bin/python
import os
import read_input_ramon
import img_map

html_name = "heat.html"
form = {}

imagename = "First_image"
read_input_ramon.write_to_file(form, imagename)

Rcommand = "/usr/bin/R CMD BATCH --no-restore --no-readline --no-save -q new_heatmap.R 2> error.msg"

Rrun = os.system(Rcommand)

if os.path.exists('NoImagemapPossible'):
	file=open("heat_new.html","w")
	file.write("<p> Unable to draw heatmap, not enough data. (Maybe the default options are too restrictive for your data?.")
	file.write(" Click on 'Edit heatmap' and choose other options to obtain a heatmap.)</p>")
	file.close()
else:
        f=open("idtype")
	idtype = f.read().strip()
	f.close()
	f=open("organism")
	organism = f.read().strip()
	f.close()
	f=open("numberPixels")
	pixel_width = int(f.read().strip())
	f.close()
	img_map.change_image(html_name, pixel_width-10, idtype, organism)