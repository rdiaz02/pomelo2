#!/usr/bin/python2.4
import cgi
import os
import random
import sys
import parse_contrs_comp
import shutil
import fcntl
import socket
import time
import cgitb; cgitb.enable() ## zz: eliminar for real work?
sys.stderr = sys.stdout


################################ Functions ############################################################

## For redirections, from Python Cookbook
def getQualifiedURL(uri = None):
    """ Return a full URL starting with schema, servername and port.
        *uri* -- append this server-rooted uri (must start with a slash)
    """
    schema, stdport = ('http', '80')
    host = os.environ.get('HTTP_HOST')
    if not host:
        host = os.environ.get('SERVER_NAME')
        port = os.environ.get('SERVER_PORT', '80')
        if port != stdport: host = host + ":" + port
    result = "%s://%s" % (schema, host)
    if uri: result = result + uri
    return result


def add_to_log(application, tmpDir, error_type,error_text):
    date_time = time.strftime('%Y\t%m\t%d\t%X')
    # Truncate error text
    error_text = error_text[:300]
    outstr = '%s\t%s\t%s\t%s\n%s\n' % (application, date_time, error_type, tmpDir, error_text)
    cf = open('/http/mpi.log/app_caught_error', mode = 'a')
    fcntl.flock(cf.fileno(), fcntl.LOCK_SH)
    cf.write(outstr)
    fcntl.flock(cf.fileno(), fcntl.LOCK_UN)
    cf.close()

def cgi_error_page(error_type, error_text):
    error_template = open("/http/pomelo2/www/Pomelo2_html_templates/templ-error.html","r")
    err_templ_hmtl = error_template.read()
    error_template.close()
    err_templ_hmtl = err_templ_hmtl.replace("_ERROR_TITLE_", error_type)
    err_templ_hmtl = err_templ_hmtl.replace("_ERROR_TEXT_" , error_text)
    add_to_log("Pomelo II", tmpDir, error_type, error_text)
    err_templ_hmtl = "Content-type: text/html\n\n" + err_templ_hmtl 
    print err_templ_hmtl


# Upload file and deal with weird files
def fileUpload(fieldName,fs,tmpDir):
    """Upload and get the files and do some checking. We assume there is an existing call
    to fs = cgi.FieldStorage()"""
    ## we don't deal with OS specific "\n"
    ## because R does not have a problem (at least with Windows files)
    ## no problem in R either with empty carriage returns at end of file

    if fs.has_key(fieldName):
        fileClient = fs[fieldName].file
        if not fileClient:
            shutil.rmtree(tmpDir)
            err_msg = "<p> The " + fieldName + "file you entered is not a file </p>"
            err_msg = err_msg + "<p> Please fill up the required fields and try again.</p>"
            cgi_error_page("INPUT ERROR", err_msg)
            sys.exit()
    else:
        shutil.rmtree(tmpDir)
        err_msg = "<p> A " +  fieldName + "file is required </p>"
        err_msg = err_msg + "<p> Please fill up the required fields and try again.</p>"
        cgi_error_page("INPUT ERROR", err_msg)
        sys.exit()
    # transferring files to final destination;
    fileInServer = tmpDir + "/COVARIABLES/" + fieldName
    srvfile = open(fileInServer, mode = 'w')
    fileString = fs[fieldName].value
    srvfile.write(fileString)
    srvfile.close()
    os.chmod(fileInServer, 0666)
    if os.path.getsize(fileInServer) == 0:
	err_msg = "<p> The "+ fieldName + " file you entered is empty </p>"
	err_msg = err_msg + "<p> Please enter a file with something in it.</p>"
	cgi_error_page("INPUT ERROR", err_msg)
	sys.exit

