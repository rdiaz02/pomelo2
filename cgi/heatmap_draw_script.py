#!/usr/bin/python
import os
import img_map


#***********************************************************************************
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
#***********************************************************************************


html_name = "heat.html"
form = {}

imagename = "First_image"
write_to_file(form, imagename)

Rcommand = "/var/www/bin/R-local-7-LAM-MPI/bin/R CMD BATCH --no-restore --no-readline --no-save -q new_heatmap.R 2> error.msg"

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
        try:
            f=open("numberPixels")
        except:
            print "****####@@@@****  ERROR:         numberPixels NOT found, but NoImagemapPossible neither"
            print "               we are in " + os.getcwd()
	pixel_width = int(f.read().strip())
	f.close()
	img_map.change_image(html_name, pixel_width-10, idtype, organism)
