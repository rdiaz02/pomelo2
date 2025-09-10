#!/usr/bin/python
## All this code is copyright 2006-2014 Ramon Diaz-Uriarte, and
## distributed under the Affero GPL license

## apparently, these aren't used
# import types
# import cgi 
# import signal
# import re
# import tarfile
# import string

import os
import time
import sys
import glob
import shutil
import fcntl
import socket
import random
import cgi
import cgitb; cgitb.enable() ## comment out once debugged?

## this is called from pomeloII.cgi and from check_covariables.cgi

## See pomelo_run2.py for why we need both
sys.path.append("/home2/ramon/web-apps/web-apps-common")
## sys.path.append("../../../../web-apps-common")

from web_apps_config import *  # noqa

sys.stderr = sys.stdout
tmpDir     = sys.argv[1]
## web_apps_dir = sys.argv[2]

newDir = tmpDir.replace(ROOT_POMELO_TMP_DIR, "")
newDir = newDir.replace("/", "")  # just the number

newDirPath = Pomelo_runningProcs + "/Pom." + newDir


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




def add_to_log(application, tmpDir, error_type, error_text):
    date_time = time.strftime('%Y\t%m\t%d\t%X')
    outstr = '%s\t%s\t%s\t%s\n%s\n' % (application, date_time, error_type, tmpDir, error_text)
    cf = open(web_apps_app_caught_error, mode = 'a')
    fcntl.flock(cf.fileno(), fcntl.LOCK_SH)
    cf.write(outstr)
    fcntl.flock(cf.fileno(), fcntl.LOCK_UN)
    cf.close()

# def cgi_error_page(error_type, error_text, tmpDir):
#     error_template = open(pomelo_templates_dir + "/templ-error.html","r")
#     err_templ_hmtl = error_template.read()
#     error_template.close()
#     err_templ_hmtl = err_templ_hmtl.replace("_ERROR_TITLE_", error_type)
#     err_templ_hmtl = err_templ_hmtl.replace("_ERROR_TEXT_" , error_text)
#     add_to_log("Pomelo II", tmpDir, error_type, error_text)
#     err_templ_hmtl = "Content-type: text/html\n\n" + err_templ_hmtl
#     print err_templ_hmtl

def html_error_page(error_type, error_text, tmpDir):
    error_template = open(pomelo_templates_dir + "/templ-error.html","r")
    err_templ_hmtl = error_template.read()
    error_template.close()
    err_templ_hmtl = err_templ_hmtl.replace("_ERROR_TITLE_", error_type)
    err_templ_hmtl = err_templ_hmtl.replace("_ERROR_TEXT_" , error_text)
    add_to_log("Pomelo II", tmpDir, error_type, error_text)
    f_results = open(tmpDir + "/results.html", mode = "w")
    f_results.write(err_templ_hmtl)
    f_results.close()


## For redirections, from Python Cookbook

# def getQualifiedURL(uri = None):
#     """ Return a full URL starting with schema, servername and port.
    
#     *uri* -- append this server-rooted uri (must start with a slash)
#     """
#     schema, stdport = ('http', '80')
#     host = os.environ.get('HTTP_HOST')
#     if not host:
#         host = os.environ.get('SERVER_NAME')
#         port = os.environ.get('SERVER_PORT', '80')
#         if port != stdport: host = host + ":" + port

#     result = "%s://%s" % (schema, host)
#     if uri: result = result + uri
  
#     return result


# def getScriptname():
#     """ Return te scriptname part of the URL."""
#     return os.environ.get('SCRIPT_NAME', '')


# def getBaseURL():
#     """ Return a fully qualified URL to this script. """
#     return getQualifiedURL(getScriptname())


# def commonOutput():
#     print "Content-type: text/html\n\n"
#     print """
#     <html>
#     <head>
#     <title>Pomelo II results</title>
#     </head>
#     <body>
#     """


def mpi_error():
    error_text = "<p> A technical problem has ocurred during execution. </p>"
    error_text = error_text + "<p> The webmaster will be warned and hopefully the problem will be solved soon. </p>"
    html_error_page("MPI ERROR", error_text, tmpDir)


### FIXME: This is ugly and a hack; if there is a user error, report as such!!!
    

def multest_error():
    error_text = "<p> PomeloII crashed. </p>"
    error_text = error_text + "<p> The problem could be in the code or in your data </p>"
    error_text = error_text + "<p> Below is the output from the execution: </p>"
    if os.path.exists(tmpDir + "/pomelo.msg"):
        pom_out = open(tmpDir + "/pomelo.msg")
        lines = pom_out.readlines()
        pom_out.close()
        lines = lines[:10]
        text  = ''.join(lines)
        error_text = error_text + text
        
    error_text = error_text + '<br> MACHINE: ' + str(socket.gethostname())
    html_error_page("ERROR", error_text, tmpDir)


