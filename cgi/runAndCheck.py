#!/usr/bin/python2.4
## All this code is copyright Ramon Diaz-Uriarte, and distributed under the
## Affero GPL license

import glob
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
import fcntl
import socket 
import random
import cgitb; cgitb.enable() 
sys.stderr = sys.stdout 

tmpDir     = sys.argv[1]

Pomelo_MAX_time = 8 * 3600 ## 8 hours is max duration allowd for any process
MAX_NUM_RELAUNCHES = 5 
TIME_BETWEEN_CHECKS = 10
ROOT_TMP_DIR = "/http/pomelo2/www/tmp"
newDir = tmpDir.replace(ROOT_TMP_DIR, "")
newDir = newDir.replace("/", "") ## just the number



################################################################
################################################################
######################                  ########################
######################   Functions      ########################
######################                  ########################
################################################################
################################################################


def issue_echo2(fecho):
    """Silly function to output small tracking files. Debugging"""
    timeHuman = '##########   ' + \
                str(time.strftime('%d %b %Y %H:%M:%S')) 
    os.system('echo "' + timeHuman + \
              '" >> ' + tmpDir + '/checkdone2.echo')
    os.system('echo "' + fecho + \
              '" >> ' + tmpDir + '/checkdone2.echo')
    os.system('echo "    " >> ' + tmpDir + '/checkdone2.echo')




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
# ## to keep executing myself:
# def relaunchCGI():
#     print "Content-type: text/html\n\n"
#     old_html = open(tmpDir + "/results.html")
#     html_data = old_html.read()
#     old_html.close()
#     print html_data

    
def mpi_error():
    error_text = "<p> A technical problem has ocurred during execution. </p>"
    error_text = error_text + "<p> The webmaster will be warned and hopefully the problem will be solved soon. </p>"
    html_error_page("MPI ERROR", error_text, tmpDir)


def multest_error():
    error_text = "<p> PomeloII crashed. </p>"
    error_text = error_text + "<p> Below is the output from the execution: </p>"
    if os.path.exists(tmpDir + "/pomelo.msg"):
        pom_out = open(tmpDir + "/pomelo.msg")
        lines = pom_out.readlines()
        pom_out.close()
        lines = lines[:10]
        text  = ''.join(lines)
        error_text = error_text + text
        
    error_text = error_text + '\n\n MACHINE: ' + str(socket.gethostname())
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
    heat_temp_f.close()
    os.chdir(tmpDir)
    shutil.copyfile("pre-results.html","results.html")
    if os.path.exists('p.v.sort.FDR.d.html'):
#        os.system('w3m -config = "/var/www/.w3m" -dump p.v.sort.FDR.d.html > results.pomelo.txt')
        fi,fo,fu = os.popen3('w3m -config = "/var/www/.w3m" -dump p.v.sort.FDR.d.html > results.pomelo.txt')
        fi.close()
        fo.close()
        fu.close()
        ### when launched from python, w3m complaints about Can't create config directory
        ### which I do not understand
##    	os.system('html2text -width 200 -nobs  -o results.pomelo.txt p.v.sort.FDR.d.html')
##      html2text leaves weird characters sometimes

    
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
        ## probably redundant, and fills error logs.
        numPomelo = len(glob.glob("/http/pomelo2/www/Pom.running.procs/Pom." + newDir + "*"))
        if numPomelo > 1:
            tmptmp = os.system("rm /http/pomelo2/www/Pom.running.procs/Pom." + newDir + "*")
    except:
        None

################################################################
################################################################
######################                  ########################
###################### End of functions ########################
######################                  ########################
################################################################
################################################################

issue_echo2("Start")

test_type = open(tmpDir + "/testtype", mode = "r").readline()
try:
    num_permut = open(tmpDir + "/num_permut", mode = "r").readline()
except:
    num_permut = 1 ## just in case, although it makes no difference, but with
    ## 0 it crashed on 32 bits, in IBM cluster


### Do very first run attempt.

