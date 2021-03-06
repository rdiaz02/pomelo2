#!/usr/bin/python
import sys
import cgitb; cgitb.enable() ## comment out once debugged?

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
def used_covariables(test_type):
    if test_type=="Limma Anova test":
        try:
            f_covariables = open("COVARIABLES/chosen_covariables")
            covars_text   = f_covariables.read(); f_covariables.close()
            return_text   = ', '.join(covars_text.split())
        except:
            return_text = "No additional covariables have been used"
    else:
        return_text = "Selected test does not allow additional covariables"
    return(return_text)

        

def table_gen_sort(l1, l2, l3, l4, l5, l6, order, idtype, organism, test_type, fileout = 'tabla.html'):

    # If the test is Limma, we must add an extra field
    if is_limma:
        add_header = '<td width=100><b>B</b></td>' 
        add_column = '</td><td>'
    else:
        add_header = '' 
        add_column = ''
                 
    fout = open(fileout, mode = 'w')
    fout.write('Chosen test type: ' + test_type + '<br>' )
    fout.write(permut_text + '<br>')
    covariables_text = used_covariables(test_type)
    fout.write('Covariables used: ' + covariables_text + '<br>')
    fout.write('Class labels: <a href="./class_labels" target="classWindow">Click here</a><br>')
    fout.write('<br><table>')
   
    outstring = "<tr><td>&nbsp;</td><td width=150><b>Gene Name</b></td><td width=150><b>Row number</b></td><td width=150><b>unadj.p</b></td><td width=150><b>FDR_indep</b></td><td width=150><b>Obs_stat</b></td><td width=100><b>abs(Obs_stat)</b></td>" + add_header + "</tr>\n"
    fout.write(outstring)
    for i in range(len(df11)-14):

        # If the test belongs to Limma, then l7 contains B if not it will just be a list of empty strings
        outstring = ''.join(['<tr><td><b>',str(i+1),'&nbsp;&nbsp;&nbsp;',
			    '</b></td><td>', linkGene(l1[order[i]], idtype, organism),
			    '</td><td>', str(l2[order[i]]),
			    '</td><td>', for_print_p_value(l3[order[i]]),
			    '</td><td>', for_print_p_value(l4[order[i]]),
			    '</td><td>', str(round(l5[order[i]], 6)),
                            '</td><td>', str(round(l6[order[i]], 6)),
                            add_column , l7[order[i]],
                            '</td></tr>\n'])
        fout.write(outstring)
    fout.write('</table>')

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


f=open("idtype")
idtype = f.read().strip()
f.close()

f=open("organism")
organism = f.read().strip()
f.close()

# Los tests de limma deben empezar con "Limma " para que haga la tabla sacando la B
d={"t":"t-test","FisherIxJ":"Fisher IxJ","Anova":" Anova","Cox":"Cox model","Regres":"Regression","t_limma":"Limma t-test","t_limma_paired":"Limma paired t-test","Anova_limma":"Limma Anova test"}

f = open("testtype")
test_type = f.read().strip()
f.close()
test_type = d[test_type]

# Check to see if the test is limma t (we will need an extra field)
if test_type == 't_limma' or test_type == 't_limma_paired':
    is_limma= True
else:
    is_limma= False

df1 = open("multest_parallel.res", mode = 'r')
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
    if is_limma:
        aux_num = float(splitted[6])
        aux_num = str(round(aux_num, 6))
        l7.append(aux_num)
    else:
        l7.append("")

df1.close()


nameAscending     = permutation_indices(l1)
nameDescending    = permutation_indices_reverse(l1)
rowAscending      = permutation_indices(l2)
rowDescending     = permutation_indices_reverse(l2)
unadjpAscending   = permutation_indices(l3)
unadjpDescending  = permutation_indices_reverse(l3)
FDRAscending      = permutation_indices(l4)
FDRDescending     = permutation_indices_reverse(l4)
obsstatAscending  = permutation_indices(l5)
obsstatDescending = permutation_indices_reverse(l5)
absobsAscending   = permutation_indices(l6)
absobsDescending  = permutation_indices_reverse(l6)


table_gen_sort(l1, l2, l3, l4, l5, l6, nameAscending,  idtype, organism, test_type, fileout = "p.v.sort.name.a.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, nameDescending, idtype, organism, test_type, fileout = "p.v.sort.name.d.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, rowAscending,    idtype, organism, test_type, fileout = "p.v.sort.row.a.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, rowDescending,   idtype, organism, test_type, fileout = "p.v.sort.row.d.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, unadjpAscending,  idtype, organism, test_type, fileout = "p.v.sort.unadjp.a.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, unadjpDescending, idtype, organism, test_type, fileout = "p.v.sort.unadjp.d.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, FDRAscending,  idtype, organism, test_type, fileout = "p.v.sort.FDR.a.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, FDRDescending, idtype, organism, test_type, fileout = "p.v.sort.FDR.d.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, obsstatAscending,  idtype, organism, test_type, fileout = "p.v.sort.obss.a.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, obsstatDescending, idtype, organism, test_type, fileout = "p.v.sort.obss.d.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, absobsAscending,  idtype, organism, test_type, fileout = "p.v.sort.abso.a.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, absobsDescending, idtype, organism, test_type, fileout = "p.v.sort.abso.d.html")
