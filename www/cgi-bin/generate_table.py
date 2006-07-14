#!/usr/bin/python2.4
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
def table_gen_sort(l1, l2, l3, l4, l5, l6, order, idtype, organism, fileout = 'tabla.html'):
    fout = open(fileout, mode = 'w')
    fout.write('<table>')
 
    outstring = "<tr><td width=150>Gene Name</td><td width=150>Row number</td><td width=150>unadj.p</td><td width=150>FDR_indep</td><td width=150>Obs_stat</td><td width=100>abs(Obs_stat)</td></tr>\n"
    fout.write(outstring)
    for i in range(len(df11)-14):
        outstring = ''.join(['<tr><td>', linkGene(l1[order[i]], idtype, organism),
			    '</td><td>', str(l2[order[i]]),
			    '</td><td>', for_print_p_value(l3[order[i]]),
			    '</td><td>', str(round(l4[order[i]], 6)),
			    '</td><td>', str(round(l5[order[i]], 6)),
                            '</td><td>', str(round(l6[order[i]], 6)), '</td></tr>\n'])
        fout.write(outstring)
    fout.write('</table>')


def linkGene(geneName, idtype, organism):
    if idtype == 'None' or organism == 'None':
        return geneName
    else:
	link_gn = ''.join(['http://idclight.bioinfo.cnio.es/IDClight.prog?idtype=',
                        idtype, '&id=', geneName, '&internal=0&org=',
                        organism])
        return ("<a href='" + link_gn + "'>" + geneName + "</a>")


f=open("idtype")
idtype = f.read().strip()
f.close()

f=open("organism")
organism = f.read().strip()
f.close()
# print idtype + "\n" + organism
# idtype = sys.argv[1]
# organism = sys.argv[2]

df1 = open("multest_parallel.res", mode = 'r')
df11 = df1.read().splitlines()


l1=[]
l2=[]
l3=[]
l4=[]
l5=[]
l6=[]

for i in range(14, len(df11)): ## skip first line
    splitted = df11[i].split('\t')
    l1.append(splitted[1])
    l2.append(int(splitted[0]))
    l3.append(float(splitted[2]))
    l4.append(float(splitted[3]))
    l5.append(float(splitted[4]))
    l6.append(float(splitted[5]))


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


table_gen_sort(l1, l2, l3, l4, l5, l6, nameAscending,  idtype, organism, fileout = "p.v.sort.name.a.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, nameDescending, idtype, organism, fileout = "p.v.sort.name.d.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, rowAscending,    idtype, organism, fileout = "p.v.sort.row.a.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, rowDescending,   idtype, organism, fileout = "p.v.sort.row.d.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, unadjpAscending,  idtype, organism, fileout = "p.v.sort.unadjp.a.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, unadjpDescending, idtype, organism, fileout = "p.v.sort.unadjp.d.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, FDRAscending,  idtype, organism, fileout = "p.v.sort.FDR.a.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, FDRDescending, idtype, organism, fileout = "p.v.sort.FDR.d.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, obsstatAscending,  idtype, organism, fileout = "p.v.sort.obss.a.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, obsstatDescending, idtype, organism, fileout = "p.v.sort.obss.d.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, absobsAscending,  idtype, organism, fileout = "p.v.sort.abso.a.html")
table_gen_sort(l1, l2, l3, l4, l5, l6, absobsDescending, idtype, organism, fileout = "p.v.sort.abso.d.html")