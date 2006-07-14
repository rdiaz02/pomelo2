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
#import cgitb;cgitb.enable() ## zz: eliminar for real work?
import fcntl
sys.stderr = sys.stdout ## eliminar?

Pomelo_MAX_time = 8 * 3600 ## 8 hours is max duration allowd for any process

# *************************************************************************************
# *********************         Functions        **************************************

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

def cgi_error_page(error_type, error_text, tmpDir):
    error_template = open("/http/pomelo2/www/Pomelo2_html_templates/templ-error.html","r")
    err_templ_hmtl = error_template.read()
    error_template.close()
    err_templ_hmtl = err_templ_hmtl.replace("_ERROR_TITLE_", error_type)
    err_templ_hmtl = err_templ_hmtl.replace("_ERROR_TEXT_" , error_text)
    add_to_log("Pomelo II", tmpDir, error_type, error_text)
    err_templ_hmtl = "Content-type: text/html\n\n" + err_templ_hmtl 
    print err_templ_hmtl

def commonOutput():
    print "Content-type: text/html\n\n"
    print """
    <html>
    <head>
    <title>Pomelo II results</title>
    </head>
    <body>
    """    

        
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

covariables_cgi_template = "/http/pomelo2/www/Pomelo2_html_templates/add_covariables_template.html"
f = open(covariables_cgi_template)
template = f.read()
f.close()
template = template.replace("_SUBS_DIR_", tmpDir)
templ_hmtl = "Content-type: text/html\n\n" + template
print templ_hmtl


