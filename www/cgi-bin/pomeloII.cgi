#!/usr/bin/python2.4

import glob
import socket
import sys
import os
import cgi 
##import types
import time
import shutil
import dircache
##import string
import random
##import re
from stat import ST_SIZE
import cgitb
cgitb.enable() ## zz: eliminar for real work?
sys.stderr = sys.stdout

MAX_signs = 4 ## MAX_genesrf + 1 = Maximum number of R processes running at same time.
MAX_time = 3600 * 24 * 5 ## 5 is days until deletion of a tmp directory
R_MAX_time = 3600 * 8 ## 8 hours is max duration allowed for any process
MAX_covariate_size = 363948523L ## a 500 * 40000 array of floats
MAX_time_size = 61897L

acceptedIDTypes = ('None', 'cnio', 'affy', 'clone', 'acc', 'ensembl', 'entrez', 'ug')
acceptedOrganisms = ('None', 'Hs', 'Mm', 'Rn')
acceptedTests = ('t','FisherIxJ','Anova','Cox','Regres')

def commonOutput():
    print "Content-type: text/html\n\n"
    print """
    <html>
    <head>
    <title>Pomelo</title>
    </head>
    <body>
    """

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

def fileUpload(fieldName):
    """Upload and get the files and do some checking. We assume there is an existing call
    to fs = cgi.FieldStorage()"""
    ## we don't deal with OS specific "\n"
    ## because R does not have a problem (at least with Windows files)
    ## no problem in R either with empty carriage returns at end of file

    if fs.has_key(fieldName):
        fileClient = fs[fieldName].file
        if not fileClient:
            shutil.rmtree(tmpDir)
            commonOutput()
            print "<h1> Pomelo ERROR </h1>"
            print "<p> The ", fieldName, "file you entered is not a file </p>"
            print "<p> Please fill up the required fields and try again</p>"
            print "</body></html>"
            sys.exit()
    else:
        shutil.rmtree(tmpDir)
        commonOutput()
        print "<h1> Pomelo ERROR </h1>"    
        print "<p> ", fieldName, "file required </p>"
        print "<p> Please fill up the required fields and try again</p>"
        print "</body></html>"
        sys.exit()
    # transferring files to final destination;
    fileInServer = tmpDir + "/" + fieldName
    srvfile = open(fileInServer, mode = 'w')
    fileString = fs[fieldName].value
    srvfile.write(fileString)
    srvfile.close()
    ## this is slower than reading all to memory and copying from
    ## there, but this is less taxing on memory.
    ## but with the current files, probably not worth it
    #     while 1:
    #         line = fileClient.readline()
    #         if not line: break
    #         srvfile.write(line)
    #     srvfile.close()
    os.chmod(fileInServer, 0666)
    if not fieldName == "survival_time":
	if os.path.getsize(fileInServer) == 0:
		#shutil.rmtree(tmpDir)
		commonOutput()
		print "<h1> Pomelo ERROR </h1>"
		print "<p>", fieldName, " file has size 0 </p>"
		print "<p> Please enter a file with something in it.</p>"
		print "</body></html>"
		sys.exit()


def valueNumUpload(fieldName, testNumber = 'float', minValue = 0):
    """Upload and get the values and do some checking. For text and radio selections
    with positive numeric data.
    We assume there is an existing call to fs = cgi.FieldStorage()"""

    if not fs.has_key(fieldName):
        shutil.rmtree(tmpDir)
        commonOutput()
        print "<h1> Pomelo ERROR </h1>"
        print "<p> ", fieldName, "value required </p>"
        print "<p> Please fill up the required fields and try again</p>"
        print "</body></html>"
        sys.exit()
    if fs[fieldName].filename:
        shutil.rmtree(tmpDir)
        commonOutput()
        print "<h1> Pomelo ERROR </h1>"
        print "<p> ", fieldName, "should not be a file. </p>"
        print "<p> Please fill up the required fields and try again</p>"
        print "</body></html>"
        sys.exit()
    if type(fs[fieldName]) == type([]):
        shutil.rmtree(tmpDir)
        commonOutput()
        print "<h1> Pomelo ERROR </h1>"
        print "<p> ", fieldName, "should be a single value.</p>"
        print "<p> Please fill up the required fields and try again</p>"
        print "</body></html>"
        sys.exit()
    else:
        tmp = fs[fieldName].value

    ## Accept only numeric values that can be turned to floats or ints
    if testNumber == 'float':
        try:
            tmpn = float(tmp)
        except:
            commonOutput()
            print "<h1> Pomelo ERROR </h1>"
            print "<p> ", fieldName, "is not a valid numeric value.</p>"
            print "<p> Please fill up the required fields and try again</p>"
            print "</body></html>"
            sys.exit()
    else:
        try:
            tmpn = int(tmp)
        except:
            commonOutput()
            print "<h1> Pomelo ERROR </h1>"
            print "<p> ", fieldName, "is not a valid numeric value.</p>"
            print "<p> Please fill up the required fields and try again</p>"
            print "</body></html>"
            sys.exit()

    if tmpn < minValue:
        shutil.rmtree(tmpDir)
        commonOutput()
        print "<h1> Pomelo ERROR </h1>"
        print "<p> ", fieldName, "smaller than smallest accepted value (", minValue, "). </p>"
        print "<p> Please fill up the required fields and try again</p>"
        print "</body></html>"
        sys.exit()

    # transferring files to final destination;

    fileInServer = tmpDir + "/" + fieldName
    srvfile = open(fileInServer, mode = 'w')
    srvfile.write(str(tmpn))
    srvfile.close()
    os.chmod(fileInServer, 0666)

    return tmpn

