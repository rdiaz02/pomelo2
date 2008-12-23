#!/usr/bin/python


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





### This file should be linked from /http/mpi.log, and that is
### where the call comes from


###  This is not as full proof as the mechanisms in ADaCGH: if there is a crash
###  during the execution, there is no recovery or re-start.

###  FIXME: maybe via pomelo_checkdone.cgi: do a few loops


import os
import time
import signal
import shutil
import sys
import random
import socket
import fcntl
import cgitb;cgitb.enable() 
sys.stderr = sys.stdout 


sys.path.append('/http/mpi.log')
import counterApplications

ROOT_TMP_DIR = "/http/pomelo2/www/tmp"
tmpDir     = sys.argv[1]
test_type  = sys.argv[2]
num_permut = sys.argv[3]
newDir = tmpDir.replace(ROOT_TMP_DIR, "")

limma_tests = ("t_limma", "t_limma_paired", "Anova_limma")

R_pomelo_dir = '/http/R-pomelo2'


runningProcs = '/http/pomelo2/www/Pom.running.procs'


NCPU = 4
MAX_MPI_CRASHES = 20
TIME_BETWEEN_CHECKS = 45


### These commands are NOT launched in the background!!!
def CoxCommand(lamSuffix, tmpDir, R_pomelo_dir):
    run_command = 'export LAM_MPI_SESSION_SUFFIX="' + lamSuffix + '"; cd ' + \
                  tmpDir +  '; ' + R_pomelo_dir + \
                  '/bin/R  --no-restore --no-readline --no-save --slave <f1-pomelo.R >>f1-pomelo.Rout 2> error.msg '
    os.system(run_command)
    
def multestCommand(lamSuffix, tmpDir, num_permut, test_type):
    run_command = 'export LAM_MPI_SESSION_SUFFIX="' + lamSuffix + '"; cd ' + \
                  tmpDir + '; ' + "mpiexec multest_paral " + test_type + \
                  " maxT " + num_permut + " covariate class_labels " + " > pomelo.msg"
    os.system(run_command)

    

def collectZombies(k = 10):
    """ Make sure there are no zombies in the process tables.
    This is probably an overkill, but works.
    """
    for nk in range(k):
        try:
            tmp = os.waitpid(-1, os.WNOHANG)
        except:
            None


def writeErrorMessage(tmpDir):
    numtries = MAX_MPI_CRASHES * 10
    out1 = open(tmpDir + "/natural.death.pid.txt", mode = "w")
    out2 = open(tmpDir + "/kill.pid.txt", mode = "w")
    out1.write('MPI initialization error!!')
    out2.write('MPI initialization error!!')
    out1.close()
    out2.close()
    outf = open(tmpDir + "/pre-results.html", mode = "w")
    outf.write("<html><head><title> MPI initialization problem.</title></head><body>\n")
    outf.write("<h1> MPI initialization problem.</h1>")
    outf.write("<p> After " + numtries + " attempts we have been unable to ")
    outf.write(" initialize MPI.</p>")
    outf.write("<p> We will be notified of this error, but we would also ")
    outf.write("appreciate if you can let us know of any circumstances or problems ")
    outf.write("so we can diagnose the error.</p>")
    outf.write("</body></html>")
    outf.close()
    shutil.copyfile(tmpDir + "/pre-results.html", tmpDir + "/results.html")


###################################################################
###################################################################

####       Most of these are the same (or similar to)
####          ones in ADaCGH-server            

###################################################################
###################################################################

def cleanups(tmpDir, newDir,
             lamSuffix,
             runningProcs= runningProcs,
             newnamepid = 'finished_pid.txt'):
    """ Clean up actions; kill lam, delete running.procs files, clean process table."""
    lamenv = open(tmpDir + "/lamSuffix", mode = "r").readline()
    try:
        rinfo = open(tmpDir + '/current_R_proc_info', mode = 'r').readline().split()
    except:
        None
    try:
        kill_pid_machine(rinfo[1], rinfo[0])
    except:
        None
    try:
        os.system('export LAM_MPI_SESSION_SUFFIX=' + lamenv +
                  '; lamhalt -H; lamwipe -H')
    except:
        None
    try:
        os.system('rm ' + runningProcs + '/Pom.' + newDir + '*')
    except:
        None
    try:
        os.rename(tmpDir + '/pid.txt', tmpDir + '/' + newnamepid)
    except:
        None
    try:
        os.remove(''.join([runningProcs, '/sentinel.lam.', newDir, '.', lamSuffix]))
    except:
        None


def issue_echo(fecho, tmpDir):
    """Silly function to output small tracking files"""
    timeHuman = '##########   ' + \
                str(time.strftime('%d %b %Y %H:%M:%S')) 
    os.system('echo "' + timeHuman + \
              '" >> ' + tmpDir + '/checkdone.echo')
    os.system('echo "' + fecho + \
              '" >> ' + tmpDir + '/checkdone.echo')
    os.system('echo "    " >> ' + tmpDir + '/checkdone.echo')


