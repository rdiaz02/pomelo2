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
##import string
import signal
import re
##import glob
import tarfile
import string
#import cgitb
#cgitb.enable() ## zz: eliminar for real work?
sys.stderr = sys.stdout ## eliminar?

Pomelo_MAX_time = 8 * 3600 ## 4 hours is max duration allowd for any process

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
#     print """
#     <html>
#     <head>
#     """
#     print '<meta http-equiv="Refresh"'
#     print 'content="30; URL=' + getBaseURL() + '?newDir=' + newDir + '">'
#     print '<title>Pomelo II results</title>'
#     print '</head> <body>'
#     print '<p> This is an autorefreshing page; your results will eventually be displayed here.\n'
#     print 'If your browser does not autorefresh, the results will be kept for five days at</p>'
#     print '<p><a href="' + getBaseURL() + '?newDir=' + newDir + '">', 'http://pomelo2.bioinfo.cnio.es/tmp/'+ newDir + '/results.html</a>.' 
#     print '</p> </body> </html>'
    
## Output-generating functions
def printErrorRun():
    Pom_results = open(tmpDir + "/pomelo.msg")
    resultsFile = Pom_results.read()
    outf = open(tmpDir + "/pre-results.html", mode = "w")
    outf.write("<html><head><title>Pomelo II results </title></head><body>\n")
    outf.write("<h1> ERROR: There was a problem with Pomelo </h1> \n")
    outf.write("<p>  This could be a bug on our code, or a problem  ")
    outf.write("with your data (that we hadn't tought of). Below is all the output from the execution ")
    outf.write("of the run. Unless it is obvious to you that this is a fault of your data ")
    outf.write("(and that there is no way we could have avoided the crash) ")
    outf.write("please let us know so we can fix the problem. ")
    outf.write("Please sed us this URL and the output below</p>")
    outf.write("<p> This is the results file:<p>")
    outf.write("<pre>")
    outf.write(cgi.escape(resultsFile))
    outf.write("</pre>")
    outf.write("</body></html>")
    outf.close()
    Pom_results.close()
    shutil.copyfile(tmpDir + "/pre-results.html", tmpDir + "/results.html")



def printOKRun():
#    dummy = os.system("cd " + tmpDir + "; python /http/pomelo2/cgi/heatmap_draw_script.py << heat_table.log; python2.4 /http/pomelo2/cgi/generate_table.py; << heat_table.log")
#    dummy = os.system("cd " + tmpDir + "; python /http/pomelo2/cgi/heatmap_draw_script_ramon.py << heat_table.log; python2.4 /http/pomelo2/cgi/generate_table.py; << heat_table.log")
    dummy = os.system("cd " + tmpDir + "; python /http/pomelo2/cgi/heatmap_draw_script_ramon.py; python2.4 /http/pomelo2/cgi/generate_table.py")
    Heatresults = open(tmpDir + "/heat_new.html")
    table_file  = open(tmpDir + "/p.v.sort.FDR.a.html")
#     template    = open("/http/pomelo2/www/results_template.html","r")
#     heat_temp_f = open("/http/pomelo2/www/tmp/templ_heatmap.html","r")
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

    

def printPomKilled():
    Rresults = open(tmpDir + "/pomelo.msg")
    resultsFile = Rresults.read()
    outf = open(tmpDir + "/pre-results.html", mode = "w")
    outf.write("<html><head><title>Pomelo II results </title></head><body>\n")
    outf.write("<h1> ERROR: Pomelo process killed </h1> \n")
    outf.write("<p>  Pomelo execution lasted longer than the maximum  allowed time, ")
    outf.write(str(Pomelo_MAX_time))
    outf.write(" seconds,  and was killed.")
    ###     outf.write("<p> This is the output from the R run:<p>")
    ###     outf.write("<pre>")
    ###     outf.write(cgi.escape(soFar))
    ###     outf.write("</pre>")
    outf.write("<p> This is the results file:<p>")
    outf.write("<pre>")
    outf.write(cgi.escape(resultsFile))
    outf.write("</pre>")
    outf.write("</body></html>")
    outf.close()
    Rresults.close()
    shutil.copyfile(tmpDir + "/pre-results.html", tmpDir + "/results.html")

    ## Changing to the appropriate directory