def radioUpload(fieldName, acceptedValues):
    """Upload and get the values and do some checking. For radio selections
    with text data; check those are in acceptedValues.
    We assume there is an existing call to fs = cgi.FieldStorage()"""

    if not fs.has_key(fieldName):
        shutil.rmtree(tmpDir)
        commonOutput()
        print "<h1> Pomelo ERROR </h1>"
        print "<p>", fieldName, "required </p>"
        print "<p> Please fill up the required fields and try again</p>"
        print "</body></html>"
        sys.exit()
    if fs[fieldName].filename:
        shutil.rmtree(tmpDir)
        commonOutput()
        print "<h1> Pomelo ERROR </h1>"
        print "<p> ", fieldName, "should not be a file. </p>"
        print "<p> Please fill up the required fields and try again</p>"
        print "</body></html>"
        sys.exit()
    if type(fs[fieldName]) == type([]):
        shutil.rmtree(tmpDir)
        commonOutput()
        print "<h1> Pomelo ERROR </h1>"
        print "<p>", fieldName, "should be a single value.</p>"
        print "<p> Please fill up the required fields and try again</p>"
        print "</body></html>"
        sys.exit()
    else:
        tmp = fs[fieldName].value
            
    if tmp not in acceptedValues:
        shutil.rmtree(tmpDir)
        commonOutput()
        print "<h1> Pomelo ERROR </h1>"
        print "<p> The", fieldName, "choosen is not valid.</p>"
        print "<p> Please fill up the required fields and try again.</p>"
	print "Your value:" + tmp + " accepted values " + str(acceptedValues)
        print "</body></html>"
        sys.exit()

    fileInServer = tmpDir + "/" + fieldName
    srvfile = open(fileInServer, mode = 'w')
    fileString = tmp
    srvfile.write(fileString)
    srvfile.close()
    os.chmod(fileInServer, 0666)

    return tmp




#########################################################
#########################################################

####          Execution starts here      ################

#########################################################
#########################################################



## Deleting tmp directories older than MAX_time
currentTime = time.time()
currentTmp = dircache.listdir("/http/pomelo2/www/tmp")
for directory in currentTmp:
    tmpS = "/http/pomelo2/www/tmp/" + directory
    if (currentTime - os.path.getmtime(tmpS)) > MAX_time:
        shutil.rmtree(tmpS)


### Creating temporal directories
newDir = str(random.randint(1, 10000)) + str(os.getpid()) + str(random.randint(1, 100000)) + str(int(currentTime)) + str(random.randint(1, 10000))
redirectLoc = "/tmp/" + newDir
tmpDir = "/http/pomelo2/www/tmp/" + newDir
os.mkdir(tmpDir)
os.chmod(tmpDir, 0700)


### File and parameter upload
fs = cgi.FieldStorage()

idtype     = radioUpload('idtype', acceptedIDTypes)
organism   = radioUpload('organism', acceptedOrganisms)
test_type  = radioUpload('testtype', acceptedTests)
num_permut = valueNumUpload('num_permut', 'int' , 50)

## Uploading files and checking not abusively large
fileUpload('covariate')
if os.stat(tmpDir + '/covariate')[ST_SIZE] > MAX_covariate_size:
    shutil.rmtree(tmpDir)
    commonOutput()
    print "<h1> Pomelo ERROR </h1>"
    print "<p> Covariate file way too large </p>"
    print "<p> Covariate files this size not allowed.</p>"
    print "</body></html>"
    sys.exit()

