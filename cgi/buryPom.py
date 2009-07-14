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




### There should be a link to this file in /http/mpi.log

### There are better mechanisms, like in ADaCGH, and having each run
### clean up after itself... But complicated with Pomelo II

### Note that this is conservative: we look over the process
### table in each node, and if there is any pomelo-related
### process in a node, none of the Pom.running.procs indicators
### of that node is deleted.


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

theDir = ('/http/pomelo2/www/Pom.running.procs')


MachineIP = {
    'karl01'  :  '192.168.7.1',
    'karl02'  :  '192.168.7.2',
    'karl03'  :  '192.168.7.3',
    'karl04'  :  '192.168.7.4',
    'karl05'  :  '192.168.7.5',
    'karl06'  :  '192.168.7.6',
    'karl07'  :  '192.168.7.7',
    'karl08'  :  '192.168.7.8',
    'karl09'  :  '192.168.7.9',
    'karl10'  :  '192.168.7.10',
    'karl11'  :  '192.168.7.11',
    'karl12'  :  '192.168.7.12',
    'karl13'  :  '192.168.7.13',
    'karl14'  :  '192.168.7.14',
    'karl15'  :  '192.168.7.15',
    'karl16'  :  '192.168.7.16',
    'karl17'  :  '192.168.7.17',
    'karl18'  :  '192.168.7.18',
    'karl19'  :  '192.168.7.19',
    'karl20'  :  '192.168.7.20',
    'karl21'  :  '192.168.7.21',
    'karl22'  :  '192.168.7.22',
    'karl23'  :  '192.168.7.23',
    'karl24'  :  '192.168.7.24',
    'karl25'  :  '192.168.7.25',
    'karl26'  :  '192.168.7.26',
    'karl27'  :  '192.168.7.27',
    'karl28'  :  '192.168.7.28',
    'karl29'  :  '192.168.7.29',
    'karl30'  :  '192.168.7.30',
    'karl31'  :  '192.168.7.31',
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
			'mpirun.lam multest_paral',
                        'mpiexec multest_paral',
                        'R-pomelo2',
                        'testContinuous.R',
                        'testDiscrete.R',
                        'testInputCommon.R',
                        'test_and_summary.R',
                        'Pals_gene_filter.R',
                        'f1-pomelo.R',
                        'pomelo_run.py',
                        'tryRpomelorun.py',
                        'contrast_generate_table.py',
                        'generate_table_Cox.py',
                        'generate_table.py',
                        'heatmap_draw_script.py',
                        'img_map.py',
                        'parse_contrs_comp.py',
                        'pomeloII.cgi'
                        )


def fcheck():
    rrunsFiles = glob.glob(theDir + '/Pom.*@*')
    for dirMachine in rrunsFiles:
        Machine = dirMachine.split('@')[1]
        procs0 = os.popen("ssh " + MachineIP[Machine] + \
                         " 'ps -F -U www-data'")
        procs = procs0.readlines()
        procs0.close()
        alive = False
        for line in procs:
            for the_sign in signs_of_pomelo_life:
                alive = line.find(the_sign) >= 0
                if alive:
#                     os.system("touch buryPom.is.alive.sign." + the_sign + "IP." + MachineIP[Machine])
                    break
            if alive:
                break
        if not alive: ## if not Pomelo-associated activity with this machine
#             os.system("touch buryPom.REMOVE.sign." + the_sign + "IP." + MachineIP[Machine])
            try:
                os.remove(dirMachine)
            except:
                None

# os.system("touch buryPom_entering")
fcheck()
# os.system("touch buryPom_exiting")