def printPomKilled():
    error_text = "<p> Execution has exceeded maximum time (" + str(Pomelo_MAX_time/3600) + "hours).</p>"
    error_text = error_text + "<p> Either the data and options you entered produced an excessively long execution or </p>"
    error_text = error_text + "<p> a technical problem ocurred.</p>"
    html_error_page("POMELO KILLED", error_text, tmpDir)

def printOKRun():
    issue_echo2("       at 1")
    f=open(tmpDir + "/testtype")
    test_type = f.read().strip()
    f.close()
    issue_echo2("       at 2")
    draw_heatmaptable = "cd " + tmpDir + "; python " + Pomelo_cgi_dir + "/heatmap_draw_script.py;" 
    issue_echo2("       at 2.2")
    # Cox script draws its own tables
    if test_type != "Cox":
	    draw_heatmaptable = draw_heatmaptable + " python " + Pomelo_cgi_dir + "/generate_table.py"
    dummy = os.system(draw_heatmaptable)
    issue_echo2(draw_heatmaptable)
    issue_echo2("       at 2.3")
    Heatresults = open(tmpDir + "/heat_new.html")
    issue_echo2("       at 2.4")
    table_file  = open(tmpDir + "/p.v.sort.FDR.a.html")
    issue_echo2("      at 3")
    # If limma anova we use template that has the links that take you to class comparison
    if test_type == "Anova_limma":
        template    = open(pomelo_templates_dir + "/results_template_limmma_anova.html","r")
    else:
        template    = open(pomelo_templates_dir + "/results_template.html","r")
    issue_echo2("      at 3b")    
    heat_temp_f = open(pomelo_templates_dir + "/templ_heatmap.html","r")
    templ_heat  = heat_temp_f.read()
    templ_heat  = templ_heat.split("_SPLIT_ME_")
    number_arr  = tmpDir.split("/")
    var_number  = number_arr[-1]
    templ_heat[0] = templ_heat[0].replace("_TEMP_DIR_",tmpDir)
    templ_hmtl  = template.read()
    issue_echo2("      at 3c")
    temp_array  = templ_hmtl.split("_SPLIT_ME_")
    table_res   = table_file.read()
    resultsFile = Heatresults.read()
    temp_array[0] = temp_array[0].replace("_NUMBERS_",var_number)
    temp_array[0] = temp_array[0].replace("_TEMP_DIR_",tmpDir)
    temp_array[1] = temp_array[1].replace("_TEMP_DIR_",tmpDir)
    issue_echo2("      at 3d")
    final_html  = temp_array[0] + table_res + temp_array[1] + resultsFile + temp_array[2]
    final_heat_map = templ_heat[0] + resultsFile + templ_heat[1]
    issue_echo2("     before writing pre-results")
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
        ### fi,fo,fu = os.popen3('w3m -config = "/var/www/.w3m" -dump p.v.sort.FDR.d.html > results.pomelo.txt')
        fi,fo,fu = os.popen3(w3mPath + ' -dump p.v.sort.FDR.d.html > results.pomelo.txt')
        fi.close()
        fo.close()
        fu.close()
        ### when launched from python, w3m complaints about Can't create config directory
        ### which I do not understand
##    	os.system('html2text -width 200 -nobs  -o results.pomelo.txt p.v.sort.FDR.d.html')
##      html2text leaves weird characters sometimes


################################################################
################################################################
######################                  ########################
###################### End of functions ########################
######################                  ########################
################################################################
################################################################

issue_echo2("Start")
# the next line would show that we run from different depth
# dirs
# issue_echo2(os.getcwd())

test_type = open(tmpDir + "/testtype", mode = "r").readline()
try:
    num_permut = open(tmpDir + "/num_permut", mode = "r").readline()
except:
    num_permut = 1 ## just in case, although it makes no difference, but with
    ## 0 it crashed on 32 bits, in IBM cluster


### Do very first run attempt.

issue_echo2("Before first tryrrun")
tryrrun = os.system(Pomelo_cgi_dir + '/pomelo_run2.py ' + tmpDir + 
                    ' ' + test_type + ' ' + str(num_permut) +'&')

time.sleep(TIME_BETWEEN_CHECKS + random.uniform(0.01, 0.3))
issue_echo2("After first tryrrun")


### FIXME: where do we check for lam_mpi_crash and return the message that likely memory problem?

### We should change the logic for pomelo.
### If there is a user problem, we have to cycle until we get 5 crashes.
### The loop below expects a multest_parallel.res, which is not produces
### (e.g., using test test_limma_not_estimable).
### We cannot just output an empty multest_parallel.res,
### cause that would launch printOKRun, and
### lots of things there are missing.

### If we allow looping up to 5 times, then we eventually launch
### the multest_error.

### So we will do something very ugly: make the program believe we have looped
### those many times. We do this by setting number_relaunches to 99
### from within limma_functions.R

### But this should be handled in a better way!!!!!



