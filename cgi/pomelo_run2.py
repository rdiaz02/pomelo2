#!/usr/bin/python


####  Copyright (C)  2003-2005, 2014, Ramon Diaz-Uriarte <rdiaz02@gmail.com>,
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


###  This is not as full proof as the mechanisms in ADaCGH: if there is a crash
###  during the execution, there is no recovery or re-start.

###  FIXME: maybe via pomelo_checkdone.cgi: do a few loops

## apparently not used
# import fcntl
# import glob
# import signal

import os
import time
import shutil
import sys
import random
import socket
import cgitb; cgitb.enable() ## can comment out once debugged?
sys.stderr = sys.stdout

## from pomelo_config import *  # noqa
## sys.path.append(web_apps_common_dir)
sys.path.append("../../web-apps-common")
from web_apps_config import *
import counterApplications


tmpDir     = sys.argv[1]
test_type  = sys.argv[2]
num_permut = sys.argv[3]

newDir = tmpDir.replace(ROOT_POMELO_TMP_DIR, "")
newDir = newDir.replace("/", "")  ## just the number


limma_tests = ("t_limma", "t_limma_paired", "Anova_limma")

## NCPU = 4


### These commands are NOT launched in the background!!!
def CoxCommand(tmpDir, R_pomelo_bin):
    # run_command = 'export LAM_MPI_SESSION_SUFFIX="' + lamSuffix + '"; cd ' + \
    #               tmpDir +  '; ' + R_pomelo_bin + \
    #               ' --no-restore --no-readline --no-save --slave <f1-pomelo.R >>f1-pomelo.Rout 2> error.msg '
    run_command = 'cd ' + \
                  tmpDir +  '; ' + R_pomelo_bin + \
                  ' --no-restore --no-readline --no-save --slave <f1-pomelo.R >>f1-pomelo.Rout 2> error.msg '
    issue_echo('    inside CoxCommand: ready for os.system', tmpDir)
    os.system(run_command)
    issue_echo('    inside CoxCommand: done os.system', tmpDir)

    
def multestCommand(tmpDir, num_permut, test_type):
    issue_echo('    inside multestCommand: before creating command', tmpDir)
    run_command = 'cd ' +  tmpDir + '; ' + mpirun_command + "    multest_paral " +\
                  test_type +  " maxT " + num_permut + \
                  " covariate class_labels " + " > pomelo.msg"
    issue_echo('           command to run is ' + run_command, tmpDir)
    issue_echo('    inside multestCommand: ready for os.system', tmpDir)
    fi,foe = os.popen4(run_command)
    fi.close()
    outcommand = foe.read()
    if (outcommand.find('bad_alloc') > (-1)): 
        dummy   = os.system('cd ' + tmpDir + '; ' + 'touch MemoryERROR')
        issue_echo(' MEMORY ERROR (from inside multestCommand)', tmpDir)
    elif (outcommand.find('exit status 9') > (-1)): ## I think this are ALWAYS memory
        ## errors, but I am not sure. The C++ coudl should be changed
        ## to have checks in each new, and return a custom exit status number. FIXME
        dummy   = os.system('cd ' + tmpDir + '; ' + 'touch MemoryERROR')
        issue_echo(' MEMORY ERROR (from inside multestCommand)', tmpDir)
    issue_echo('    inside multestCommand: done os.system', tmpDir)

    

def collectZombies(k = 10):
    """ Make sure there are no zombies in the process tables.
    This is probably an overkill, but works.
    """
    issue_echo(" .... inside collectZombies", tmpDir)
    for nk in range(k):
        try:
            tmp = os.waitpid(-1, os.WNOHANG)
        except:
            None

## leave this, since this could happen with OpenMPI
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
    outf.write("<p> After " + str(numtries) + " attempts we have been unable to ")
    outf.write(" initialize MPI.</p>")
    outf.write("<p> We will be notified of this error, but we would also ")
    outf.write("appreciate if you can let us know of any circumstances or problems ")
    outf.write("so we can diagnose the error.</p>")
    outf.write("</body></html>")
    outf.close()
    shutil.copyfile(tmpDir + "/pre-results.html", tmpDir + "/results.html")


