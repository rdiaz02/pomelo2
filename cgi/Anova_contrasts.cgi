#!/usr/bin/python2.4
import cgi
import os
#import cgitb;cgitb.enable()
import random
import sys
import parse_contrs_comp

################################ Functions ############################################################

def update_radio_link(line):
#	line     = line.replace("Class","")
	elements = line.split("\t")
	elements = elements[1:]
	radio_elem1 = ["Choose contrast 1: <input name='venn1' value='None' type='radio' checked='TRUE'>  None "]
	radio_elem2 = ["Choose contrast 2: <input name='venn2' value='None' type='radio' checked='TRUE'>  None "]
	radio_elem3 = ["Choose contrast 3: <input name='venn3' value='None' type='radio' checked='TRUE'>  None "]
	links_elem  = []
	for i in elements:
		link_i = "<a href='" + i + ".html' " + "target='help_window_" + i + "'>" + i.replace("Class","") + "</a><br>"
		links_elem.append(link_i)
		radio1 = "<input name='venn1' value='" + i + "' type='radio'>" + i.replace("Class","")
		radio2 = "<input name='venn2' value='" + i + "' type='radio'>" + i.replace("Class","")
		radio3 = "<input name='venn3' value='" + i + "' type='radio'>" + i.replace("Class","")
		radio_elem1.append(radio1)
		radio_elem2.append(radio2)
		radio_elem3.append(radio3)
	radio      = ''.join(radio_elem1+["<br>"]+ radio_elem2+["<br>"]+ radio_elem3 + ["<br>"])
	links_elem = ''.join(links_elem)
	ret_text   = "&&radio_opt&&" + radio + "&&indv_table&&" + links_elem
	
	return ret_text


# Check for class comparisons and return the links and options
def refresh(redraw, radio_link, do_table, do_FDR):
	stat = "OK"
	try:
		f    = open("contrast_compare.res")
		line = f.readline()
		f.close()
		line = line.replace("\n","")
	except:
		stat = "exit"
		
	if stat == "exit":
		print "Content-type: text/html;charset=utf-8\n\n"
		FDR_value = read_FDR()
		print "&&FDR&&" + FDR_value
		sys.exit()

	return_text = ""
	if radio_link == "updateRadLink":
		return_text = return_text + update_radio_link(line)

	if do_table   == "updateTable":
		table_calc  = parse_contrs_comp.make_html_table()
		return_text = return_text + "&&contrast_table&&" + table_calc
		
	if redraw == "redraw":
		draw_new_venn()

	if redraw == "redraw" or redraw=="refresh_venn":
		venn_hmlt   = venn_drawing_html()		
		return_text = return_text + "&&venn_diagr&&" + venn_hmlt
		
	if do_FDR == "updateFDR":
		FDR_value   = read_FDR()
		return_text = return_text + "&&FDR&&" + FDR_value
		
	return_text = return_text + "&&"
	
	return return_text

def venn_drawing_html():
	try:
		f = open("vennNames")
		file_names = f.readline()
		f.close()		
		file_names = file_names.split("\t")
		style_text="<td><img border=1 style='width:19.8em; height:16.5em'"
		return_text = "<table><tr>"
		return_text = return_text + style_text + "src='" + file_names[1] + "'></td>"
		return_text = return_text + style_text + "src='" + file_names[2] + "'></td>"	
		return_text = return_text + style_text + "src='" + file_names[0] + "'></td></tr>"
		return_text = return_text + "<tr><td>Up-regulated</td><td>Down-regulated</td><td>Both</td></tr></table>"
		
	except:
		return_text = "No diagram has been drawn yet."

	return return_text

def read_FDR():
	try:
		f = open("max_FDR"); file_FDR = f.read();f.close()
	except:
		file_FDR = "0.05"

	html_FDR = "Genes are considered differentially expressed, for the diagram and table below, when: <B style = 'position:relative; left:2%; color:ff6600' > FDR < " + file_FDR + "</B>"
	
	return html_FDR


def class_compare(class1, class2):
	f = open("contrast_classes","w")
	clas_comp="Class" + class1 + "-Class" +  class2
	f.write(clas_comp)
	f.close()
	Rcommand = "cd " + tmp_dir + "; " + "/usr/bin/R CMD BATCH --no-restore --no-readline --no-save -q calculate_contrasts.R  2> error.msg "
	Rrun         = os.system(Rcommand)
	pyparsetable = "cd "+ tmp_dir + "; "+"/usr/bin/python2.4 /http/pomelo2/cgi/contrast_generate_table.py " + tmp_dir
	dummy_run    = os.system(pyparsetable)

	
def drawDiagram(contr1,contr2,contr3):
	file_names = "vennboth" +str(random.randint(1, 999999)) + ".png\t" + "vennup" + str(random.randint(1, 999999)) + ".png\t" + "venndown" + str(random.randint(1, 999999)) + ".png\n"
	try:
		f    = open("contrast_compare.res")
		line = f.readline()
		f.close()
		line = line.replace("\n","")
		#line = line.replace("Class","")
		elements = line.split("\t")
		elements = elements[1:]	
	except:
		print "Content-type: text/html;charset=utf-8\n\n"
		print "NULL, nada, agua, water"
		sys.exit()
	positions = []
	try:
		pos1 = elements.index(contr1)+1
		positions.append(str(pos1))
	except:
		pass
	try:
		pos2 = elements.index(contr2)+1
		positions.append(str(pos2))
	except:
		pass
	try:
		pos3 = elements.index(contr3)+1
		positions.append(str(pos3))
	except:
		pass
	
	file_names = file_names + '\t'.join(positions)
	f = open("vennNames","w")
	f.write(file_names)
	f.close()
	draw_new_venn()
	
