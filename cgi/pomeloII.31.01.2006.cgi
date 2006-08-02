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
# import cgitb
# cgitb.enable() ## zz: eliminar for real work?
sys.stderr = sys.stdout

MAX_poms = 15 ## Max number of pomelo2 running
MAX_time = 3600 * 24 * 5 ## 5 is days until deletion of a tmp directory
Pom_MAX_time = 3600 * 12 ## 12 hours is max duration allowed for any process
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
    <title>Pomelo II</title>
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
    if not fieldName == "survival_time":  ### zzz ???
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
os.chmod(tmpDir, 0770)


### File and parameter upload
fs = cgi.FieldStorage()

idtype     = radioUpload('idtype', acceptedIDTypes)
organism   = radioUpload('organism', acceptedOrganisms)
test_type  = radioUpload('testtype', acceptedTests)
num_permut = valueNumUpload('num_permut', 'int' , 1000)


## zz: I think this won't work. Needs to check:
## if Cox: the three files; o.w. two files.


##check if file coming from preP

if(fs.getfirst("covariate2")!= None):
    prep_tmpdir = fs.getfirst("covariate2")
    shutil.copy("/http/prep/www/tmp/" + prep_tmpdir +"/covariate",tmpDir + "/covariate")
else:

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


### Where is censored status loaded??zz
### Is survival time the same as the file for regression??zz



## Upload worked OK. We store the original names of the files in the
## browser for later report:
## We'll need to get this working for the validation data.zz
fileNamesBrowser = open(tmpDir + '/fileNamesBrowser', mode = 'w')
if(fs.getfirst("covariate2")== None):
    fileNamesBrowser.write(fs['covariate'].filename + '\n')
fileNamesBrowser.write(fs['survival_time'].filename + '\n')
fileNamesBrowser.write(fs['class_labels'].filename + '\n')
fileNamesBrowser.close()

## If a process lasts longer than the Pom_MAX_time, kill it and delete files asociated
PomrunningFiles = dircache.listdir("/http/pomelo2/www/Pom.running.procs")
for Pomtouchfile in PomrunningFiles:
    tmpS = "/http/pomelo2/www/Pom.running.procs/" + Pomtouchfile
    if (currentTime - os.path.getmtime(tmpS)) > Pom_MAX_time:
        os.remove(tmpS)
	aux_num_dir = Pomtouchfile.split(".")[1]
	num_Oldir   = aux_num_dir.split("@")[0]
	oldDir = "/http/pomelo2/www/tmp/" + num_Oldir
	try:
		lamenv = open(oldDir + "/lamSuffix", mode = "r").readline()
	except:
		None
	try:
		os.system('export LAM_MPI_SESSION_SUFFIX=' + lamenv + '; lamhalt -H; lamwipe -H')
	except:
		None
	try:
		shutil.rmtree(oldDir)
	except:
		None

# Check to see if a new pomelo can be run
numPomelo = len(glob.glob("/http/pomelo2/www/Pom.running.procs/Pom.*"))
if numPomelo > MAX_poms:
    shutil.rmtree(tmpDir)
    commonOutput()
    print "<h1> Pomelo2 problem: The servers are too busy </h1>"
    print "<p> Because of the popularity of the application "
    print " the maximum number of simultaneous runs of Pomelo2 has been reached.</p>"
    print "<p> Please try again later.</p>"
    print "<p> We apologize for the inconvenience.</p>"    
    print "</body></html>"
    sys.exit()

################        Launching Pomelo   ###############

# prepare the arrayNames file:

covarInServer = tmpDir + "/covariate"
arrayNames = tmpDir + "/arrayNames"
srvfile = open(covarInServer, mode = 'rU')
arrayfile = open(arrayNames, mode = 'w')

### Checking no commas and verifying other issues (using R).
covarR = open(tmpDir + '/covarR', mode = 'w')

all_covar_lines = srvfile.readlines()
srvfile.close()