def writeMemoryErrorMessage(tmpDir):
    out1 = open(tmpDir + "/natural.death.pid.txt", mode = "w")
    out2 = open(tmpDir + "/kill.pid.txt", mode = "w")
    out1.write('MEMORY ERROR!!')
    out2.write('MEMORY ERROR!!')
    out1.close()
    out2.close()
    outf = open(tmpDir + "/pre-results.html", mode = "w")
    outf.write("<html><head><title> Out of memory problem.</title></head><body>\n")
    outf.write("<h1> Out of memory problems.</h1>")
    outf.write("<p> Your data are too large for the current load and memory")
    outf.write("available in our servers. We are getting out of memory problems.")
    outf.write("Try merging replicates and/or reducing number of permutations.")
    outf.write("<p> We will be notified of this problem, but we would also ")
    outf.write("appreciate if you can let us know of the specific circumstances.")
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
             Pomelo_runningProcs= Pomelo_runningProcs,
             newnamepid = 'finished_pid.txt'):
    """ Clean up actions; kill lam, delete running.procs files, clean process table."""
##    lamenv = open(tmpDir + "/lamSuffix", mode = "r").readline()
    try:
        rinfo = open(tmpDir + '/current_R_proc_info', mode = 'r').readline().split()
    except:
        None
    try:
        kill_pid_machine(rinfo[1], rinfo[0])
    except:
        None
    # try:
    #     os.system('export LAM_MPI_SESSION_SUFFIX=' + lamenv +
    #               '; lamhalt -H; lamwipe -H')
    # except:
    #     None
    try:
        fii = os.popen3('rm ' + Pomelo_runningProcs + '/Pom.' + newDir + '*')
    except:
        None
    try:
        os.rename(tmpDir + '/pid.txt', tmpDir + '/' + newnamepid)
    except:
        None
    # try:
    #     os.remove(''.join([Pomelo_runningProcs, '/sentinel.lam.', newDir, '.', lamSuffix]))
    # except:
    #     None


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



def mpi_crash_log(tmpDir, value):
    """ Write to the lam crash log, 'recoverFromMPICrash.out' """
    timeHuman = str(time.strftime('%d %b %Y %H:%M:%S')) 
    os.system('echo "' + value + '  at ' + timeHuman + \
              '" >> ' + tmpDir + '/recoverFromMPICrash.out')



###################################################################
###################################################################

issue_echo('pomelo_run2.py pid = '+ str(os.getpid()), tmpDir)

## killedlamandr = os.system('/http/mpi.log/killOldLam.py')

# os.system("cd " + tmpDir + "; touch about_to_call_buryPom")
# os.system("cd " + tmpDir + "; /http/mpi.log/buryPom.py; touch just_called_buryPom")


try:
    counterApplications.add_to_counter_log('PomeloII-' + test_type,
                                           tmpDir, socket.gethostname())
except:
    None


count_mpi_crash = 0

if test_type in limma_tests:
    R_launch = R_pomelo_bin + " CMD BATCH --no-restore --no-readline --no-save -q limma_functions.R"
    fullPomelocommand = "cd " + tmpDir + "; " + R_launch
    issue_echo(' about to do fullPomelocommand', tmpDir)
    os.system(fullPomelocommand)
    issue_echo(' just did fullPomelocommand', tmpDir)
else: ## we use MPI
    startedOK = False
    issue_echo('starting else loop', tmpDir)
    checkpoint = os.system("echo 0 > " + tmpDir + "/checkpoint.num")
    ## lamSuffix = generate_lam_suffix(tmpDir)
    ## We do not check for room here. Maybe later? FIXME
    issue_echo('before lamboot', tmpDir)
    while True:
