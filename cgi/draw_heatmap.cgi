#!/usr/bin/python
import cgi
import os
import cgitb;cgitb.enable()
import img_map
import random
import sys

sys.path.append("/home2/ramon/web-apps/web-apps-common")
from web_apps_config import R_pomelo_bin


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

# Function that writes the form options to a file to later be read by R
def write_to_file(cgi_dict, imagename):
    """Write the cgi_dict values to be read by R later"""
    ## First define a set of predefined values. Will overwrite with
    ## stuff from the cgi, o.w. write those to the file
    
    maxUnadjp   = 0.05
    maxFDR      = 0.15
    minAbsObsrv = 0.0
    minObsrv    = -9999999999999
    maxObsrv    = 9999999999999
    maxGenes    = 50
    size        = "auto"
    var_colour  = "gr"

    if ( cgi_dict.has_key("below_unadj-p") ):
	maxUnadjp = float( cgi_dict["below_unadj-p"].value )
    if ( cgi_dict.has_key("below_FDR") ):
	maxFDR = float( cgi_dict["below_FDR"].value )
    if ( cgi_dict.has_key("above_abs_obs_stat") ):
	minAbsObsrv = float( cgi_dict["above_abs_obs_stat"].value )
    if ( cgi_dict.has_key("above_obs_stat") ):
	minObsrv = float( cgi_dict["above_obs_stat"].value )
    if ( cgi_dict.has_key("below_obs_stat") ):
	maxObsrv = float( cgi_dict["below_obs_stat"].value )
    if ( cgi_dict.has_key("max_genes") ):
	maxGenes    = int( cgi_dict["max_genes"].value )
    if ( cgi_dict.has_key("colour") ):
	var_colour  = cgi_dict["colour"].value
    if ( cgi_dict.has_key("pixels") ):
	size        = cgi_dict["pixels"].value
    
    heatmapOpts = open('heatmapOpts', mode = 'w')
    heatmapOpts.write('maxUnadjp\tmaxFDR\tminAbsObsrv\tminObsrv\tmaxObsrv\tmaxGenes\tPixels\tColour\timg_name\n')
    heatmapOpts.write(''.join([str(maxUnadjp), '\t', str(maxFDR), '\t',
                               str(minAbsObsrv), '\t', str(minObsrv), '\t',
			       str(maxObsrv), '\t', str(maxGenes),'\t',
			       size,'\t',var_colour,'\t',imagename,'\n']))
    heatmapOpts.close()

#******************************************************************************************


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

imagename = "heatmap" + str(random.randint(1, 999999))
write_to_file(form,imagename)

Rcommand = "cd " + tmp_dir + "; " + R_pomelo_bin + " CMD BATCH --no-restore --no-readline --no-save -q new_heatmap.R 2> error.msg "
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