def numeric_table(table):
    covar_name = table[0].strip()
    summary_values = table[3].split()
    
    # CSS defs
    CSS_chkbox     = "<span style=\"position:relative;left:5%\">"
    CSS_covar_name = "<span style=\"position:relative;left:8%;font-weight:bold;font-size:large\">"
    CSS_type       = "<span style=\"position:relative;left:10%;color:ff6600;font-weight:bold;\">"

    # Table header
    html_chkbox     = CSS_chkbox + "<INPUT TYPE=\"checkbox\" NAME=\""+covar_name+"\" VALUE=\""+covar_name+"\" onClick=\" box_changed('" + covar_name + "',1)\"></span>"
    html_covar_name = CSS_covar_name + covar_name + "</span>"
    html_type       = CSS_type + " (NUMERIC COVARIABLE)</span>"
    html_header     = html_chkbox + html_covar_name + html_type
    
    # Table
    table_start  = "<table>" #style=\"position:relative;left:7%\">"
    table_mean   = "<tr><td>Mean Value:</td><td>&nbsp;</td><td align=\"right\">"    + summary_values[3] + "</td></tr>"
    table_min    = "<tr><td>Minimum Value:</td><td>&nbsp;</td><td>" + summary_values[0] + "</td></tr>"
    table_max    = "<tr><td>Maximum Value:</td><td>&nbsp;</td><td>" + summary_values[5] + "</td></tr>"
    table_1qurt  = "<tr><td>25% below(1st Quartile):</td><td>&nbsp;</td><td>"    + summary_values[1] + "</td></tr>"
    table_median = "<tr><td>50% below(median):</td><td>&nbsp;</td><td>"    + summary_values[2] + "</td></tr>"
    table_3qurt  = "<tr><td>75% below(3rd Quartile):</td><td>&nbsp;</td><td>"    + summary_values[4] + "</td></tr></table>\n"
    html_table   =  table_start +  table_min + table_max +  table_mean + table_1qurt + table_median + table_3qurt

    # In the end
    #html_numeric_summary = html_header + html_table 
    html_table_foto_and_summary  = "<table style=\"position:relative;left:7%\"><tr><td style=\"width:15%\" valign=\"top\">" + html_table  + "</td></tr><tr><td style=\"width:30%\"><img border=1 src='http://pomelo2.bioinfo.cnio.es/tmp/" + newDir + "/COVARIABLES/" + covar_name.strip() +".png'></td></tr></table>\n<br><br><br>"
    html_numeric_summary = html_header + html_table_foto_and_summary
    
    return html_numeric_summary
    
    
def non_numeric_table(table):
    covar_name = table[0].strip()
    summary_values = table[2:]
    
    # CSS defs
    CSS_chkbox     = "<span style=\"position:relative;left:5%\">"
    CSS_covar_name = "<span style=\"position:relative;left:8%;font-weight:bold;font-size:large\">"
    CSS_type       = "<span style=\"position:relative;left:10%;color:ff6600;font-weight:bold;\">"

    # Table header contains _number_ which is replaced at the end of the function
    html_chkbox     = CSS_chkbox + "<INPUT TYPE=\"checkbox\" NAME=\"" + covar_name + "\" VALUE=\""+covar_name+"\" onClick=\" box_changed('" + covar_name + "',_number_)\" ></span>"
    html_covar_name = CSS_covar_name + covar_name + "</span>"
    html_type       = CSS_type + " (NON-NUMERIC COVARIABLE)</span>"
    html_header     = html_chkbox + html_covar_name + html_type
    
    # Table
    table_start  = "<table>"# style=\"position:relative;left:15%\">"
    table_html = []
    # Degrees of freedom
    df = 0
    for i in range(len(summary_values)/2):
        j = 2*i
        factor_names     = summary_values[j].split()
        factor_frequency = summary_values[j+1].split()
        for i_name, i_freq in zip(factor_names, factor_frequency):
            df = df + 1
            table_row   = "<tr><td>" + i_name + "</td><td>" + i_freq + "</td></tr>\n"
            table_html.append(table_row)
    
    html_table   =  table_start + '\n'.join(table_html)  + "</table>\n"
    
    
    # In the end
    #html_non_numeric_summary = html_header + html_table
    html_table_foto_and_summary  = "<table style=\"position:relative;left:7%\"><tr><td style=\"width:15%\" valign=\"top\">" + html_table  + "</td></tr><tr><td style=\"width:30%\"><img border=1 src='http://pomelo2.bioinfo.cnio.es/tmp/" + newDir + "/COVARIABLES/" + covar_name.strip() +".png'></td></tr></table>\n<br><br><br>"
    html_header = html_header.replace("_number_",str(df))
    html_non_numeric_summary = html_header + html_table_foto_and_summary
    return html_non_numeric_summary
    