# #     for i in range(int(MAX_MPI_CRASHES)):
#         lamboot(lamSuffix, NCPU) ## note that this tries a number of times!
# ## checkTping ain't working. And I don't get it. FIXME!!
# #        time.sleep(20) ## wait for LAM to be set
# #        lam_ok = check_tping(lamSuffix, tmpDir)
# #         if lam_ok == 0:
# #             issue_echo('check_tping fails', tmpDir)
# #             lboot = lamboot(lamSuffix, NCPU)
        issue_echo('after lamboot', tmpDir)
        # counterApplications.add_to_LAM_SUFFIX_LOG('PomeloII-' + test_type,
        #                                           tmpDir,
        #                                           socket.gethostname())
        issue_echo('after counter applications', tmpDir)

        ## launch actual R or multtest process
        if(test_type == "Cox"):
            issue_echo(' about to launch CoxCommand', tmpDir)
            CoxCommand(tmpDir, R_pomelo_bin)
        else:
            issue_echo(' about to launch multestCommand', tmpDir)
            multestCommand(tmpDir, num_permut, test_type)

        time.sleep(TIME_BETWEEN_CHECKS + random.uniform(0.1, 3))
        collectZombies()

        if os.path.exists(tmpDir + "/MemoryERROR"):
            issue_echo(' MEMORY ERROR ', tmpDir)
            counterApplications.add_to_MPIErrorLog('PomeloII-' + test_type,
                                                   tmpDir, socket.gethostname(),
                                                   message = 'MPI MEMORY ERROR')
            mpi_crash_log(tmpDir, "MPI MEMORY ERROR")
            cleanups(tmpDir, newDir)
            writeErrorMessage(tmpDir)
            break
            
        
        if os.path.exists(tmpDir + "/RterminatedOK"):
            issue_echo('   startedOK : RterminatedOK exists', tmpDir)
            startedOK = True
            break
        if os.path.exists(tmpDir + "/mpiOK"):
            issue_echo('   startedOK : mpiOK exists', tmpDir)
            startedOK = True
            break

        ## If we get here, MPI did not work
        count_mpi_crash += 1
        issue_echo('   MPI did not work', tmpDir)
        issue_echo('      count_mpi_crash = ' + str(count_mpi_crash), tmpDir)
        counterApplications.add_to_MPIErrorLog('PomeloII-' + test_type,
                                               tmpDir, socket.gethostname(),
                                               message = 'MPI crash')
        issue_echo('   called add_to_MPIErrorLog', tmpDir)

        if count_mpi_crash > MAX_MPI_CRASHES:
            issue_echo('count_mpi_crash > MAX_MPI_CRASHES', tmpDir)
            lam_crash_log(tmpDir, "MAX_MPI_CRASHES reached")
            cleanups(tmpDir, newDir)
            writeErrorMessage(tmpDir)
            break
        else:
            issue_echo('count_mpi_crash < MAX_MPI_CRASHES', tmpDir)
            ## del_mpi_logs(tmpDir, socket.gethostname())
            mpi_crash_log(tmpDir, 'Crashed')
            try:
                fuoo = os.popen3('mv ' + tmpDir + '/mpiOK ' + tmpDir + '/previous_mpiOK')
            except:
                None
            cleanups(tmpDir, newDir)
            issue_echo('mpi crashed; looping again', tmpDir)

## Recall the process (R or multtest) are blocking! We wait for them to finish or crash.

issue_echo('before touch pomelo_run_finished', tmpDir)

## why the next line!!!!??? FIXME
dummy   = os.system('cd ' + tmpDir + '; ' + 'touch pomelo_run.finished')
issue_echo('before collectZombies', tmpDir)

collectZombies()
issue_echo('before burying', tmpDir)

burying = os.system("cd " + tmpDir + "; " + Pomelo_cgi_dir + "buryPom.py")
issue_echo('after burying', tmpDir)

# killingoldLam = os.system("cd " + tmpDir + "; /http/mpi.log/killOldLamAllMachines.py")
# issue_echo('after killing all old lam', tmpDir)

issue_echo('right before sys.exit()', tmpDir)
sys.exit()


### FIXME: delete myself; hard to do cause we are still running and
### buryPom searches for pomelo_run.py as a sign of life.
### But we can minimize start-up time for other pomelos

### Recall that pomelo_run2.py can be called several times from runAndCheck.













# def generate_lam_suffix(tmpDir):
#     """As it says. Generate and write it out"""
#     lamSuffix = str(int(time.time())) + \
#                 str(os.getpid()) + str(random.randint(10, 999999))
#     lamenvfile = open(tmpDir + '/lamSuffix', mode = 'w')
#     lamenvfile.write(lamSuffix)
#     lamenvfile.flush()
#     lamenvfile.close()
#     return lamSuffix


## FIXME: either rename to mpilaunch, or do everything with
## forking
# def lamboot(lamSuffix, ncpu, Pomelo_runningProcs = Pomelo_runningProcs):
#     'Boot a lam universe and leave a sentinel file behind'
#     issue_echo('before sentinel inside lamboot', tmpDir)
#     issue_echo('newDir is ' + newDir, tmpDir)
#     issue_echo('lamSuffix ' + lamSuffix, tmpDir)
#     issue_echo('Pomelo_runningProcs ' + Pomelo_runningProcs, tmpDir)
# # why doesn't this work? FIXME
# #     sentinel = os.open(''.join([Pomelo_runningProcs, '/sentinel.lam.', newDir, '.', lamSuffix]),
# #                        os.O_RDWR | os.O_CREAT | os.O_NDELAY)
#     issue_echo('before fullCommand inside lamboot', tmpDir)
#     fullCommand = 'export LAM_MPI_SESSION_SUFFIX="' + lamSuffix + \
#                   '"; /http/mpi.log/tryBootLAM2.py ' + lamSuffix + \
#                   ' ' + str(ncpu)
#     issue_echo('before os.system inside lamboot', tmpDir)
#     lboot = os.system(fullCommand)
#     issue_echo('after lboot ---os.system--- inside lamboot. Exiting lamboot', tmpDir)