for nr in range(0, len(all_covar_lines)):
    line = all_covar_lines[nr]
    if (line.find("#name") == 0) or (line.find("#NAME") == 0) or (line.find("#Name") == 0):
        arrayfile.write(line)
        arrayfile.write("\n\n")
        arrayfile.close()
        os.chmod(arrayNames, 0660)
    elif (line.find("#", 0, 1) == 0):
    	continue
    else:
        line_splitted = line.split('\t', 1)[-1]
        if line_splitted.find(',') >= 0:
            commonOutput()
            print "<h1> Pomelo ERROR </h1>"
            print """<p> You have commas in the data matrix.
            You probably are using commas instead of "." for the
            decimal separator. Please, use a "." instead of a
            ",".</p>
            """
            covarR.close()
            sys.exit()
        else:
            if line_splitted.rstrip():
                covarR.write(line_splitted)
covarR.close()



## checking constant genes and missings is done with R zz
if test_type == 't' or test_type == 'FisherIxJ' or test_type =='Anova':
    os.system('cp /http/pomelo2/cgi/testDiscrete.R ' + tmpDir + '/.')
    Rcommand = "cd " + tmpDir + "; " + "/usr/bin/R CMD BATCH --no-restore --no-readline --no-save -q testDiscrete.R 2> error.msg "
    Rrun = os.system(Rcommand)
    if os.path.exists(tmpDir + '/errorInput'):
        commonOutput()
	print "<h1> Pomelo ERROR </h1>"
        rif = open(tmpDir + '/errorInput', mode = 'r')
        rift = rif.read()
        print(cgi.escape(rift))
        rif.close()
        sys.exit()
else:
    os.system('cp /http/pomelo2/cgi/testContinuous.R ' + tmpDir + '/.')
    Rcommand = "cd " + tmpDir + "; " + "/usr/bin/R CMD BATCH --no-restore --no-readline --no-save -q testContinuous.R 2> error.msg "
    Rrun = os.system(Rcommand)
    if os.path.exists(tmpDir + '/errorInput'):
        commonOutput()
        print "<h1> Pomelo ERROR </h1>"
        rif = open(tmpDir + '/errorInput', mode = 'r')
        rift = rif.read()
        print(cgi.escape(rift))
        rif.close()
        sys.exit()




## It would be good to use spawnl or similar instead of system,
## but I have no luck with R. This, I keep using system.
## Its safety depends crucially on the newDir not being altered,
## but newDir is not passed from any other user-reachable place
## (it is created here).

dummy = os.system('cp /http/pomelo2/cgi/new_heatmap.R ' + tmpDir + '/.')
##old macs issues
dummy = os.system("cd " + tmpDir +"; /bin/sed 's/\\r\\n/\\n/g' covariate > tmpc; mv tmpc covariate; /bin/sed 's/\\r/\\n/g' covariate > tmpc; mv tmpc covariate")
touchPomrunning = os.system("/bin/touch /http/pomelo2/www/Pom.running.procs/Pom." + newDir + "@" + socket.gethostname())
dummy = os.system('ln -s /http/pomelo2/bin/multest_paral ' + tmpDir + '/multest_paral')
tryrrun = os.system('/http/mpi.log/pomelo_run.py ' + tmpDir + ' ' + test_type + ' ' + str(num_permut) +'&')
createResultsFile = os.system("/bin/touch " + tmpDir + "/results.txt")


###########   Creating a results.hmtl   ###############

## Copy to tmpDir a results.html that redirects to checkdone.cgi
## If communication gets broken, there is always a results.html
## that will do the right thing.
# shutil.copy("/http/pomelo2/www/tmp/results-pre.html", tmpDir)
shutil.copy("/http/pomelo2/www/Pomelo2_html_templates/results-pre.html", tmpDir)
os.system("cd " + tmpDir + "; /bin/sed 's/sustituyeme/" +
          newDir + "/g' results-pre.html > results.html; rm results-pre.html")

##############    Redirect to checkdone.cgi    ##################
print "Location: "+ getQualifiedURL("/cgi-bin/pomelo_checkdone.cgi") + "?newDir=" + newDir, "\n\n"
# commonOutput()
# print "Todo ha ido chachi"