def parse_summary(summary, names_covar):
    html_list = []
    line_start = 0
    # Add dummy to list to get a with find -1
    names_covar.append("dummy")
    for i in range(len(names_covar)-1):
        line_finish = summary.find(names_covar[i + 1])
        text = summary[line_start:line_finish]
        if text.find("TRUE")!= -1:
            text_line = text.split("\n")
            html_list.append(non_numeric_table(text_line))
        elif text.find("FALSE")!= -1:
            text_line = text.split("\n")
            html_list.append(numeric_table(text_line))
        line_start  = line_finish
    html_sum = ''.join(html_list)
    return html_sum

# Make html summary or error page
def r2html(tmp_dir, newDir):
    try:
        f = open("COVARIABLES/errCovariables")
        error_msg = f.read()
        f.close()
        f = open("/http/pomelo2/www/Pomelo2_html_templates/templ-error.html")
        err_template = f.read()
        f.close()
        error_msg = error_msg + "<br><br><input type='button' value=' Back to add covariables ' OnClick='document.location=\"add_covariables.cgi?newDir=" + newDir + " \"'>"
        err_template = err_template.replace("_ERROR_TEXT_", error_msg)
        html_output  = err_template.replace("_ERROR_TITLE_", "Covariables Error")
        
    except:
        # Note for me: watch new lines \n
        f = open("COVARIABLES/covariable_summary")
        summary_lines = f.read()
        f.close()
#         f = open("class_labels");subj = f.read().split();f.close()
        f = open("COVARIABLES/names_covariables")
        names_covar   = f.read().split()
        f.close()
        ## max_df     = str(len(subj)-2)
        f = open("max.df")
        max_df = int(f.read().split()[0])
        f.close()
        name_list  = '\",\"'.join(names_covar)
        name_list  = '\"' + name_list + '\"'
        # Create list of zeros
        zeros_list = []
        for i in names_covar:
            zeros_list.append("0")
        value_list = ','.join(zeros_list)
        html_summary  = parse_summary(summary_lines, names_covar)
        f = open("/http/pomelo2/www/Pomelo2_html_templates/templ_check_covariables.html")
        html_templ    = f.read();f.close()
        f.close()
        html_templ  = html_templ.replace("_SUBS_DIR_"      , tmp_dir)
        html_templ  = html_templ.replace("_NUMBERS_"       , newDir)
        html_templ  = html_templ.replace("_VARIABLE_LIST_" , name_list)
        html_templ  = html_templ.replace("_VALUES_LIST_"   , value_list)
        html_templ  = html_templ.replace("_MAX_DF_"        , str(max_df))

        html_output = html_templ.replace("_SUMMARY_TABLE_" , html_summary)
        
    return html_output

		
##################################################################################
#************  SELENIUM STUFF **************
covariable_sel_file ="/http/pomelo2/www/selenium-core-0.7.1/TEST_DATA/covariables.anova"
#*******************************************
form    = cgi.FieldStorage()
try:
    tmp_dir = form['tmp_dir'].value
except:
    tmpDir = 'NULL'
    cgi_error_page('tmp_dir error',
                   'You should NOT call this cgi directly. It is to be called by the application')
    sys.exit()