# def check_tping(lamSuffix, tmpDir, tsleep = 15, nc = 2):
#     """ Use tping to verify LAM universe OK.
#     tsleep is how long we wait before checking output of tping.
#     Verify also using 'lamexec C hostname' """
    
#     tmp2 = os.system('export LAM_MPI_SESSION_SUFFIX="' +\
#                      lamSuffix + '"; cd ' + tmpDir + \
#                      '; tping C N -c' + str(nc) + \
#                      ' > tping.out & ')
#     time.sleep(tsleep)
#     tmp = int(os.popen('cd ' + tmpDir + \
#                        '; wc tping.out').readline().split()[0])
#     os.system('rm ' + tmpDir + '/tping.out')
#     timeHuman = '##########   ' + \
#                 str(time.strftime('%d %b %Y %H:%M:%S')) 
#     os.system('echo "' + timeHuman + \
#               '" >> ' + tmpDir + '/checkTping.out')
#     if tmp == 0:
#         os.system('echo "tping fails" >> ' + \
#                   tmpDir + '/checkTping.out')
#         return 0
#     elif tmp > 0:
#         os.system('echo "tping OK" >> ' + \
#                   tmpDir + '/checkTping.out')
#         lamexec = os.system('export LAM_MPI_SESSION_SUFFIX="' +\
#                             lamSuffix + '"; lamexec C hostname')
#         if lamexec == 0:
#             os.system('echo "lamexec OK" >> ' + \
#                       tmpDir + '/checkTping.out')
#             return 1
#         else:
#             os.system('echo "lamexec fails" >> ' + \
#                       tmpDir + '/checkTping.out')
#             return 0
#     else:
#         os.system('echo "tping weird ' + str(tmp) + '" >> ' + \
#                   tmpDir + '/checkTping.out')
#         return 0





# def lam_crash_log(tmpDir, value):
#     """ Write to the lam crash log, 'recoverFromLAMCrash.out' """
#     timeHuman = str(time.strftime('%d %b %Y %H:%M:%S')) 
#     os.system('echo "' + value + '  at ' + timeHuman + \
#               '" >> ' + tmpDir + '/recoverFromLAMCrash.out')
    
# def recover_from_lam_crash(tmpDir, NCPU, MAX_NUM_PROCS, lamSuffix,
#                            Pomelo_runningProcs= Pomelo_runningProcs,
#                            machine_root = 'karl'):
#     """Check if lam crashed during R run. If it did, restart R
#     after possibly rebooting the lam universe.
#     Leave a trace of what happened.
#     FIXME: it looks like we are not using this as such as we just loop
#     below.
#     """

    
#     os.remove(''.join([Pomelo_runningProcs, '/sentinel.lam.', newDir, '.', lamSuffix]))
#     del_mpi_logs(tmpDir, machine_root)
#     lam_crash_log(tmpDir, 'Crashed')
#     ## We need to halt the universe, or else we can keep a lamd with no R hanging from
#         ## it, but that leads to too many lamds, so it cannot start. Like a vicious circle
#     lamenv = open(tmpDir + "/lamSuffix", mode = "r").readline()
#     try:
#         os.system('export LAM_MPI_SESSION_SUFFIX=' + lamenv +
#                   '; lamhalt -H; lamwipe -H')
#     except:
#         None
#     issue_echo('inside recover_from_lam_crash: lamhalting', tmpDir)
#     try:
#         foo = os.popen3('mv ' + tmpDir + '/mpiOK ' + tmpDir + '/previous_mpiOK')
#     except:
#         None
# #     check_room = my_queue(MAX_NUM_PROCS)
# #     if check_room == 'Failed':
# #         printMPITooBusy(tmpDir, MAX_DURATION_TRY = 5 * 3600)

#     lam_ok = check_tping(lamSuffix, tmpDir)
#     if lam_ok == 0:
#         lboot = lamboot(lamSuffix, NCPU)
# #     Rrun(tmpDir, lamSuffix)
#     lam_crash_log(tmpDir, '..... recovering')


# def del_mpi_logs(tmpDir, machine_root = 'karl'):
#     """ Delete logs from LAM/MPI."""
#     lam_logs = glob.glob(tmpDir + '/' + machine_root + '*.*.*.log')
#     try:
#         fuu = os.popen3('rm ' + tmpDir + '/R_Status.txt')
#     except:
#         None
#     try:
#         for lam_log in lam_logs:
#             fuuu = os.popen3('rm ' + lam_log)    
#     except:
#         None
