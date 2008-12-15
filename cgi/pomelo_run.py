#!/usr/bin/python

### This file should be linked from /http/mpi.log, and that is
### where the call comes from

import os
import time
import signal
import shutil
import sys
import random
import socket

sys.path.append('/http/mpi.log')
import counterApplications

tmpDir     = sys.argv[1]
test_type  = sys.argv[2]
num_permut = sys.argv[3]
limma_tests = ("t_limma", "t_limma_paired", "Anova_limma")

R_pomelo_dir = '/http/R-pomelo2'

def collectZombies(k = 10):
    """ Make sure there are no zombies in the process tables.
    This is probably an overkill, but works.
    """
    for nk in range(k):
        try:
            tmp = os.waitpid(-1, os.WNOHANG)
        except:
            None

os.system("cd " + tmpDir + "; /http/mpi.log/buryPom.py")

lamSuffix = str(os.getpid()) + str(random.randint(1, 999999))
killedlamandr = os.system('/http/mpi.log/killOldLam.py')
try:
    counterApplications.add_to_log('PomeloII', tmpDir, socket.gethostname())
except:
    None

if test_type in limma_tests:
    R_launch = R_pomelo_dir + "/bin/R CMD BATCH --no-restore --no-readline --no-save -q limma_functions.R"
    fullPomelocommand = "cd " + tmpDir + "; " + R_launch
elif test_type!="Cox":
    Pomelo_launch = "mpiexec multest_paral " + test_type + " maxT " + num_permut + " covariate class_labels "
    fullPomelocommand = 'export LAM_MPI_SESSION_SUFFIX="' + lamSuffix + '";' + '/usr/bin/lamboot -H /http/mpi.defs/lamb-host.' + socket.gethostname() + '.def; cd ' + tmpDir + '; ' + Pomelo_launch + " > pomelo.msg"
    lamenvfile = open(tmpDir + '/lamSuffix', mode = 'w')
    lamenvfile.write(lamSuffix)
    lamenvfile.close()
else : 
    fullPomelocommand = 'cd ' + tmpDir + '; ' + '/http/mpi.log/tryRpomelorun.py ' + tmpDir +' 10 ' + 'PomeloII_cox'



Pom_run = os.system(fullPomelocommand)
dummy   = os.system('cd ' + tmpDir + '; ' + 'touch pomelo_run.finished')

collectZombies()


