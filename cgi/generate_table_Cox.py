#!/usr/bin/python
import sys

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

def print_warning(x):
    if x == 0:
        return ''
    elif x == 1:
        return 'Coefficient may be infinite'
    elif x == 2:
        return 'Did not converge'
    elif x == 3:
        return 'Some other problem'
    
def table_gen_sort(l1, l2, l3, l4, l5, l6, l7,
                   order, idtype, organism, test_type, fileout = 'tabla.html'):
    fout = open(fileout, mode = 'w')
    fout.write('Chosen test type: ' + test_type + '<br>' )
    fout.write(permut_text + '<br>')
    fout.write('Covariables used: Selected test does not allow additional covariables<br>')
    fout.write('Survival time: <a href="./class_labels" target="classWindow">Click here</a><br>')
    fout.write('<br><table>')
 
    outstring = "<tr><td>&nbsp;</td><td width=150><b>Gene Name</b></td><td width=150><b>Row number</b></td><td width=150><b>unadj.p</b></td><td width=150><b>FDR_indep</b></td><td width=150><b>Obs_stat</b></td><td width=150><b>abs(Obs_stat)</b></td><td width=150><b>Warning</b></td></tr>\n"
    fout.write(outstring)
    for i in range(len(df11)-14):
        if (l3[order[i]] > 98):
            outstring = ''.join(['<tr><td><b>',str(i+1),'&nbsp;&nbsp;&nbsp;',
                                 '</b></td><td>', linkGene(l1[order[i]], idtype, organism),
                                 '</td><td>', str(l2[order[i]]),
                                 '</td><td>', 'NA',
                                 '</td><td>', 'NA',
                                 '</td><td>', 'NA',
                                 '</td><td>', 'NA',
                                 '</td><td>',print_warning(l7[order[i]]),
                                 '</td></tr>\n'])
        else:
            outstring = ''.join(['<tr><td><b>',str(i+1),'&nbsp;&nbsp;&nbsp;',
                                 '</b></td><td>', linkGene(l1[order[i]], idtype, organism),
                                 '</td><td>', str(l2[order[i]]),
                                 '</td><td>', for_print_p_value(l3[order[i]]),
                                 '</td><td>', for_print_p_value(l4[order[i]]),
                                 '</td><td>', str(round(l5[order[i]], 6)),
                                 '</td><td>', str(round(l6[order[i]], 6)),
                                 '</td><td>',print_warning(l7[order[i]]),                             
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

d={"t":"t-test","FisherIxJ":"Fisher IxJ","Anova":" Anova","Cox":"Cox model","Regres":"Regression"}
f = open("testtype")
test_type = f.read().strip()
f.close()
test_type = d[test_type]
# print idtype + "\n" + organism
# idtype = sys.argv[1]
# organism = sys.argv[2]

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
    l7.append(float(splitted[6]))


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


table_gen_sort(l1, l2, l3, l4, l5, l6, l7, nameAscending,  idtype, organism, test_type, fileout = "p.v.sort.name.a.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, l7, nameDescending, idtype, organism, test_type, fileout = "p.v.sort.name.d.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, l7, rowAscending,    idtype, organism, test_type, fileout = "p.v.sort.row.a.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, l7, rowDescending,   idtype, organism, test_type, fileout = "p.v.sort.row.d.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, l7, unadjpAscending,  idtype, organism, test_type, fileout = "p.v.sort.unadjp.a.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, l7, unadjpDescending, idtype, organism, test_type, fileout = "p.v.sort.unadjp.d.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, l7, FDRAscending,  idtype, organism, test_type, fileout = "p.v.sort.FDR.a.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, l7, FDRDescending, idtype, organism, test_type, fileout = "p.v.sort.FDR.d.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, l7, obsstatAscending,  idtype, organism, test_type, fileout = "p.v.sort.obss.a.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, l7, obsstatDescending, idtype, organism, test_type, fileout = "p.v.sort.obss.d.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, l7, absobsAscending,  idtype, organism, test_type, fileout = "p.v.sort.abso.a.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, l7, absobsDescending, idtype, organism, test_type, fileout = "p.v.sort.abso.d.html")
