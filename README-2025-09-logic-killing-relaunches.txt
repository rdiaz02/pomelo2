I was having problems because buryPom was deleting Pom.running.procs files when it should not. The logic there was wrong for the new setting.

So buryPom now does nothing: the call to fcheck is commented.

What I want instead is to rm the sentinel files when there is no longer any process running. And prevent things running for long. So what I do now is, right before attemtping to launch, in pomeloII.cgi, (look for  zz-new-checks-runs 2025-09)

1. Check if, after four hours (i.e., Pomelo_MAX_time, in seconds, in web_apps_config.py):

- there are still running multest_parla
- there are still running R processes

I kill those.

2. And I check for any Pom.running.procs/Pom.[number]@whaterve older than 4 hours, and remove it.


I also used to allow several attempts at launching MPI. This is not needed anymore, I think. And that breaks the logic above, because runAndCheck.py could relaunch an mpi_run. So I set MAX_NUM_RELAUNCHES = 0 in web_apps_config.py


The runAndCheck.py are left running, so they can return the error page clearly.

The relevant changes are all locatable searching for ## zz-new-checks-runs 2025-09

But this is already being done in lines 507 and ff of pomeloII.cgi!
And that seems to remove the directory too? That is not what I want!!
Commented.

And there is some redundancy: in runAndCheck.py we have the "printPomKilled". Whatever.


And where is the cleaning up of files?
Most of the apps have a logic like (in slightly different incantations)

## Deleting tmp directories older than MAX_time
currentTime = time.time()
currentTmp = dircache.listdir(ROOT_POMELO_TMP_DIR)
for directory in currentTmp:
    tmpS = ROOT_POMELO_TMP_DIR + "/" + directory
    if (currentTime - os.path.getmtime(tmpS)) > MAX_time:
        try:
            shutil.rmtree(tmpS)
        except:
            None
