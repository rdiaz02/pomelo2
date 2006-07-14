#!/usr/bin/python
import os
import read_input
import img_map
from rpy import *
import Numeric
import whrandom

max_number_genes = "50"
html_name = "heat.html"
covariates, gene_names, header, results, result_row_id = read_input.covars_header_results("covariate", "class_labels", "multest_parallel.res")

pixel_width  = len(header)*10+700
pixel_height = len(gene_names)*20 #+ 20
if pixel_width< 700: pixel_width = 700
if pixel_height< 900: pixel_height = 900

f=open("idtype")
idtype = f.read().strip()
f.close()
f=open("organism")
organism = f.read().strip()
f.close()
form = {}

def_max_genes = 50
covariates, gene_names = read_input.filter_covars(covariates, gene_names, results, result_row_id, form, def_max_genes)

if len(covariates)>3:
	covariates_array = Numeric.array(covariates, Numeric.Float)
	r.library("imagemap")
	r.library("GDD")
	r.source("/http/pomelo2/cgi/rpy_source.R")
# 	imagename = "heatmap" + str(whrandom.randint(1, 999999))
	imagename = "First_image"

	r.heatimagemap(covariates_array, gene_names, header, pixel_height, pixel_width, html_name, imagename)
	img_map.change_image(html_name,pixel_width-10, idtype, organism)
#	***** Heatmap-imagemap is now heat_new.html


else:
	file=open("heat_new.html","w")
	file.write("<p> Unable to draw heatmap, not enough data. </p>")
	file.close()
