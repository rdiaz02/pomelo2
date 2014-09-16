#!/usr/bin/python
# -*- mode: python ; -*-

####  Copyright (C)  2003-2005, Ramon Diaz-Uriarte <rdiaz02@gmail.com>,
####                 2005-2009, Edward R. Morrissey and 
####                            Ramon Diaz-Uriarte <rdiaz02@gmail.com> 

#### This program is free software; you can redistribute it and/or
#### modify it under the terms of the Affero General Public License
#### as published by the Affero Project, version 1
#### of the License.

#### This program is distributed in the hope that it will be useful,
#### but WITHOUT ANY WARRANTY; without even the implied warranty of
#### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#### Affero General Public License for more details.

#### You should have received a copy of the Affero General Public License
#### along with this program; if not, you can download if
#### from the Affero Project at http://www.affero.org/oagpl.html


import sys
import os
import cgi
import types
import time
# import shutil
# import signal
import re
# import tarfile
# import string

import cgitb; cgitb.enable() ## zz: eliminar for real work? NOPE!

import fcntl
sys.stderr = sys.stdout  # eliminar?

sys.path.append("../../web-apps-common")
from web_apps_config import web_apps_common_dir, \
    ROOT_POMELO_DIR, pomelo_templates_dir, ROOT_POMELO_TMP_DIR



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

def add_to_log(application, tmpDir, error_type,error_text):
    date_time = time.strftime('%Y\t%m\t%d\t%X')
    # Truncate error text
    error_text = error_text[:300]
    outstr = '%s\t%s\t%s\t%s\n%s\n' % (application, date_time, error_type, tmpDir, error_text)
    cf = open(web_apps_common_dir + '/app_caught_error', mode = 'a')
    fcntl.flock(cf.fileno(), fcntl.LOCK_SH)
    cf.write(outstr)
    fcntl.flock(cf.fileno(), fcntl.LOCK_UN)
    cf.close()

def cgi_error_page(error_type, error_text, tmpDir):
    error_template = open(ROOT_POMELO_DIR + "/www/Pomelo2_html_templates/templ-error.html","r")
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
tmpDir = ROOT_POMELO_TMP_DIR + "/" +  newDir

if not os.path.isdir(tmpDir):
    err_msg = "<p> newDir is not a valid directory. </p>"
    err_msg = err_msg + "<p> Anyone trying to mess with it?</p>"
    err_msg = err_msg + "<p> This is newDir" + tmpDir + "</p>"
    cgi_error_page("URL ERROR", err_msg, '-')
    sys.exit()
# ***********************************************************

covariables_cgi_template = pomelo_templates_dir + "/add_covariables_template.html"
f = open(covariables_cgi_template)
template = f.read()
f.close()
template = template.replace("_SUBS_DIR_", tmpDir)

if os.path.exists(tmpDir + '/COVARIABLES/added-example-covariables'):
    name_example_added_covs = file(tmpDir + '/COVARIABLES/added-example-covariables').readline()
    template = template.replace('<INPUT TYPE="file" NAME="covariables">',
                                '<span style="color:red"> Data from ' +
                                name_example_added_covs + '</span>')
    
templ_hmtl = "Content-type: text/html\n\n" + template
print templ_hmtl