os.chdir(tmp_dir)
cgi_option = form['cgi_option'].value
f = open("testtype");test_type = f.read().strip();f.close()  
num_permut = 10000  ## this should be irrelevant here; these are limma tests so no permut.
newDir = tmp_dir.split("/")[-1]
tmpDir = tmp_dir
##tmpDir = '/http/pomelo2/www/tmp/' + newDir

# If they have chosen to continue without covariables
if cgi_option == "continue":
    try:
       dummyi, dummyo, dummye = os.popen3("rm COVARIABLES/*")
    except:
       pass
    run_and_check = os.spawnv(os.P_NOWAIT, '/http/pomelo2/cgi/runAndCheck.py',
                              ['', tmpDir])
    os.system('echo "' + str(run_and_check) + ' ' + socket.gethostname() +\
                  '"> ' + tmpDir + '/run_and_checkPID')
    ##############    Redirect to results.html    ##################
    print "Location: "+ getQualifiedURL("/tmp/" + newDir + "/results.html"), "\n\n"

#     tryrrun = os.system('/http/mpi.log/pomelo_run.py ' + tmp_dir + ' ' + test_type + ' ' + str(num_permut) +'&')
#     ##############    Redirect to checkdone.cgi    ##################
#     print "Location: "+ getQualifiedURL("/cgi-bin/pomelo_checkdone.cgi") + "?newDir=" + newDir, "\n\n"



# If they have sent covariables
if cgi_option=="check_covariables":
    # Selenium if *********
    if os.path.exists('SELENIUM_TEST'):
        shutil.copy(covariable_sel_file,"COVARIABLES/covariables")
    elif os.path.exists('COVARIABLES/added-example-covariables'):
        pass
    else:
        fileUpload("covariables",form,tmp_dir)
    dummy = os.system('cp /http/pomelo2/cgi/test_and_summary.R COVARIABLES/' + '/. ; chmod 777 COVARIABLES/test_and_summary.R')
    Rcommand = "cd " + tmp_dir + "/COVARIABLES; /var/www/bin/R-local-7-LAM-MPI/bin/R CMD BATCH --no-restore --no-readline --no-save -q test_and_summary.R "
    dummy = os.system(Rcommand)
    html_page = r2html(tmp_dir, newDir)        
    print "Content-type: text/html\n\n"
    print html_page

# Once they have chosen tje coveriables they have already sent
if cgi_option=="covar_launch":
    #print "Content-type: text/html\n\n"
    keys_form =  form.keys()
    keys_form.remove('tmp_dir')
    keys_form.remove('cgi_option')
    keys_form.remove('submit_button')
    covars_list = []
    for i in range(len(keys_form)):
        i_key = keys_form[i]
        covars_list.append(i_key)
    covars_string = "\t".join(covars_list)
    if len(covars_string) != 0:
        f=open("COVARIABLES/chosen_covariables","w")
        f.write(covars_string)
        f.close()
        # Aqui habria que rellenar los templates


    run_and_check = os.spawnv(os.P_NOWAIT, '/http/pomelo2/cgi/runAndCheck.py',
                              ['', tmpDir])
    os.system('echo "' + str(run_and_check) + ' ' + socket.gethostname() +\
                  '"> ' + tmpDir + '/run_and_checkPID')
    ##############    Redirect to results.html    ##################
    print "Location: "+ getQualifiedURL("/tmp/" + newDir + "/results.html"), "\n\n"
    
#     tryrrun = os.system('/http/mpi.log/pomelo_run.py ' + tmp_dir + ' ' + test_type + ' ' + str(num_permut) +'&')
#     ##############    Redirect to checkdone.cgi    ##################
#     print "Location: "+ getQualifiedURL("/cgi-bin/pomelo_checkdone.cgi") + "?newDir=" + newDir, "\n\n"