def kill_pid_machine(pid, machine):
    'as it says: to kill somehting somewhere'
    os.system('ssh ' + machine + ' "kill -s 9 ' + pid + '"')

def generate_lam_suffix(tmpDir):
    """As it says. Generate and write it out"""
    lamSuffix = str(int(time.time())) + \
                str(os.getpid()) + str(random.randint(10, 999999))
    lamenvfile = open(tmpDir + '/lamSuffix', mode = 'w')
    lamenvfile.write(lamSuffix)
    lamenvfile.flush()
    lamenvfile.close()
    return lamSuffix

def lamboot(lamSuffix, ncpu, runningProcs = runningProcs):
    'Boot a lam universe and leave a sentinel file behind'
    issue_echo('before sentinel inside lamboot', tmpDir)
    issue_echo('newDir is ' + newDir, tmpDir)
    issue_echo('lamSuffix ' + lamSuffix, tmpDir)
    issue_echo('runningProcs ' + runningProcs, tmpDir)
# why doesn't this work? FIXME
#     sentinel = os.open(''.join([runningProcs, '/sentinel.lam.', newDir, '.', lamSuffix]),
#                        os.O_RDWR | os.O_CREAT | os.O_NDELAY)
    issue_echo('before fullCommand inside lamboot', tmpDir)
    fullCommand = 'export LAM_MPI_SESSION_SUFFIX="' + lamSuffix + \
                  '"; /http/mpi.log/tryBootLAM2.py ' + lamSuffix + \
                  ' ' + str(ncpu)
    issue_echo('before os.system inside lamboot', tmpDir)
    lboot = os.system(fullCommand)
    issue_echo('after lboot ---os.system--- inside lamboot. Exiting lamboot', tmpDir)


def check_tping(lamSuffix, tmpDir, tsleep = 15, nc = 2):
    """ Use tping to verify LAM universe OK.
    tsleep is how long we wait before checking output of tping.
    Verify also using 'lamexec C hostname' """
    
    tmp2 = os.system('export LAM_MPI_SESSION_SUFFIX="' +\
                     lamSuffix + '"; cd ' + tmpDir + \
                     '; tping C N -c' + str(nc) + \
                     ' > tping.out & ')
    time.sleep(tsleep)
    tmp = int(os.popen('cd ' + tmpDir + \
                       '; wc tping.out').readline().split()[0])
    os.system('rm ' + tmpDir + '/tping.out')
    timeHuman = '##########   ' + \
                str(time.strftime('%d %b %Y %H:%M:%S')) 
    os.system('echo "' + timeHuman + \
              '" >> ' + tmpDir + '/checkTping.out')
    if tmp == 0:
        os.system('echo "tping fails" >> ' + \
                  tmpDir + '/checkTping.out')
        return 0
    elif tmp > 0:
        os.system('echo "tping OK" >> ' + \
                  tmpDir + '/checkTping.out')
        lamexec = os.system('export LAM_MPI_SESSION_SUFFIX="' +\
                            lamSuffix + '"; lamexec C hostname')
        if lamexec == 0:
            os.system('echo "lamexec OK" >> ' + \
                      tmpDir + '/checkTping.out')
            return 1
        else:
            os.system('echo "lamexec fails" >> ' + \
                      tmpDir + '/checkTping.out')
            return 0
    else:
        os.system('echo "tping weird ' + str(tmp) + '" >> ' + \
                  tmpDir + '/checkTping.out')
        return 0



def lam_crash_log(tmpDir, value):
    """ Write to the lam crash log, 'recoverFromLAMCrash.out' """
    timeHuman = str(time.strftime('%d %b %Y %H:%M:%S')) 
    os.system('echo "' + value + '  at ' + timeHuman + \
              '" >> ' + tmpDir + '/recoverFromLAMCrash.out')
    
def recover_from_lam_crash(tmpDir, NCPU, MAX_NUM_PROCS, lamSuffix,
                           runningProcs= runningProcs,
                           machine_root = 'karl'):
    """Check if lam crashed during R run. If it did, restart R
    after possibly rebooting the lam universe.
    Leave a trace of what happened."""
    
    os.remove(''.join([runningProcs, '/sentinel.lam.', newDir, '.', lamSuffix]))
    del_mpi_logs(tmpDir, machine_root)
    lam_crash_log(tmpDir, 'Crashed')
    ## We need to halt the universe, or else we can keep a lamd with no R hanging from
        ## it, but that leads to too many lamds, so it cannot start. Like a vicious circle
    lamenv = open(tmpDir + "/lamSuffix", mode = "r").readline()
    try:
        os.system('export LAM_MPI_SESSION_SUFFIX=' + lamenv +
                  '; lamhalt -H; lamwipe -H')
    except:
        None
    issue_echo('inside recover_from_lam_crash: lamhalting', tmpDir)
    try:
        os.system('mv ' + tmpDir + '/mpiOK ' + tmpDir + '/previous_mpiOK')
    except:
        None
#     check_room = my_queue(MAX_NUM_PROCS)
#     if check_room == 'Failed':
#         printMPITooBusy(tmpDir, MAX_DURATION_TRY = 5 * 3600)

    lam_ok = check_tping(lamSuffix, tmpDir)
    if lam_ok == 0:
        lboot = lamboot(lamSuffix, NCPU)