fileUpload('survival_time')
if os.stat(tmpDir + '/survival_time')[ST_SIZE] > MAX_time_size:
    shutil.rmtree(tmpDir)
    commonOutput()
    print "<h1> Pomelo ERROR </h1>"
    print "<p> Survival time file way too large </p>"
    print "<p> This size is not allowed.</p>"
    print "</body></html>"
    sys.exit()

fileUpload('class_labels')
if os.stat(tmpDir + '/class_labels')[ST_SIZE] > MAX_time_size:
    shutil.rmtree(tmpDir)
    commonOutput()
    print "<h1> Pomelo ERROR </h1>"
    print "<p> Class labels file way too large </p>"
    print "<p> This size is not allowed.</p>"
    print "</body></html>"
    sys.exit()

## Upload worked OK. We store the original names of the files in the
## browser for later report:
## We'll need to get this working for the validation data.zz
fileNamesBrowser = open(tmpDir + '/fileNamesBrowser', mode = 'w')
fileNamesBrowser.write(fs['covariate'].filename + '\n')
fileNamesBrowser.write(fs['survival_time'].filename + '\n')
fileNamesBrowser.write(fs['class_labels'].filename + '\n')
fileNamesBrowser.close()




## current number of processes > max number of processes?
## and we do it here, not before, so that we have the most
## current info about number of process right before we launch R.


# ## First, delete any R file left (e.g., from killing procs, etc).
# RrunningFiles = dircache.listdir("/http/signs/www/R.running.procs")
# for Rtouchfile in RrunningFiles:
#     tmpS = "/http/signs/www/R.running.procs/" + Rtouchfile
#     if (currentTime - os.path.getmtime(tmpS)) > R_MAX_time:
#         os.remove(tmpS)

## Now, verify any processes left
# numPomelo = len(glob.glob("/http/signs/www/Pom.running.procs/Pom.*@*%*"))
# if numPomelo > MAX_signs:
#     shutil.rmtree(tmpDir)
#     commonOutput()
#     print "<h1> Pomelo problem: The servers are too busy </h1>"
#     print "<p> Because of the popularity of the application "
#     print " the maximum number of simultaneous runs of Pomelo has been reached.</p>"
#     print "<p> Please try again later.</p>"
#     print "<p> We apologize for the inconvenience.</p>"    
#     print "</body></html>"
#     sys.exit()

################        Launching Pomelo   ###############

# prepare the arrayNames file:

covarInServer = tmpDir + "/covariate"
arrayNames = tmpDir + "/arrayNames"
srvfile = open(covarInServer, mode = 'r')
arrayfile = open(arrayNames, mode = 'w')

while 1:
    line = srvfile.readline()
    if not line: break
    if (line.find("#name") == 0) or (line.find("#NAME") == 0) or (line.find("#Name") == 0):
        arrayfile.write(line)
        arrayfile.write("\n\n")
        break

srvfile.close()
arrayfile.close()
os.chmod(arrayNames, 0600)

## It would be good to use spawnl or similar instead of system,
## but I have no luck with R. This, I keep using system.
## Its safety depends crucially on the newDir not being altered,
## but newDir is not passed from any other user-reachable place
## (it is created here).

touchPomrunning = os.system("/bin/touch /http/pomelo2/www/Pom.running.procs/Pom." + newDir + "@" + socket.gethostname())
dummy = os.system('ln -s /home/mpi/PRUEBAS_PARALELO/PARALEL_APP_WEB/multest_paral ' + tmpDir + '/multest_paral')
tryrrun = os.system('/http/mpi.log/pomelo_run.py ' + tmpDir + ' ' + test_type + ' ' + str(num_permut) +'&')
createResultsFile = os.system("/bin/touch " + tmpDir + "/results.txt")


###########   Creating a results.hmtl   ###############

## Copy to tmpDir a results.html that redirects to checkdone.cgi
## If communication gets broken, there is always a results.html
## that will do the right thing.
shutil.copy("/http/pomelo2/www/tmp/results-pre.html", tmpDir)
os.system("cd " + tmpDir + "; /bin/sed 's/sustituyeme/" +
          newDir + "/g' results-pre.html > results.html; rm results-pre.html")

##############    Redirect to checkdone.cgi    ##################
print "Location: "+ getQualifiedURL("/cgi-bin/pomelo_checkdone.cgi") + "?newDir=" + newDir, "\n\n"
# commonOutput()
# print "Todo ha ido chachi"
