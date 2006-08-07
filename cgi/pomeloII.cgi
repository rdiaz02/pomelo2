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
import fcntl
#import cgitb;cgitb.enable() ## zz: eliminar for real work?
sys.stderr = sys.stdout

MAX_poms = 15 ## Max number of pomelo2 running
MAX_time = 3600 * 24 * 5 ## 5 is days until deletion of a tmp directory
Pom_MAX_time = 3600 * 12 ## 12 hours is max duration allowed for any process
MAX_covariate_size = 363948523L ## a 500 * 40000 array of floats
MAX_time_size = 61897L

#************  SELENIUM STUFF **************
covariate_sel_file = "/http/pomelo2/www/selenium-core-0.7.1/TEST_DATA/EXPRESSION_Anova-limma"
class_lab_sel_file = "/http/pomelo2/www/selenium-core-0.7.1/TEST_DATA/CLASS_LABELS_Anova-limma"

#*******************************************

acceptedIDTypes        = ('None', 'cnio', 'affy', 'clone', 'acc', 'ensembl', 'entrez', 'ug', 'swissp', 'rsdna', 'rspep')
acceptedOrganisms      = ('None', 'Hs', 'Mm', 'Rn')
acceptedTests          = ('t', 'FisherIxJ', 'Anova', 'Cox', 'Regres', 't_limma', 't_limma_paired','Anova_limma')
permutation_tests      = ('t', 'Anova', 'Regres')
testDiscrete_tests     = ('t', 'FisherIxJ', 'Anova', 't_limma', 't_limma_paired','Anova_limma')
limma_covariable_tests = ('Anova_limma') 

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

    # Easy solution to name issue
    error_text = error_text.replace("covariate","Gene expression")
    error_text = error_text.replace("\n","<br>")
    
    err_templ_hmtl = err_templ_hmtl.replace("_ERROR_TITLE_", error_type)
    err_templ_hmtl = err_templ_hmtl.replace("_ERROR_TEXT_",  error_text)
    add_to_log("Pomelo II", "-", error_type, error_text)
    err_templ_hmtl = "Content-type: text/html\n\n" + err_templ_hmtl 
    print err_templ_hmtl


def create_classcomp_html():
    template_file = open("/http/pomelo2/www/Pomelo2_html_templates/templ_contrasts_main.html","r")
    templ_text    = template_file.read()
    template_file.close()
    f = open(tmpDir + "/diff_classes","r");classes = f.read().split("\t");f.close()
    opt_list = []
    for class_i in classes:
        opt_indv = " <option value='" + class_i + "'>" + class_i + "</option>"
        opt_list.append(opt_indv)

    repl_text = ''.join(opt_list)
    templ_text = templ_text.replace("_REPLACE_OPTS_",repl_text)
    templ_text = templ_text.replace("_SUBS_DIR_",tmpDir)
    f = open(tmpDir + "/class_compare.html","w");f.write(templ_text);f.close()

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
    fileInServer = tmpDir + "/" + fieldName
    srvfile = open(fileInServer, mode = 'w')
    fileString = fs[fieldName].value
    srvfile.write(fileString)
    srvfile.close()
    os.chmod(fileInServer, 0666)
    if not fieldName == "survival_time":  ### zzz ???
        if os.path.getsize(fileInServer) == 0:
            err_msg = "<p> The "+ fieldName + " file you entered is empty </p>"
            err_msg = err_msg + "<p> Please enter a file with something in it.</p>"
            cgi_error_page("INPUT ERROR", err_msg)
            sys.exit()


