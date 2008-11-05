#!/usr/bin/python

##  BEWARE!!! THIS FILE MUST LIVE IN /http/mpi.log


## Based on bury them, but for Pomelo, which has the complications
## of being able to launch different types of jobs and uses somewhat
## different names. Will unify later.


## The logic here is a little bit different from buryThem.py; we only want
## to get rid of unjustified Pom.whatever that prevent Pomelo II from launching
## more runs because it incorrectly thinks there are many processes running.

import shutil
import os
import time
import glob
import sys

theDir = ('/http/pomelo2/www/Pom.running.procs')


MachineIP = {
    'prot01'  :  '192.168.2.1',
    'prot02'  :  '192.168.2.2',
    'prot03'  :  '192.168.2.3',
    'prot04'  :  '192.168.2.4',
    'prot05'  :  '192.168.2.5',
    'prot06'  :  '192.168.2.6',
    'prot07'  :  '192.168.2.7',
    'prot08'  :  '192.168.2.8',
    'prot09'  :  '192.168.2.9',
    'prot10'  :  '192.168.2.10',
    'prot11'  :  '192.168.2.11',
    'prot12'  :  '192.168.2.12',
    'prot13'  :  '192.168.2.13',
    'prot14'  :  '192.168.2.14',
    'prot15'  :  '192.168.2.15',
    'prot16'  :  '192.168.2.16',
    'prot17'  :  '192.168.2.17',
    'prot18'  :  '192.168.2.18',
    'prot19'  :  '192.168.2.19',
    'prot20'  :  '192.168.2.20',
    'prot21'  :  '192.168.2.21',
    'prot22'  :  '192.168.2.22',
    'prot23'  :  '192.168.2.23',
    'prot24'  :  '192.168.2.24',
    'prot25'  :  '192.168.2.25',
    'prot26'  :  '192.168.2.26',
    'prot27'  :  '192.168.2.27',
    'prot28'  :  '192.168.2.28',
    'prot29'  :  '192.168.2.29',
    'prot30'  :  '192.168.2.30'
    }



# def R_done(tmpDir):
#     """Verify if Rout exists. If it does, see if done"""
# ##    rfile = 1
#     try: 
# 	Rrout = open(tmpDir + "/f1.Rout")
#     except:
# 	return 1
#     if os.path.exists(tmpDir + '/RterminatedOK'):
#         return 1
# ##    if rfile:
#     soFar = Rrout.read()
#     Rrout.close()
#     finishedOK = soFar.endswith("Normal termination\n")
#     errorRun = soFar.endswith("Execution halted\n")
#     if finishedOK or errorRun:
#         return 1
#     else:
#         return 0


## As it says: any pomelo II process living here as master?"""
signs_of_pomelo_life = ('PomeloII_Cox', 'limma_functions.R',
                        'draw_venn.R', 'calculate_contrasts.R',
                        'heatimage.R', 'new_heatmap.R',
                        'mpiexec multest_paral')

## Maybe not looking hard enough?? FIXME
## what about f1.R?
## and the t-tests?
## and the permutation tests?

## and, I think, it deletes the very pom.running of itself,
## since not enough time to start the run  FIXME!!!!
    
def fcheck():
    rrunsFiles = glob.glob(theDir + '/Pom.*@*')
    for dirMachine in rrunsFiles:
        print 'dirMachine ' + str(dirMachine)
        Machine = dirMachine.split('@')[1]
        procs = os.popen("ssh " + MachineIP[Machine] + \
                         " 'ps -F -U www-data'").readlines()

        alive = False
        for line in procs:
            if alive:
                break
            for the_sign in signs_of_pomelo_life:
                alive = line.find(the_sign) >= 0
                print 'alive ' + str(alive) + '  with sign ' + the_sign
                if alive:
                    print 'the sign ' + the_sign
                    break
        if not alive:
            print 'not alive'
            try:
                os.remove(dirMachine)
            except:
                None

##  FIXME: we'll have to incorporate the following, since its very nice extra
                    ## info


                    
#                 ## were we done legitimately?
#                 tmpDir = theDir.split('R.')[0] + 'tmp/' + t1[0].split('R.')[2]
# 		## recall natural.death.pid and killed.pid only created after every 30" check.
# 		## But python or the shell can take a while to complete several operations
# 		## 
# 		legitimate = os.path.exists(tmpDir + "/natural.death.pid.txt") or os.path.exists(tmpDir + "/killed.pid.txt") or R_done(tmpDir)
                
#                 if not legitimate:
# 		## write the results file
#                     out1 = open(tmpDir + "/natural.death.pid.txt", mode = "w")
#                     out2 = open(tmpDir + "/kill.pid.txt", mode = "w")
#                     out1.write('Process died without saying goodbye!!')
#                     out2.write('Process died without saying goodbye!!')
#                     out1.close()
#                     out2.close()
#                     outf = open(tmpDir + "/pre-results.html", mode = "w")
#                     outf.write("<html><head><title> Some undiagnosed problem</title></head><body>\n")
#                     outf.write("<h1> Some undiagnosed problem happened</h1>")
#                     outf.write(" <p> Your process died unexpectedly, without giving")
#                     outf.write(" any advanced notice or leaving much trace. ")
#                     outf.write(" The error is being logged, but we would also ")
#                     outf.write("appreciate if you can let us know of any circumstances or problems ")
#                     outf.write("so we can diagnose the error.</p>")
#                     outf.write("</body></html>")
#                     outf.close()
#                     shutil.copyfile(tmpDir + "/pre-results.html", tmpDir + "/results.html")

fcheck()


# while True:
#     fcheck()
