######## CHANGE THE FOLLOWING FOR YOUR SETUP
ROOT_APPS_DIR = "/web-apps"
R_pomelo_bin = ROOT_APPS_DIR + '/R-3.1.1-patched-2014-08-21/bin/R'
w3mPath = '/usr/bin/w3m'



ROOT_POMELO_DIR = ROOT_APPS_DIR + "/pomelo2"
web_apps_common_dir = ROOT_APPS_DIR + '/web-apps-common'

## next unlikely to require changing, unless you want, of course
num_procs = 63 ## For mpi
MAX_MPI_CRASHES = 2 ## note we loop also in runAndCheck.py
Pomelo_MAX_time = 3 * 3600 ## 3 hours is max duration allowd for any process
MAX_NUM_RELAUNCHES = 5 
TIME_BETWEEN_CHECKS = 10


MAX_poms = 10 ## Max number of pomelo2 running
MAX_time = 3600 * 24 * 5 ## 5 is days until deletion of a tmp directory
MAX_covariate_size = 363948523L ## a 500 * 40000 array of floats
MAX_time_size = 61897L ## time to survival, class, etc size
MAX_PERMUT = 90000000  ## maximum number of permutations


##########################################################
##########################################################

ROOT_TMP_DIR = ROOT_POMELO_DIR + "/www/tmp"
runningProcs = ROOT_POMELO_DIR + "/www/Pom.running.procs"
cgi_dir      = ROOT_POMELO_DIR + "/cgi"


pomelo_templates_dir = ROOT_POMELO_DIR + "/www/Pomelo2_html_templates"
pomelo_running_procs_dir = ROOT_POMELO_DIR + "/www/Pom.running.procs"
pomelo_running_procs_file_expression = pomelo_running_procs_dir + "/Pom.*@*"

buryPomCall = cgi_dir + "/buryPom.py"