def valueNumUpload(fieldName, testNumber = 'float', minValue = 0):
    """Upload and get the values and do some checking. For text and radio selections
    with positive numeric data.
    We assume there is an existing call to fs = cgi.FieldStorage()"""

    if not fs.has_key(fieldName):
        shutil.rmtree(tmpDir)
        err_msg = "<p> The "+ fieldName + " field is empty. </p>"
        err_msg = err_msg + "<p> Please fill up the required fields and try again.</p>"
        cgi_error_page("INPUT ERROR", err_msg)
        sys.exit()
    if fs[fieldName].filename:
        shutil.rmtree(tmpDir)
        err_msg = "<p> The "+ fieldName + " field should not contain a file. </p>"
        err_msg = err_msg + "<p> Please fill up the required fields and try again.</p>"
        cgi_error_page("INPUT ERROR", err_msg)
        sys.exit()
    if type(fs[fieldName]) == type([]):
        shutil.rmtree(tmpDir)
        err_msg = "<p> The "+ fieldName + " should be a single value.</p>"
        err_msg = err_msg + "<p> Please fill up the required fields and try again.</p>"
        cgi_error_page("INPUT ERROR", err_msg)
        sys.exit()
    else:
        tmp = fs[fieldName].value

    ## Accept only numeric values that can be turned to floats or ints
    if testNumber == 'float':
        try:
            tmpn = float(tmp)
        except:
            err_msg = "<p> The "+ fieldName + " is not a valid numeric value.</p>"
            err_msg = err_msg + "<p> Please enter a file with something in it.</p>"
            cgi_error_page("INPUT ERROR", err_msg)
            sys.exit()
    else:
        try:
            tmpn = int(tmp)
        except:
            err_msg = "<p> The "+ fieldName + " is not a valid numeric value.</p>"
            err_msg = err_msg + "<p> Please enter a file with something in it.</p>"
            cgi_error_page("INPUT ERROR", err_msg)
            sys.exit()

    if tmpn < minValue:
        shutil.rmtree(tmpDir)
        err_msg = "<p> Value of " + fieldName + " is smaller than smallest accepted value (" + str(minValue) +  ").</p>"
        err_msg = err_msg + "<p>  Please fill up the required fields and try again.</p>"
        cgi_error_page("INPUT ERROR", err_msg)
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
        err_msg = "<p> The "+ fieldName + " field is empty. </p>"
        err_msg = err_msg + "<p> Please fill up the required fields and try again.</p>"
        cgi_error_page("INPUT ERROR", err_msg)
        sys.exit()
    if fs[fieldName].filename:
        shutil.rmtree(tmpDir)
        err_msg = "<p> The "+ fieldName + " field should not contain a file. </p>"
        err_msg = err_msg + "<p> Please fill up the required fields and try again.</p>"
        cgi_error_page("INPUT ERROR", err_msg)
        sys.exit()
    if type(fs[fieldName]) == type([]):
        shutil.rmtree(tmpDir)
        err_msg = "<p> The "+ fieldName + " should be a single value.</p>"
        err_msg = err_msg + "<p> Please fill up the required fields and try again.</p>"
        cgi_error_page("INPUT ERROR", err_msg)
        sys.exit()
    else:
        tmp = fs[fieldName].value
            
    if tmp not in acceptedValues:
        shutil.rmtree(tmpDir)
        err_msg = "<p> Chosen value for " + fieldName + " is not valid. </p>"
        err_msg = err_msg + "<p> Your value:" + tmp + ". Accepted values are:" + str(acceptedValues) + "</p>"
        err_msg = err_msg + "<p> Please fill up the required fields and try again.</p>"
        cgi_error_page("INPUT ERROR", err_msg)
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

if test_type in permutation_tests:
    num_permut = valueNumUpload('num_permut', 'int' , 1000)
else:
    num_permut = 200000

if test_type == 't_limma_paired':
    fileUpload('paired_indicator')
    if os.stat(tmpDir + '/paired_indicator')[ST_SIZE] > MAX_time_size:
        shutil.rmtree(tmpDir)
        err_msg = "<p> Paired indicator file way too large. </p>"
        err_msg = err_msg + "<p> Paired indicator files this size are not allowed.</p>"
        cgi_error_page("INPUT ERROR", err_msg)
        sys.exit()
    
## zz: I think this won't work. Needs to check:
## if Cox: the three files; o.w. two files.


##check if file coming from preP

if(fs.getfirst("covariate2")!= None):
    prep_tmpdir = fs.getfirst("covariate2")
    shutil.copy("/http/prep/www/tmp/" + prep_tmpdir +"/outdata.txt",tmpDir + "/covariate")
# Selenium if *********
elif(fs.has_key("selenium_indicator")):
    shutil.copy(covariate_sel_file,tmpDir + "/covariate")
    os.system("touch " + tmpDir + "/SELENIUM_TEST")
else:
    ## Uploading files and checking not abusively large
    fileUpload('covariate')
    if os.stat(tmpDir + '/covariate')[ST_SIZE] > MAX_covariate_size:
        shutil.rmtree(tmpDir)
        err_msg = "<p> Gene expression file way too large. </p>"
        err_msg = err_msg + "<p> Gene expression files this size are not allowed.</p>"
        cgi_error_page("INPUT ERROR", err_msg)
        sys.exit()


