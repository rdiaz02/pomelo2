#!/usr/bin/python
# -*- mode: python; -*-
# This code is used to load a window with the downloadable files and description. And to
# then zip and send the chosen files.
import cgi
import cgitb;cgitb.enable()
import dircache
import os
from pomelo_config import cgi_dir, pomelo_templates_dir, pomelo_url

##################################### Functions ##################################################
def make_files_dictionary(description_file):
    f = open(description_file)
    # Define bloc separation
    line_sep = "****************************************************************************************\n"
    # Read text and seprate into blocs 
    file_text_blocs = f.read().split(line_sep)
    # skip beginning (example etc)
    file_text_blocs = file_text_blocs[3:]
    file_dictionary = {}
    # iter over blocks
    for bloc in file_text_blocs:
        # Take block and separate into array of lines
        lines = bloc.split("\n")
        # If block is empty or missing either name, tag or description, do nothing
        if len(lines)<3:
            continue
        # Separate file name, file tag and file description
        name_key    = lines[0].strip()
        tag         = lines[1].strip()
        description = "\n".join(lines[2:])
        file_dictionary[name_key]=[tag,description]         
    return file_dictionary 

def html_checklist(file_dictionary, tmp_dir_fileList):
    #html_text = "<table style = \"position:relative; left:4%\">\n"
    html_all_rows = ""
    for file_in_dir in tmp_dir_fileList:
        if file_dictionary.has_key(file_in_dir):
            name_and_descrip = file_dictionary[file_in_dir]
            html_checkbox = "<input type=\"checkbox\" name=\"" + file_in_dir + "\" CHECKED >"
            html_rows     = "<tr><td>" + html_checkbox + "</td>\n"
            html_rows     = html_rows  + "<td><B>" + name_and_descrip[0] + "</B></td></tr>\n"
            description   = name_and_descrip[1].replace("\n","<br>")
            html_rows     = html_rows  + "<tr><td>&nbsp;</td><td>" + description + "<br></td></tr>\n"
            if html_rows.find("_checked_")!=-1:
                html_rows     = html_rows.replace("_checked_","")
                html_all_rows = html_rows + html_all_rows
            else:
                html_rows     = html_rows.replace("CHECKED","")
                html_all_rows = html_all_rows + html_rows                
        else:
            pass        
    html_text = "<table style = \"position:relative; left:4%\">\n" + html_all_rows + "</table>\n"
    return(html_text)
        
def create_readme(file_list, file_dictionary):
    text_header = "This is a help file which contains the name of the files\n"
    text_header = text_header + "you have downloaded and the description of"
    text_header = text_header + " what they contain.\n\n"
    text_header = text_header + "*************************************************\n"
    text_header = text_header + "*************************************************\n"
    description_list = [] 
    for file_name in file_list:
        dict_desc = file_dictionary[file_name]
        text_desc = file_name + "\n"
        text_desc = text_desc + dict_desc[0] + ":" +  dict_desc[1] + "\n"
        text_desc = text_desc + "-------------\n"
        description_list.append(text_desc)
    readme_text = text_header + "\n".join(description_list)
    readme_text = readme_text.replace("_checked_","")
    f = open("README.txt","w")
    f.write(readme_text)
    f.close()
    
def file_list(form, file_dictionary):
    full_form          = form.keys()
    possible_files     = file_dictionary.keys()
    list_downloadFiles = []
    for form_element in full_form:
        if possible_files.count(form_element) != 0:
            list_downloadFiles.append(form_element)
        else:
            pass
    return(list_downloadFiles)

################################## End of Functions ##############################################
form    = cgi.FieldStorage()
tmp_dir = form['tmp_dir'].value
os.chdir(tmp_dir)
cgi_action = form['cgi_action'].value
newDir     = tmp_dir.split("/")[-1]

# ******************** FOR DIFFERENT APPLICATIONS CHANGE THIS *************************
description_file  = cgi_dir + "/downloadable_files_description.txt"
download_template = pomelo_templates_dir + "/download_template.html"
zip_file          = "pomeloII_output.zip"
# *************************************************************************************
# Also make sure template has a hidden field cgi_action with value createZip
# and another hidden field tmp_dir with value _SUBS_DIR_ (python will replace this)

file_dictionary = make_files_dictionary(description_file)

if cgi_action=="showFiles":
    tmp_dir_fileList  = dircache.listdir(".")
    html_list         = html_checklist(file_dictionary, tmp_dir_fileList)
    f                 = open(download_template)
    html_downloadText = f.read()
    f.close()
    html_downloadText = html_downloadText.replace("_REPLACE_LIST_", html_list)
    html_downloadText = html_downloadText.replace("_SUBS_DIR_", tmp_dir)
    cgi_html          = "Content-type: text/html\n\n" + html_downloadText
    print cgi_html
    
elif cgi_action=="createZip":
    list_downloadFiles = file_list(form, file_dictionary)
    space_sep_file     = " ".join(list_downloadFiles)
    create_readme(list_downloadFiles, file_dictionary)
    zip_command = "zip " + zip_file + " " + space_sep_file + " README.txt"
    os.system(zip_command)
    print 'Location: ' pomelo_url + '/tmp/'+ newDir + '/' + zip_file + ' \n\n'
