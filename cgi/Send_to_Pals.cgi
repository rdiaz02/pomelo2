#!/usr/bin/python

####  Copyright (C)  2003-2005, Ramon Diaz-Uriarte <rdiaz02@gmail.com>,
####                 2005-2009, Edward R. Morrissey and 
####                            Ramon Diaz-Uriarte <rdiaz02@gmail.com> 

#### This program is free software; you can redistribute it and/or
#### modify it under the terms of the Affero General Public License
#### as published by the Affero Project, version 1
#### of the License.

#### This program is distributed in the hope that it will be useful,
#### but WITHOUT ANY WARRANTY; without even the implied warranty of
#### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#### Affero General Public License for more details.

#### You should have received a copy of the Affero General Public License
#### along with this program; if not, you can download if
#### from the Affero Project at http://www.affero.org/oagpl.html



import cgi
import os
import cgitb;cgitb.enable()
import sys

#################  Functions   ##################################################
def write_to_file(cgi_dict):
    """Write the cgi_dict values to be read by R later"""
    ## First define a set of predefined values. Will overwrite with
    ## stuff from the cgi, o.w. write those to the file
    maxUnadjp   = 0.05
    maxFDR      = 0.15
    minAbsObsrv = 0.0
    minObsrv    = -9999999999999
    maxObsrv    = 9999999999999
 
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
    
    heatmapOpts = open('Pals_Opts', mode = 'w')
    heatmapOpts.write('maxUnadjp\tmaxFDR\tminAbsObsrv\tminObsrv\tmaxObsrv\n')
    heatmapOpts.write(''.join([str(maxUnadjp), '\t', str(maxFDR), '\t',
                               str(minAbsObsrv), '\t', str(minObsrv), '\t',
			       str(maxObsrv),'\n']))
    heatmapOpts.close()


# Function that checks that nothing strange is being fed
def chk_form(form):
	try:
		dummy = float(form['below_unadj-p'].value)
		dummy = float(form['below_FDR'].value)
		dummy = float(form['above_abs_obs_stat'].value)
		dummy = float(form['above_obs_stat'].value)
		dummy = float(form['below_obs_stat'].value)
	except:
		print "Content-type: text/html;charset=utf-8\n\n"
		print "Sorry, you have entered an invalid value in one or more of the fields."
		sys.exit()

def create_html_table(gene_list,mini_list_template):
	list_of_genes = gene_list.split("\n")
	if len(list_of_genes[-1])<2:
		list_of_genes = list_of_genes[:-1]		
	html_list = []
	for gene in list_of_genes:
		html_row = "<tr><td>" + gene + "</td></tr>"
		html_list.append(html_row)
	#html_table = "<B> List of genes:</B><br>"
	html_table = "<table>\n" + '\n'.join(html_list) + "</table>\n"
	f=open(mini_list_template)
	template_mini_list = f.read()
	f.close()
	html_page = template_mini_list.replace("_LIST_",html_table)
	f=open("gene_list.html","w")
	f.write(html_page)
	f.close()	
	if gene_list.find("No genes") != -1:
		html_text = gene_list
	else:
		html_text = "With the parameters you have selected, you have created a list with <B>"
		html_text = html_text + str(len(list_of_genes)) + " genes</B>.<br> To see the list of genes "
		html_text = html_text + "<a href=\"#\" onClick=\"openList()\">click here</a>."
	return(	html_text)
	
def makePalsurl(tmp_dir):
	f=open("idtype")
	idtype = f.read().strip()
	f.close()
	f=open("organism")
	organism = f.read().strip()
	f.close()
	if (idtype != "None" and organism != "None"):
		url_org_id = "org=" + organism + "&idtype=" + idtype + "&"
	else:
		url_org_id = ""
	gene_list_file = "http://pomelo2.bioinfo.cnio.es/tmp/" + tmp_dir + "/gene.list.txt"
	data_file = "datafile=" + gene_list_file
	Pals_main_url = "http://pals.bioinfo.cnio.es?" + url_org_id + data_file
	return(Pals_main_url)
	
##################################################################################
form    = cgi.FieldStorage()
# tmp_dir just contains the random number
tmp_dir = form['tmp_dir'].value
whole_dir = "/http/pomelo2/www/tmp/" + tmp_dir
os.chdir(whole_dir)

list_template      = "/http/pomelo2/www/Pomelo2_html_templates/templ-Pals_list.html"
mini_list_template = "/http/pomelo2/www/Pomelo2_html_templates/templ-mini_list.html"

if not form.has_key("ajax"):
      f=open(list_template)
      template_Pals = f.read()
      f.close()
      pals_url = makePalsurl(tmp_dir)
      template_Pals = template_Pals.replace("_POMELO_PALS_REPLACE_",pals_url)
      template_Pals = template_Pals.replace("_TEMP_DIR_",tmp_dir)
      _tmp_route_ = "http://pomelo2.bioinfo.cnio.es/tmp/" + tmp_dir #+ "/pomelo2.GeneList.zip"
      template_Pals = template_Pals.replace("_TMP_ROUTE_", _tmp_route_)
      print "Content-type: text/html;charset=utf-8\n\n"
      print template_Pals
      sys.exit()
chk_form(form)
tmp = write_to_file(form)
r_file = "/http/pomelo2/cgi/Pals_gene_filter.R "


Rcommand = "cd " + tmp_dir + "; /var/www/bin/R-local-7-LAM-MPI/bin/R CMD BATCH --no-restore --no-readline --no-save -q " + r_file
Rrun = os.system(Rcommand)
f=open("gene.list.txt")
gene_list = f.read()
f.close()
html_list_table = create_html_table(gene_list,mini_list_template)
# Place an # at the beginnig of the list
gene_list = "# List created from Pomelo II output\n" + gene_list
f=open("gene.list.txt","w")
f.write(gene_list)
f.close()
zip_command =  "zip pomelo2.GeneList.zip gene.list.txt" 
dummy_var   = os.system(zip_command)
#####################################################

print "Content-type: text/html;charset=utf-8\n\n"
print html_list_table 



