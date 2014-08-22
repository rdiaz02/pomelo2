######## CHANGE THE FOLLOWING FOR YOUR SETUP
ROOT_POMELO_DIR = "/home2/ramon/web-apps/pomelo2/"
R_pomelo_bin = '/home2/ramon/web-apps/R-3.1.1-patched-2014-08-21/bin/R'
num_procs = 63 ## For mpi
web_apps_common_dir = '/home2/ramon/web-apps/web-apps-common/'


## next unlikely to require changing, unless you want, of course
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

ROOT_TMP_DIR = ROOT_POMELO_DIR + "www/tmp/"
runningProcs = ROOT_POMELO_DIR + "www/Pom.running.procs/"
cgi_dir      = ROOT_POMELO_DIR + "cgi/"



pomelo_templates_dir = ROOT_POMELO_DIR + "www/Pomelo2_html_templates/"
pomelo_running_procs_dir = ROOT_POMELO_DIR + "www/Pom.running.procs/"
pomelo_running_procs_file_expression = pomelo_running_procs_dir + "Pom.*@*"

buryPomCall = cgi_dir + "buryPom.py"