def draw_new_venn():
	if os.path.exists("vennNames"):
		os.system("rm venn*.png")
		drawvenn = "cd " + tmp_dir + "; " + "/usr/bin/R CMD BATCH --no-restore --no-readline --no-save -q draw_venn.R 2> error.msg "
		dummy_run    = os.system(drawvenn)

def change_FDR(new_FDR):
	f = open("max_FDR","w"); f.write(new_FDR);f.close()	
	try:
		f = open("vennNames")
		lines = f.readlines()
		f.close()
		new_file_names = "vennboth" +str(random.randint(1, 999999)) + ".png\t" + "vennup" + str(random.randint(1, 999999)) + ".png\t" + "venndown" + str(random.randint(1, 999999)) + ".png\n"
		lines[0] = new_file_names		
		f = open("vennNames","w")
		f.writelines(lines)
		f.close()
	except:
		pass

def check_class_comp (class1, class2):
	comparison_status = "OK"
	if class1 == class2:
		comparison_status = "invalid comparison"
	clas_comp1="Class" + class1 + "-Class" +  class2
	clas_comp2="Class" + class2 + "-Class" +  class1
	try:
		f    = open("contrast_compare.res")
		line = f.readline()
		f.close()
		ind1 = line.find(clas_comp1)
		ind2 = line.find(clas_comp2)
		if (ind1!=-1) or (ind2!=-1):
			comparison_status = "invalid comparison"
      	except:
		pass

	if comparison_status == "invalid comparison":
		#ajax_text = refresh("noRedraw")
		print "Content-type: text/html;charset=utf-8\n\n"
		print "Invalid comparison"
		sys.exit()

def check_draw_venn (contr1,contr2,contr3):
	list_contr = [contr1,contr2,contr3]
	num1 = list_contr.count(contr1)
	num2 = list_contr.count(contr2)
	num3 = list_contr.count(contr3)
	if num1>1 or num2>1 or num3>1:
		print "Content-type: text/html;charset=utf-8\n\n"
		print "Invalid venn"
		sys.exit()
	
def check_FDR (FDR_input):
	status_flag = "OK"
	try:
		num_FDR = float(FDR_input)
		if num_FDR<0:
			status_flag = "exit"
	except:
		status_flag = "exit"
		
	if status_flag=="exit":
		print "Content-type: text/html;charset=utf-8\n\n"
		print "Invalid FDR"
		sys.exit()
	

def clear_all():
	dummy = os.system("rm contrast_compare.res")
	dummy = os.system("rm Class*")
	dummy = os.system("rm venn*png")
	dummy = os.system("rm vennNames")
	dummy = os.system("rm max_FDR")
	dummy = os.system("rm contrast_classes")
	print "Content-type: text/html;charset=utf-8\n\n"
	radio_elem1 = "Choose contrast 1: <input name='venn1' value='None' type='radio' checked='TRUE'>  None <br>"
	radio_elem2 = "Choose contrast 2: <input name='venn2' value='None' type='radio' checked='TRUE'>  None <br>"
	radio_elem3 = "Choose contrast 3: <input name='venn3' value='None' type='radio' checked='TRUE'>  None <br>"
	radio       = radio_elem1 + radio_elem2 +  radio_elem3
	links_elem  = "No class contrasts have been calculated yet."
	venn_hmlt   = "No diagram has been drawn yet."
	table_calc  = "No class contrasts have been calculated yet."
	return_text = "&&indv_table&&" + links_elem  + "&&radio_opt&&" + radio + "&&contrast_table&&" + table_calc
	html_FDR    = read_FDR()
	return_text = return_text + "&&venn_diagr&&" + venn_hmlt + "&&FDR&&" + html_FDR + "&&"
	print return_text
		
##################################################################################

form    = cgi.FieldStorage()
tmp_dir = form['tmp_dir'].value
os.chdir(tmp_dir)
cgi_option = form['cgi_option'].value

if cgi_option=="refresh":
	ajax_text = refresh("refresh_venn", "updateRadLink", "updateTable", "updateFDR")

if cgi_option=="class_comp":
	class1      = form['class1'].value
	class2      = form['class2'].value
	check_class_comp (class1, class2)
	class_compare(class1, class2)
	ajax_text   = refresh("NO_refresh_venn", "updateRadLink", "updateTable", "NO_updateFDR")

if cgi_option=="changeFDR":
	new_FDR   = form['newFDR'].value
	check_FDR (new_FDR)
	change_FDR(new_FDR)
	ajax_text = refresh("redraw", "NO_updateRadLink", "updateTable", "updateFDR") 

if cgi_option=="draw_venn":
	contr1 = form['contr1'].value
	contr2 = form['contr2'].value
	contr3 = form['contr3'].value
	check_draw_venn (contr1,contr2,contr3)
	drawDiagram(contr1,contr2,contr3)
	ajax_text = refresh("refresh_venn", "NO_updateRadLink", "NO_updateTable", "NO_updateFDR") 

if  cgi_option=="clear_all":
	clear_all()
	
	
print "Content-type: text/html;charset=utf-8\n\n"
print ajax_text
