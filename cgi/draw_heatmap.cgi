#!/usr/bin/python
import cgi
import os
# import cgitb;cgitb.enable()
import read_input_ramon
import img_map
import whrandom
import sys

colourValues = ("rg","topo","gr")
sizeValues   = ("auto","700","900","1200","1600","2000")
################################ Function that checks that nothing strange is being fed
def chk_form(form):
	try:
		dummy = float(form['below_unadj-p'].value)
		dummy = float(form['below_FDR'].value)
		dummy = float(form['above_abs_obs_stat'].value)
		dummy = float(form['above_obs_stat'].value)
		dummy = float(form['below_obs_stat'].value)
		dummy = int(form['max_genes'].value)
	except:
		print "Content-type: text/html;charset=utf-8\n\n"
		print "Sorry, you have entered an invalid value in one or more of the fields."
		sys.exit()
		
	var_colour = form['colour'].value
	if var_colour not in colourValues:
		print "Content-type: text/html;charset=utf-8\n\n"
		print "A strange value has been fed for a fixed field. Please only enter valid data."
		sys.exit()
	var_size = form['pixels'].value
	if var_size not in sizeValues:
		print "Content-type: text/html;charset=utf-8\n\n"
		print "A strange value has been fed for a fixed field. Please only enter valid data."
		sys.exit()
##################################################################################



html_name = "heat.html"
form    = cgi.FieldStorage()
tmp_dir = form['tmp_dir'].value
os.chdir(tmp_dir)
chk_form(form)
f=open("idtype")
idtype = f.read().strip()
f.close()
f=open("organism")
organism = f.read().strip()
f.close()

imagename = "heatmap" + str(whrandom.randint(1, 999999))
tmp = read_input_ramon.write_to_file(form,imagename)

Rcommand = "cd " + tmp_dir + "; " + "/usr/bin/R CMD BATCH --no-restore --no-readline --no-save -q new_heatmap.R 2> error.msg "
Rrun = os.system(Rcommand)

if os.path.exists('NoImagemapPossible'):
	print "Content-type: text/html;charset=utf-8\n\n"
	print "Sorry, with these options there is not enough data to draw a heatmap."
	print "Change the options if you want to draw a heatmap."
else:
	f=open("numberPixels")
	pixel_width = int(f.read().strip())
	f.close()
        img_map.change_image(html_name, pixel_width-10, idtype, organism)
	file=open("heat_new.html")
	text_map1=file.read()
	file.close()
	print "Content-type: text/html;charset=utf-8\n\n"
	print text_map1