fileUpload('survival_time')
if os.stat(tmpDir + '/survival_time')[ST_SIZE] > MAX_time_size:
    shutil.rmtree(tmpDir)
    err_msg = "<p> Censored indicator file way too large. </p>"
    err_msg = err_msg + "<p> Censored indicator files this size are not allowed.</p>"
    cgi_error_page("INPUT ERROR", err_msg)
    sys.exit()

# Selenium if *********
if(fs.has_key("selenium_indicator")):
    shutil.copy(class_lab_sel_file,tmpDir + "/class_labels")
else:
    fileUpload('class_labels')
    
if os.stat(tmpDir + '/class_labels')[ST_SIZE] > MAX_time_size:
    shutil.rmtree(tmpDir)
    err_msg = "<p> Class labels file way too large. </p>"
    err_msg = err_msg + "<p> Class labels files this size are not allowed.</p>"
    cgi_error_page("INPUT ERROR", err_msg)
    sys.exit()

# Aqui hay que parsear el fichero de classes para que solo haya letras y numeros.
dummy = os.system("cd " + tmpDir +"; /bin/sed 's/[^a-z^A-Z^\t^\r^0-9]/./g' class_labels > tmpcllb; mv tmpcllb class_labels;")
dummy = os.system("cd " + tmpDir +";/bin/sed 's/\.\{1,\}/\./g' class_labels > tmpcllb; mv tmpcllb class_labels;")
dummy = os.system("cd " + tmpDir +";/bin/sed 's/\.\t/\t/g' class_labels > tmpcllb; mv tmpcllb class_labels;")
dummy = os.system("cd " + tmpDir +";/bin/sed 's/\.$//g'  class_labels > tmpcllb; mv tmpcllb class_labels;") 

#sedCommand = fisrtsed + secondsed +  thirdsed + fourthsed
#dummy = os.system(sedCommand)

# # Aqui hay que parsear el fichero de classes para que solo haya letras y numeros.
# nonChar_toDot = "cd " + tmpDir +"; /bin/sed 's/[^a-z^A-Z^\t^0-9]/./g' class_labels > tmpcllab;"
# multiDot_oneDot = "/bin/sed 's/\.\{1,\}/\./g' tmpcllab > class_labels; rm tmpcllab"
# sedCommand = nonChar_toDot + multiDot_oneDot
# dummy = os.system(sedCommand)



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
    err_msg = "<p> Because of the popularity of the application "
    err_msg = err_msg + " the maximum number of simultaneous runs of Pomelo2 has been reached.</p>"
    err_msg = err_msg + "<p> Please try again later.</p>"
    err_msg = err_msg + "<p> We apologize for the inconvenience.</p>"
    cgi_error_page("SERVER BUSY", err_msg)
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
num_name_lines = 0
gene_name_list = []
for nr in range(0, len(all_covar_lines)):
    line = all_covar_lines[nr]
    if (line.find("#name") == 0) or (line.find("#NAME") == 0) or (line.find("#Name") == 0) \
           or (line.find('"#name"') == 0) or (line.find('"#NAME"') == 0) or (line.find('"#Name"') == 0):
        num_name_lines = num_name_lines + 1
        if num_name_lines > 1:
            err_msg = '<p> You have more than one line with "#Name" (or "#NAME" or "#name")," in the data matrix'
            err_msg = err_msg + 'but only one is allowed.'
            cgi_error_page("INPUT ERROR", err_msg)
            sys.exit()
        arrayfile.write(line)
        arrayfile.write("\n\n")
        arrayfile.close()
        os.chmod(arrayNames, 0660)
    elif (line.find("#", 0, 1) == 0):
    	continue
    elif (len(line) <= 2):
    	continue
    else:
        line_splitted  = line.split('\t', 1)
        gene_name_splt = line_splitted[0]
        line_splitted  = line_splitted[-1]
        gene_name_list.append(gene_name_splt)
        if line_splitted.find(',') >= 0:
            err_msg = '<p> You have "," in the data matrix.</p>'
            err_msg = err_msg + '<p> You probably are using "," instead of "." for the'
            err_msg = err_msg + ' decimal separator. Please, use a "." instead of a ",".</p>'
            cgi_error_page("INPUT ERROR", err_msg)
            covarR.close()
            sys.exit()
        else:
            if line_splitted.rstrip():
                covarR.write(line_splitted)
covarR.close()
gene_name_file = open(tmpDir + '/gene_names', mode = 'w')
string_genes   = '\t'.join(gene_name_list)
gene_name_file.write(string_genes)
gene_name_file.close()

