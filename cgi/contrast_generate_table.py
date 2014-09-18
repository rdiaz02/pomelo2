#!/usr/bin/python
# -*- mode: python; -*-
import sys
import os

## the .py files are called from deep down, in the
##  whatever/pomelo2/www/tmp/some_file
## sys.path.append("../../web-apps-common")
sys.path.append("../../../../web-apps-common")
from web_apps_config import pomelo_templates_dir

def permutation_indices(data):
    """ Title: list permutation order indices
    Submitter: Andrew Dalke
    # Based on a post by Peter Otten on comp.lang.python 2004/09/04.
    # This uses the 'key' option to sort and the 'sorted' function, both
    # new in Python 2.4.
    From python cookbook page """
    return sorted(range(len(data)), key = data.__getitem__)

def permutation_indices_reverse(data):
    """ Title: list permutation order indices
    Submitter: Andrew Dalke
    # Based on a post by Peter Otten on comp.lang.python 2004/09/04.
    # This uses the 'key' option to sort and the 'sorted' function, both
    # new in Python 2.4.
    From python cookbook page """
    return sorted(range(len(data)), key = data.__getitem__, reverse = True)

def for_print_p_value(x):
    if x < 1e-7:
        return '< 0.0000001'
    else:
        return str(round(x, 7))

# Function to generate covariables used text.
def used_covariables():
    try:
        f_covariables = open("COVARIABLES/chosen_covariables")
        covars_text   = f_covariables.read(); f_covariables.close()
        return_text   = ', '.join(covars_text.split())
    except:
        return_text   = "No additional covariables have been used"
    
    return(return_text)

def table_gen(l1, l2, l3, l4, l5, l6, order, idtype, organism, test_type):
    outstring ='Chosen test type: Class contrasts (Annova Limma) <br>'
    outstring = outstring +'Chosen contrast: ' + test_type + '<br>'
    covariables_text = used_covariables()
    outstring = outstring + 'Covariables used: ' + covariables_text + '<br><br><table>'
    
    outstring = outstring + "<tr><td>&nbsp;</td><td width=150><b>Gene Name</b></td><td width=150><b>Row number</b></td><td width=150><b>unadj.p</b></td><td width=150><b>FDR_indep</b></td><td width=150><b>Obs_stat</b></td><td width=100><b>abs(Obs_stat)</b></td></tr>\n" #<td width=100><b>B</b></td>
    for i in range(len(df11)-14):        
        outstring_aux = ''.join(['<tr><td><b>'  , str(i+1),'&nbsp;&nbsp;&nbsp;',
                                 '</b></td><td>', linkGene(l1[order[i]], idtype, organism),
                                 '</td><td>'    , str(l2[order[i]]),
                                 '</td><td>'    , for_print_p_value(l3[order[i]]),
                                 '</td><td>'    , for_print_p_value(l4[order[i]]),
                                 '</td><td>'    , str(round(l5[order[i]], 6)),
                                 '</td><td>'    , str(round(l6[order[i]], 6)),
#                                 '</td><td>'    , l7[order[i]],
                                 '</td></tr>\n'])
        outstring = outstring + outstring_aux
        
    outstring = outstring + '</table>'
    
    return(outstring)


def linkGene(geneName, idtype, organism):
    return geneName

# This is the old one, but we are not longer using idclight    
# def linkGene(geneName, idtype, organism):
#     if idtype == 'None' or organism == 'None':
#         return geneName
#     else:
# 	link_gn = ''.join(['http://idclight.bioinfo.cnio.es/IDClight.prog?idtype=',
#                         idtype, '&id=', geneName, '&internal=0&org=',
#                         organism,"\' target=\'icl_window\'"])
#         return ("<a href='" + link_gn + "'>" + geneName + "</a>")

        
####################################################################################################################
############################################ CODE STARTS HERE ######################################################
####################################################################################################################
tmpDir     = sys.argv[1]

f=open("idtype")
idtype = f.read().strip()
f.close()

f=open("organism")
organism = f.read().strip()
f.close()

f=open("contrast_classes")
contrast_classes = f.read().strip()
f.close()


df1 = open(contrast_classes + ".res", mode = 'r')
df11 = df1.read().splitlines()
permut_text = df11[7]


l1=[]
l2=[]
l3=[]
l4=[]
l5=[]
l6=[]
l7=[]

for i in range(14, len(df11)): ## skip first line
    splitted = df11[i].split('\t')
    l1.append(splitted[1])
    l2.append(int(splitted[0]))
    l3.append(float(splitted[2]))
    l4.append(float(splitted[3]))
    l5.append(float(splitted[4]))
    l6.append(float(splitted[5]))
    aux_num = float(splitted[6])
    aux_num = str(round(aux_num, 6))
    l7.append(aux_num)
    
df1.close()

FDRAscending = permutation_indices(l4)

html_table = table_gen(l1, l2, l3, l4, l5, l6, FDRAscending,
                       idtype, organism, contrast_classes)

# Read template file
tmpl_html = open(pomelo_templates_dir + "/templ_contrasts_indv.html","r")
html_page = tmpl_html.read()
tmpl_html.close()

# Create dummy html file with table
dummy_file = open(tmpDir + "dummy.html" , "w")
dummy_file.write(html_table)
dummy_file.close()

### The above seems wrong: this seems the correct version  FIXME
dummy_file = open(tmpDir + "/dummy.html" , "w")
dummy_file.write(html_table)
dummy_file.close()


# Change html to txt
html_to_text = "cd " + tmpDir + "; html2text -width 200 -nobs  -o " + contrast_classes + ".txt dummy.html; rm dummy.html" 
os.system(html_to_text)

html_page = html_page.replace("_TABLE_REPLACE_", html_table)
html_page = html_page.replace("_DOWNLOADFILE_" , contrast_classes + ".txt")

new_file_name = tmpDir + contrast_classes  + ".html"
html_file = open(new_file_name, "w")
html_file.write(html_page)
html_file.close()

### The above seems wrong: this seems the correct version  FIXME
new_file_name = tmpDir + "/" + contrast_classes  + ".html"
html_file = open(new_file_name, "w")
html_file.write(html_page)
html_file.close()
