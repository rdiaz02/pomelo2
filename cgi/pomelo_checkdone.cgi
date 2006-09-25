#!/usr/bin/python2.4
## All this code is copyright Ramon Diaz-Uriarte. For security reasons, this is for
## now confidential. No license is granted to copy, distribute, or modify it.
## Once everything is OK, it will be distributed under the GPL.
import sys
import os
import cgi 
import types
import time
import shutil
import signal
import re
import tarfile
import string
import cgitb;cgitb.enable() ## zz: eliminar for real work?
import fcntl
sys.stderr = sys.stdout ## eliminar?

Pomelo_MAX_time = 8 * 3600 ## 8 hours is max duration allowd for any process

# *************************************************************************************
# *********************         Functions        **************************************

def add_to_log(application, tmpDir, error_type,error_text):
    date_time = time.strftime('%Y\t%m\t%d\t%X')
    outstr = '%s\t%s\t%s\t%s\n%s\n' % (application, date_time, error_type, tmpDir, error_text)
    cf = open('/http/mpi.log/app_caught_error', mode = 'a')
    fcntl.flock(cf.fileno(), fcntl.LOCK_SH)
    cf.write(outstr)
    fcntl.flock(cf.fileno(), fcntl.LOCK_UN)
    cf.close()

def cgi_error_page(error_type, error_text, tmpDir):
    error_template = open("/http/pomelo2/www/Pomelo2_html_templates/templ-error.html","r")
    err_templ_hmtl = error_template.read()
    error_template.close()
    err_templ_hmtl = err_templ_hmtl.replace("_ERROR_TITLE_", error_type)
    err_templ_hmtl = err_templ_hmtl.replace("_ERROR_TEXT_" , error_text)
    add_to_log("Pomelo II", tmpDir, error_type, error_text)
    err_templ_hmtl = "Content-type: text/html\n\n" + err_templ_hmtl 
    print err_templ_hmtl

def html_error_page(error_type, error_text, tmpDir):
    error_template = open("/http/pomelo2/www/Pomelo2_html_templates/templ-error.html","r")
    err_templ_hmtl = error_template.read()
    error_template.close()
    err_templ_hmtl = err_templ_hmtl.replace("_ERROR_TITLE_", error_type)
    err_templ_hmtl = err_templ_hmtl.replace("_ERROR_TEXT_" , error_text)
    add_to_log("Pomelo II", tmpDir, error_type, error_text)
    f_results = open(tmpDir + "/results.html", mode = "w")
    f_results.write(err_templ_hmtl)
    f_results.close()


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

def getScriptname():
    """ Return te scriptname part of the URL."""
    return os.environ.get('SCRIPT_NAME', '')

def getBaseURL():
    """ Return a fully qualified URL to this script. """
    return getQualifiedURL(getScriptname())
def commonOutput():
    print "Content-type: text/html\n\n"
    print """
    <html>
    <head>
    <title>Pomelo II results</title>
    </head>
    <body>
    """    
## to keep executing myself:
def relaunchCGI():
    print "Content-type: text/html\n\n"
    old_html = open(tmpDir + "/results.html")
    html_data = old_html.read()
    old_html.close()
    print html_data

    
def mpi_error():
    error_text = "<p> A technical problem has ocurred during execution. </p>"
    error_text = error_text + "<p> The webmaster will be warned and hopefully the problem will be solved soon. </p>"
    html_error_page("MPI ERROR", error_text, tmpDir)


def multest_error():
    error_text = "<p> PomeloII crashed. </p>"
    error_text = error_text + "<p> Below is the output from the execution: </p>"
    pom_out = open(tmpDir + "/pomelo.msg")
    lines = pom_out.readlines()
    pom_out.close()
    lines = lines[:10]
    text  = ''.join(lines)
    error_text = error_text + text
    html_error_page("MULTEST ERROR", error_text, tmpDir)


def printPomKilled():
    error_text = "<p> Execution has exceeded maximum time (" + str(Pomelo_MAX_time/3600) + "hours).</p>"
    error_text = error_text + "<p> Either the data and options you entered produced an excessively long execution or </p>"
    error_text = error_text + "<p> a technical problem ocurred.</p>"
    html_error_page("POMELO KILLED", error_text, tmpDir)