form = cgi.FieldStorage()
if form.has_key('newDir'):
   value=form['newDir']
   if type(value) is types.ListType:
       commonOutput()
       print "<h1> ERROR </h1>"    
       print "<p> newDir should not be a list. </p>"
       print "<p> Anyone trying to mess with it?</p>"
       print "</body></html>"
       sys.exit()
   else:
       newDir = value.value
else:
    commonOutput()
    print "<h1> ERROR </h1>"
    print "<p> newDir is empty. /p>"
    print "</body></html>"
    sys.exit()

if re.search(r'[^0-9]', str(newDir)):
    ## newDir can ONLY contain digits
    commonOutput()
    print "<h1> ERROR </h1>"
    print "<p> newDir does not have a valid format. </p>"
    print "<p> Anyone trying to mess with it?</p>"
    print "</body></html>"
    sys.exit()

redirectLoc = "/tmp/" + newDir
tmpDir = "/http/pomelo2/www/tmp/" + newDir

if not os.path.isdir(tmpDir):
    commonOutput()
    print "<h1> ERROR </h1>"
    print "<p> newDir is not a valid directory. </p>"
    print "<p> Anyone trying to mess with it?</p>"
    print "</body></html>"
    sys.exit()

## Were we already done in a previous execution?
## No need to reopen files or check anything else. Return url with results
## and bail out.
# if os.path.exists(tmpDir + "/natural.death.pid.txt") or os.path.exists(tmpDir + "/killed.pid.txt"):
#      print 'Location: http://pomelo2.bioinfo.cnio.es/tmp/'+ newDir + '/results.html \n\n'
#      sys.exit()

try:
# 	file_size = os.path.getsize(tmpDir + "/pomelo.msg")
	f_pom_msg = open(tmpDir + "/pomelo.msg", mode = "r").read()
	#If the file exists try to find multest_parallel.res in the file, indicating correct finalization
	pom_dummy = f_pom_msg.index("multest_parallel.res")
	file_size = 1 # Non zero number indicating the file is not empty
except:
	file_size = 0

finishedOK = os.path.exists(tmpDir + "/multest_parallel.res")

if (not file_size == 0) and (not finishedOK):
	errorRun = True
else:
	errorRun = False


if not finishedOK:
	if (time.time() - os.path.getmtime(tmpDir + "/covariate")) > Pomelo_MAX_time:
		lamenv = open(tmpDir + "/lamSuffix", mode = "r").readline()
		try:
			os.system('export LAM_MPI_SESSION_SUFFIX=' + lamenv + '; lamhalt -H; lamwipe -H')
		except:
			None
	
		printPomKilled()
		try:
			os.system("rm /http/pomelo2/www/Pom.running.procs/Pom." + newDir + "*")
		except:
			None
		print 'Location: http://pomelo2.bioinfo.cnio.es/tmp/'+ newDir + '/results.html \n\n'
		sys.exit()
	
	if errorRun:
		printErrorRun()

		try:
			lamenv = open(tmpDir + "/lamSuffix", mode = "r").readline()
		except:
			None
		try:
			os.system('export LAM_MPI_SESSION_SUFFIX=' + lamenv + '; lamhalt -H; lamwipe -H')
		except:
			None
		try:
			os.system("rm /http/pomelo2/www/Pom.running.procs/Pom." + newDir + "*")
		except:
			None
		print 'Location: http://pomelo2.bioinfo.cnio.es/tmp/' + newDir + '/results.html \n\n'
		sys.exit()
	else:
		relaunchCGI()
elif finishedOK:
    try:
        lamenv = open(tmpDir + "/lamSuffix", mode = "r").readline()
    except:
        None
    try:
        lamkill = os.system('export LAM_MPI_SESSION_SUFFIX=' + lamenv + '; lamhalt -H; lamwipe -H')
    except:
        None
    printOKRun()

    try:
        os.system("rm /http/pomelo2/www/Pom.running.procs/Pom." + newDir + "*")
    except:
        None
    print 'Location: http://pomelo2.bioinfo.cnio.es/tmp/'+ newDir + '/results.html \n\n'