while True:  ## we repeat until done or unrecoverale crash
    issue_echo2("top of while")
    number_relaunches = int(open(tmpDir + "/number_relaunches", mode = "r").readline())

    if (time.time() - os.path.getmtime(tmpDir + "/covariate")) > Pomelo_MAX_time:
        ## FIXME: do we want to try and relaunch??
        issue_echo2("Out of time")
        #close_lam_env()
        printPomKilled()
#         print 'Location: http://pomelo2.bioinfo.cnio.es/tmp/'+ \
#             newDir + '/results.html \n\n'
        break

    # If file pomelo_run.finished exists, it has finished 
    run_finished = os.path.exists(tmpDir + "/pomelo_run.finished")

    if run_finished:
        issue_echo2("run_finished")
        ## mpiOK is spitted out by multtestmain_paral.cpp, so the cpp code
        ## by limma_functions.R, by f1-pomelo.R
        ## we no longer start a LAM universe, and only use MPI
        ## with the cpp code, but this signals start.
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
            #close_lam_env()
	    issue_echo2("       after close_lam_env")
            printOKRun()
	    issue_echo2("       after printOKRun")
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
            #close_lam_env()
            move_run_finished = os.rename(tmpDir + '/pomelo_run.finished', 
                                          tmpDir + '/pomelo_run.crash.finished-' +
                                          str(number_relaunches - 1))
            issue_echo2("renamed pomelo_run.finished")
            tryrrun = os.system(Pomelo_cgi_dir + '/pomelo_run2.py ' + tmpDir + 
                                ' ' + test_type + ' ' + str(num_permut) +'&')
            issue_echo2("tried relaunch")
        else: ## we cannot relaunch
            if not mpi_worked:
                issue_echo2("not mpi_worked")
                #close_lam_env()
                mpi_error()
#                print 'Location: http://pomelo2.bioinfo.cnio.es/tmp/' + newDir + '/results.html \n\n'
                break

            elif not results_exist:
                issue_echo2("not results_exist")
                #close_lam_env()
                multest_error()
#                print 'Location: http://pomelo2.bioinfo.cnio.es/tmp/' + newDir + '/results.html \n\n'
                break

    time.sleep(TIME_BETWEEN_CHECKS)



### clean ups
try:
    issue_echo2('      at final try')
    numPomelo = len(glob.glob(newDirPath + "*"))
    if numPomelo > 1:
        tmptmp = os.system("rm " + newDirPath + "*")
    issue_echo2('Deleting Pom.running.procs in ' + newDirPath + '*')
except:
    None
             
burying = os.system("cd " + tmpDir + "; " + buryPomCall)
issue_echo2("at the very end")










    
# def close_lam_env():
#     try:
#         lamenv = open(tmpDir + "/lamSuffix", mode = "r").readline()
#     except:
#         None
#     try:
#         lamkill = os.system('export LAM_MPI_SESSION_SUFFIX=' + lamenv + '; lamhalt -H; lamwipe -H')
#     except:
#         None
#     try:
#         ## probably redundant, and fills error logs.
#         numPomelo = len(glob.glob("/http/pomelo2/www/Pom.running.procs/Pom." + newDir + "*"))
#         if numPomelo > 1:
#             tmptmp = os.system("rm /http/pomelo2/www/Pom.running.procs/Pom." + newDir + "*")
#     except:
#         None



# def did_lam_crash(tmpDir, machine_root = 'karl'):
#     """ Verify whether LAM/MPI crashed by checking logs and f1.Rout
#     for single universe lamboot."""
#     OTHER_LAM_MSGS = 'Call stack within LAM:'
#     lam_logs = glob.glob(tmpDir + '/' + machine_root + '*.*.*.log')
#     try:
#         in_error_msg = int(os.popen('grep MPI_Error_string ' + \
#                                     tmpDir + '/f1-pomelo.Rout | wc').readline().split()[0])
#     except:
#         in_error_msg = 0
# #     no_universe = int(os.popen('grep "Running serial version of papply" ' + \
# #                                tmpDir + '/f1.Rout | wc').readline().split()[0])
# ## We do NOT want that, because sometimes a one node universe is legitimate!!!
#     if in_error_msg > 0:
#         for lam_log in lam_logs:
#             os.system('rm ' + lam_log)
# #     elif no_universe > 0:
# #         os.system("sed -i 's/Running serial version of papply/already_seen:running serial version of papply/g'" + \
# #                   tmpDir + "/f1.Rout")
#     else: ## look in lam logs
#         in_lam_logs = 0
#         for lam_log in lam_logs:
#             tmp1 = int(os.popen('grep "' + OTHER_LAM_MSGS + '" ' + \
#                                 lam_log + ' | wc').readline().split()[0])
#             if tmp1 > 0:
#                 in_lam_logs = 1
#                 break
#     if (in_error_msg > 0) or (in_lam_logs > 0):
#         return True
#     else:
#         return False


# ## to keep executing myself:
# def relaunchCGI():
#     print "Content-type: text/html\n\n"
#     old_html = open(tmpDir + "/results.html")
#     html_data = old_html.read()
#     old_html.close()
#     print html_data
