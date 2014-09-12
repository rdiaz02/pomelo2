#!/usr/bin/python

def red_green(value, FDR_limit, text_small, text_big):
    num     = float(value)
    abs_num = abs(num)
    if abs_num < FDR_limit:
        if num < 0.:
            table_cell = "<td><font color='red'>" + text_small + "</font></td>"
            venn_cell  = "-1"
        elif num > 0.:
            table_cell = "<td><font color='green'>" + text_big   + "</font></td>"
            venn_cell  = "1"
    else:
#        table_cell = "<td>Similar expression</td>"
        table_cell = "<td>-</td>"
        venn_cell  = "0"

    return table_cell, venn_cell

def line_to_html(line, FDR_limit, text_small, text_big, idtype, organism):
    elements = line.split("\t")
    html_line = ["<tr><td>",linkGene(elements[1], idtype, organism),"</td>"]
    venn_line = []
    for j in range(len(elements)-2):
        cell_text,venn_cell =  red_green(elements[j+2], FDR_limit, text_small[j], text_big[j])
        html_line.append(cell_text)
        venn_line.append(venn_cell)

 #   non_diff = html_line.count("<td>Similar expression</td>")
    non_diff = html_line.count("<td>-</td>")
    html_line.append("</tr>")
    venn_line[-1]= venn_line[-1] + "\n"
    if non_diff==(len(elements)-2):
        html_line=[""]

    return html_line, venn_line

def linkGene(geneName, idtype, organism):
    return geneName

# This is the old one, but we are not longer using idclight    
# def linkGene(geneName, idtype, organism):
#     if idtype == 'None' or organism == 'None':
#         return geneName
#     else:
# 	link_gn = ''.join(['http://idclight.bioinfo.cnio.es/IDClight.prog?idtype=',
#                         idtype, '&id=', geneName, '&internal=0&org=',
#                         organism, "\' target=\'icl_window\'"])
#         return ("<a href='" + link_gn + "'>" + geneName + "</a>")

def parse_contrasts(contr_text_lines, FDR_limit, idtype, organism):
    #class_contrasts = contr_text_lines[0].split("\t")
    class_contrasts = contr_text_lines[0]
    # Remove Class from class compare string
    class_contrasts = class_contrasts.replace("Class","")
    class_contrasts = class_contrasts.split("\t")
    cell_big_text   = []
    cell_small_text = []
    header_text     = []
    
    # Build cell text vectors and header vector
    for clss_cntr in class_contrasts:
        table_header     = clss_cntr.replace("-"," vs ")
        table_cell_big   = clss_cntr.replace("-"," > ")
        table_cell_small = clss_cntr.replace("-"," < ")
        cell_big_text.append(table_cell_big)
        cell_small_text.append(table_cell_small)
        header_text.append(table_header)
    
    # Remove first element from text
    cell_big_text   = cell_big_text[1:]
    cell_small_text = cell_small_text[1:]
    venn_table = header_text[1:]
    
    # Build html table header
    html_table = "<table><tr>"
    for element in header_text:
        html_table = html_table + "<td width=150><b>" + element + "</b></td>"
        
    html_table = html_table + "</tr>"
    venn_table = '\t'.join(venn_table)
    # Build body
    for i in range(len(contr_text_lines)-1):
        html_line, venn_line  = line_to_html(contr_text_lines[i+1], FDR_limit, cell_small_text, cell_big_text, idtype, organism)
        venn_table = venn_table + '\t'.join(venn_line)
        html_table = html_table + ''.join(html_line)
            
    html_table = html_table  + "</table>"
    f=open("venncontrsTable","w")
    f.write(venn_table)
    f.close()
    return html_table

def make_html_table():
    f=open("idtype");idtype = f.read().strip();f.close()
    f=open("organism");organism = f.read().strip();f.close()
    try:
        f=open("max_FDR");FDR_limit = f.read().strip();f.close()
        FDR_limit = float(FDR_limit)
    except:
        FDR_limit = 0.05

    f = open("contrast_compare.res")
    contrast_compare_text = f.readlines()
    f.close()
    html_table = parse_contrasts(contrast_compare_text, FDR_limit, idtype, organism)
    return html_table