def printOKRun():
    f=open(tmpDir + "/testtype")
    test_type = f.read().strip()
    f.close()
    draw_heatmaptable = "cd " + tmpDir + "; python /http/pomelo2/cgi/heatmap_draw_script.py;" 
    # Cox script draws its own tables
    if test_type != "Cox":
	    draw_heatmaptable = draw_heatmaptable + "python2.4 /http/pomelo2/cgi/generate_table.py"
    dummy = os.system(draw_heatmaptable)
    Heatresults = open(tmpDir + "/heat_new.html")
    table_file  = open(tmpDir + "/p.v.sort.FDR.a.html")
    # If limma anova we use template that has the links that take you to class comparison
    if test_type == "Anova_limma":
        template    = open("/http/pomelo2/www/Pomelo2_html_templates/results_template_limmma_anova.html","r")
    else:
        template    = open("/http/pomelo2/www/Pomelo2_html_templates/results_template.html","r")
        
    heat_temp_f = open("/http/pomelo2/www/Pomelo2_html_templates/templ_heatmap.html","r")
    templ_heat  = heat_temp_f.read()
    templ_heat  = templ_heat.split("_SPLIT_ME_")
    number_arr  = tmpDir.split("/")
    var_number  = number_arr[-1]
    templ_heat[0] = templ_heat[0].replace("_TEMP_DIR_",tmpDir)
    templ_hmtl  = template.read()
    temp_array  = templ_hmtl.split("_SPLIT_ME_")
    table_res   = table_file.read()
    resultsFile = Heatresults.read()
    temp_array[0] = temp_array[0].replace("_NUMBERS_",var_number)
    temp_array[0] = temp_array[0].replace("_TEMP_DIR_",tmpDir)
    temp_array[1] = temp_array[1].replace("_TEMP_DIR_",tmpDir)
    final_html  = temp_array[0] + table_res + temp_array[1] + resultsFile + temp_array[2]
    final_heat_map = templ_heat[0] + resultsFile + templ_heat[1]
    outf = open(tmpDir + "/pre-results.html", mode = "w")
    outf.write(final_html)
    outf.close()
    outf = open(tmpDir + "/heatmap_alter.html", mode = "w")
    outf.write(final_heat_map)
    outf.close()
    template.close()
    table_file.close()
    Heatresults.close()
    os.chdir(tmpDir)
    shutil.copyfile("pre-results.html","results.html")
    if os.path.exists('p.v.sort.FDR.d.html'):
    	os.system('html2text -width 200 -nobs  -o results.pomelo.txt p.v.sort.FDR.d.html')

    
def close_lam_env():
    try:
        lamenv = open(tmpDir + "/lamSuffix", mode = "r").readline()
    except:
        None
    try:
        lamkill = os.system('export LAM_MPI_SESSION_SUFFIX=' + lamenv + '; lamhalt -H; lamwipe -H')
    except:
        None
    try:
        os.system("rm /http/pomelo2/www/Pom.running.procs/Pom." + newDir + "*")
    except:
        None
        
# End of functions ****************************************************************************************
#**********************************************************************************************************

# *********************************************************************************************************
# *********************************     Beginning of CGI        *******************************************

# Get tmp dir from form and check it is valid ***************
form = cgi.FieldStorage()
if form.has_key('newDir'):
   value=form['newDir']
   if type(value) is types.ListType:
       err_msg = "<p> newDir should not be a list. </p>"
       err_msg = err_msg + "<p> Anyone trying to mess with it?</p>"
       cgi_error_page("URL ERROR", err_msg, '-')
       sys.exit()
   else:
       newDir = value.value
else:
    err_msg = "<p> newDir is empty. </p>"
    cgi_error_page("URL ERROR", err_msg, '-')
    sys.exit()

if re.search(r'[^0-9]', str(newDir)):
    ## newDir can ONLY contain digits
    err_msg = "<p> newDir does not have a valid format. </p>"
    err_msg = err_msg + "<p> Anyone trying to mess with it?</p>"
    cgi_error_page("URL ERROR", err_msg, '-')
    sys.exit()

redirectLoc = "/tmp/" + newDir
tmpDir = "/http/pomelo2/www/tmp/" + newDir

if not os.path.isdir(tmpDir):
    err_msg = "<p> newDir is not a valid directory. </p>"
    err_msg = err_msg + "<p> Anyone trying to mess with it?</p>"
    cgi_error_page("URL ERROR", err_msg, '-')
    sys.exit()
# ***********************************************************



# If file pomelo_run.finished exists, multest has finished 
run_finished = os.path.exists(tmpDir + "/pomelo_run.finished")

# If multest has finished
if run_finished:
    
    mpi_worked    = os.path.exists(tmpDir + "/mpiOK")
    results_exist = os.path.exists(tmpDir + "/multest_parallel.res")
    
    if not mpi_worked:
        close_lam_env()
        mpi_error()
        print 'Location: http://pomelo2.bioinfo.cnio.es/tmp/' + newDir + '/results.html \n\n'
        sys.exit()

    if not results_exist:
        close_lam_env()
        multest_error()
        print 'Location: http://pomelo2.bioinfo.cnio.es/tmp/' + newDir + '/results.html \n\n'
        sys.exit()
    
    else:
        close_lam_env()
        printOKRun()
        print 'Location: http://pomelo2.bioinfo.cnio.es/tmp/' + newDir + '/results.html \n\n'
        sys.exit()
        
# If multest hasn't finished, check if it needs killing
elif (time.time() - os.path.getmtime(tmpDir + "/covariate")) > Pomelo_MAX_time:
    close_lam_env()
    printPomKilled()
    print 'Location: http://pomelo2.bioinfo.cnio.es/tmp/'+ newDir + '/results.html \n\n'
    sys.exit()

relaunchCGI()