#     Rrun(tmpDir, lamSuffix)
    lam_crash_log(tmpDir, '..... recovering')


def del_mpi_logs(tmpDir, machine_root = 'karl'):
    """ Delete logs from LAM/MPI."""
    lam_logs = glob.glob(tmpDir + '/' + machine_root + '*.*.*.log')
    try:
        os.system('rm ' + tmpDir + '/R_Status.txt')
    except:
        None
    try:
        for lam_log in lam_logs:
            os.system('rm ' + lam_log)    
    except:
        None


###################################################################
###################################################################


killedlamandr = os.system('/http/mpi.log/killOldLam.py')


# os.system("cd " + tmpDir + "; touch about_to_call_buryPom")
# os.system("cd " + tmpDir + "; /http/mpi.log/buryPom.py; touch just_called_buryPom")


try:
    counterApplications.add_to_log('PomeloII-' + test_type,
                                   tmpDir, socket.gethostname())
except:
    None

if test_type in limma_tests:
    R_launch = R_pomelo_dir + "/bin/R CMD BATCH --no-restore --no-readline --no-save -q limma_functions.R"
    fullPomelocommand = "cd " + tmpDir + "; " + R_launch
    os.system(fullPomelocommand)
else: ## we use MPI
    startedOK = False
    issue_echo('starting', tmpDir)
    checkpoint = os.system("echo 0 > " + tmpDir + "/checkpoint.num")
    lamSuffix = generate_lam_suffix(tmpDir)
    ## We do not check for room here. Maybe later? FIXME
    issue_echo('before lamboot', tmpDir)
    count_mpi_crash = 0
    while True:
#     for i in range(int(MAX_MPI_CRASHES)):
        lamboot(lamSuffix, NCPU) ## note that this tries a number of times!
        lam_ok = check_tping(lamSuffix, tmpDir)
        if lam_ok == 0:
            lboot = lamboot(lamSuffix, NCPU)
        issue_echo('after lamboot', tmpDir)
        counterApplications.add_to_LAM_SUFFIX_LOG(lamSuffix,
                                                  'PomeloII-' + test_type,
                                                  tmpDir,
                                                  socket.gethostname())
        ## launch actual R or multtest process
        if(test_type == "Cox"):
            CoxCommand(lamSuffix, tmpDir, R_pomelo_dir)
        else:
            multestCommand(lamSuffix, tmpDir, num_permut, test_type)

        time.sleep(TIME_BETWEEN_CHECKS + random.uniform(0.1, 3))
        collectZombies()
        
        if os.path.exists(tmpDir + "/RterminatedOK"):
            startedOK = True
            break
        if os.path.exists(tmpDir + "/mpiOK"):
            startedOK = True
            break
            ## the following ain't needed, as lamboot() checks > MIN_LAM_NODES
#             oklamnodes = int(os.popen('export LAM_MPI_SESSION_SUFFIX="' + lamSuffix + \
#                                       '"; lamnodes | wc').readline().split()[0]) > MIN_LAM_NODES
#             if oklamnodes:
#                 os.system('echo "' +
#                           str(int(os.popen('lamnodes | wc').readline().split()[0])) +
#                           '" > ' + tmpDir + '/MIN_LAM_NODES_CHECK')  ## debug
#                 startedOK = True
#                 break


        ## If we get here, MPI did not work
        count_mpi_crash += 1
        counterApplications.add_to_MPIErrorLog('PomeloII-' + test_type,
                                               tmpDir, socket.gethostname(),
                                               message = 'MPI crash')
        if count_mpi_crash > MAX_MPI_CRASHES:
            logMPIerror(tmpDir, MAX_MPI_CRASHES)
            issue_echo('count_mpi_crash > MAX_MPI_CRASHES', tmpDir)
            cleanups(tmpDir, newDir, lamSuffix)
            writeErrorMessage(tmpDir)
            break
        else:
            del_mpi_logs(tmpDir, machine_root)
            lam_crash_log(tmpDir, 'Crashed')
            try:
                os.system('mv ' + tmpDir + '/mpiOK ' + tmpDir + '/previous_mpiOK')
            except:
                None
            cleanups(tmpDir, newDir, lamSuffix)
            issue_echo('mpi crashed; looping again', tmpDir)

## Recall the process (R or multtest) are blocking! We wait for them to finish or crash.

issue_echo('antes touch pomelo_run_finished', tmpDir)
            
dummy   = os.system('cd ' + tmpDir + '; ' + 'touch pomelo_run.finished')
issue_echo('antes collectZombies', tmpDir)

collectZombies()
issue_echo('antes burying', tmpDir)

burying = os.system("cd " + tmpDir + "; /http/mpi.log/buryPom.py")
issue_echo('despues burying', tmpDir)


### FIXME: delete myself; hard to do cause we are still running and
### buryPom searches for pomelo_run.py as a sign of life.
### But we can minimize start-up time for other pomelos