## checking constant genes and missings is done with R zz
if test_type in testDiscrete_tests:
    os.system('cp /http/pomelo2/cgi/testDiscrete.R ' + tmpDir + '/.')
    Rcommand = "cd " + tmpDir + "; " + "/usr/bin/R CMD BATCH --no-restore --no-readline --no-save -q testDiscrete.R 2> error.msg "
    Rrun = os.system(Rcommand)
    if os.path.exists(tmpDir + '/errorInput'):    
        rif = open(tmpDir + '/errorInput', mode = 'r')
        rift = rif.read()
        err_msg = cgi.escape(rift)
        cgi_error_page("INPUT ERROR", err_msg)
        rif.close()
        sys.exit()
else:
    os.system('cp /http/pomelo2/cgi/testContinuous.R ' + tmpDir + '/.')
    Rcommand = "cd " + tmpDir + "; " + "/usr/bin/R CMD BATCH --no-restore --no-readline --no-save -q testContinuous.R 2> error.msg "
    Rrun = os.system(Rcommand)
    if os.path.exists(tmpDir + '/errorInput'):
        rif = open(tmpDir + '/errorInput', mode = 'r')
        rift = rif.read()
        
        err_msg = cgi.escape(rift)
        cgi_error_page("INPUT ERROR", err_msg)
        rif.close()
        sys.exit()
        

## It would be good to use spawnl or similar instead of system,
## but I have no luck with R. This, I keep using system.
## Its safety depends crucially on the newDir not being altered,
## but newDir is not passed from any other user-reachable place
## (it is created here).

dummy = os.system('cp /http/pomelo2/cgi/new_heatmap.R ' + tmpDir + '/.')
dummy = os.system('cp /http/pomelo2/cgi/f1.R ' + tmpDir + '/. ; chmod 777 ' + tmpDir + "/f1.R")
dummy = os.system('cp /http/pomelo2/cgi/limma_functions.R ' + tmpDir + '/. ; chmod 777 ' + tmpDir + "/limma_functions.R")
if test_type=="Anova_limma":
    dummy = os.system('cp /http/pomelo2/cgi/draw_venn.R ' + tmpDir + '/. ; chmod 777 ' + tmpDir + "/draw_venn.R")
    dummy = os.system('cp /http/pomelo2/cgi/calculate_contrasts.R ' + tmpDir + '/. ; chmod 777 ' + tmpDir + "/calculate_contrasts.R")
    create_classcomp_html()
    
##old macs issues
dummy = os.system("cd " + tmpDir +"; /bin/sed 's/\\r\\n/\\n/g' covariate > tmpc; mv tmpc covariate; /bin/sed 's/\\r/\\n/g' covariate > tmpc; mv tmpc covariate")
touchPomrunning = os.system("/bin/touch /http/pomelo2/www/Pom.running.procs/Pom." + newDir + "@" + socket.gethostname())
dummy = os.system('ln -s /http/pomelo2/bin/multest_paral ' + tmpDir + '/multest_paral')

# If not limma tests then just launch, if limma see further on
#if test_type not in limma_covariable_tests:
if test_type != "Anova_limma":
    tryrrun = os.system('/http/mpi.log/pomelo_run.py ' + tmpDir + ' ' + test_type + ' ' + str(num_permut) +'&')
    
createResultsFile = os.system("/bin/touch " + tmpDir + "/results.txt")


###########   Creating a results.hmtl   ###############

## Copy to tmpDir a results.html that redirects to checkdone.cgi
## If communication gets broken, there is always a results.html
## that will do the right thing.
shutil.copy("/http/pomelo2/www/Pomelo2_html_templates/results-pre.html", tmpDir)
os.system("cd " + tmpDir + "; /bin/sed 's/sustituyeme/" +
          newDir + "/g' results-pre.html > results.html; rm results-pre.html")

#if test_type not in limma_covariable_tests:
if test_type != "Anova_limma":
    ##############    Redirect to checkdone.cgi    ##################
    print "Location: "+ getQualifiedURL("/cgi-bin/pomelo_checkdone.cgi") + "?newDir=" + newDir, "\n\n"
else:
    covar_direc = tmpDir + "/COVARIABLES"
    os.mkdir(covar_direc)
    os.chmod(covar_direc, 0770)
    
    ##############    Redirect to checkdone.cgi    ##################
    print "Location: "+ getQualifiedURL("/cgi-bin/add_covariables.cgi")  + "?newDir=" + newDir, "\n\n"