issue_echo2("Before first tryrrun")
tryrrun = os.system('/http/pomelo2/cgi/pomelo_run2.py ' + tmpDir + 
                    ' ' + test_type + ' ' + str(num_permut) +'&')

time.sleep(TIME_BETWEEN_CHECKS + random.uniform(0.1, 3))
issue_echo2("After first tryrrun")


while True:  ## we repeat until done or unrecoverale crash
    issue_echo2("top of while")
    number_relaunches = int(open(tmpDir + "/number_relaunches", mode = "r").readline())

    if (time.time() - os.path.getmtime(tmpDir + "/covariate")) > Pomelo_MAX_time:
        ## FIXME: do we want to try and relaunch??
        issue_echo2("Out of time")
        close_lam_env()
        printPomKilled()
#         print 'Location: http://pomelo2.bioinfo.cnio.es/tmp/'+ \
#             newDir + '/results.html \n\n'
        break

    # If file pomelo_run.finished exists, it has finished 
    run_finished = os.path.exists(tmpDir + "/pomelo_run.finished")

    if run_finished:
        issue_echo2("run_finished")

        mpi_worked    = os.path.exists(tmpDir + "/mpiOK")
        results_exist = os.path.exists(tmpDir + "/multest_parallel.res")

        if (not mpi_worked) or (not results_exist):
            time.sleep(5) ## some of the ones below might not have been created
            ### FIXME: I think this is just impossible
            mpi_worked    = os.path.exists(tmpDir + "/mpiOK")
            results_exist = os.path.exists(tmpDir + "/multest_parallel.res")
            if (mpi_worked and results_exist):
                issue_echo2("the impossible if")

        if mpi_worked and results_exist:
            issue_echo2("OK run")
            close_lam_env()
            printOKRun()
            ## this AIN'T a CGI. None of this print stuff should be here!!
#            print 'Location: http://pomelo2.bioinfo.cnio.es/tmp/' + newDir + '/results.html \n\n'
            break
        
        # we only get here if something failed; so check if we can relaunch
        if (number_relaunches < MAX_NUM_RELAUNCHES):
            issue_echo2("try relaunch")
            ## so something did not work. Lets try launching again
            number_relaunches += 1
            nrelaunches = open(tmpDir + '/number_relaunches', mode = 'w')
            nrelaunches.write(str(number_relaunches) + '\n')
            nrelaunches.close()
            ## we need to get rid of the previous pomelo_run.finished
            ## or we will get here and do as many launches of pomelo_run2
            ## as successive loops
            close_lam_env()
            move_run_finished = os.rename(tmpDir + '/pomelo_run.finished', 
                                          tmpDir + '/pomelo_run.crash.finished-' +
                                          str(number_relaunches - 1))
            issue_echo2("renamed pomelo_run.finished")
            tryrrun = os.system('/http/pomelo2/cgi/pomelo_run2.py ' + tmpDir + 
                                ' ' + test_type + ' ' + str(num_permut) +'&')
            issue_echo2("tried relaunch")
        else: ## we cannot relaunch
            if not mpi_worked:
                issue_echo2("not mpi_worked")
                close_lam_env()
                mpi_error()
#                print 'Location: http://pomelo2.bioinfo.cnio.es/tmp/' + newDir + '/results.html \n\n'
                break

            elif not results_exist:
                issue_echo2("not results_exist")
                close_lam_env()
                multest_error()
#                print 'Location: http://pomelo2.bioinfo.cnio.es/tmp/' + newDir + '/results.html \n\n'
                break

    time.sleep(TIME_BETWEEN_CHECKS)



### clean ups
try:
    numPomelo = len(glob.glob("/http/pomelo2/www/Pom.running.procs/Pom." + newDir + "*"))
    if numPomelo > 1:
        tmptmp = os.system("rm /http/pomelo2/www/Pom.running.procs/Pom." + newDir + "*")
    issue_echo2('Deleting Pom.running.procs in ' +
                '/http/pomelo2/www/Pom.running.procs/Pom.' +
                newDir + '*')
except:
    None
             
burying = os.system("cd " + tmpDir + "; /http/mpi.log/buryPom.py")
issue_echo2("at the very end")


