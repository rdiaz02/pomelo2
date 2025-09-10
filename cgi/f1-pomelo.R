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

rm(list = ls())

##.Last <- function() {cat("\n\n Normal termination\n")}

## From: http://ace.acadiau.ca/math/ACMMaC/Rmpi/sample.html
# In case R exits unexpectedly, have it automatically clean up 
# resources  taken up by Rmpi (slaves, memory, etc...)
## But does it really do it??
.Last <- function(){
    RterminatedOK <- file("RterminatedOK", "w")
    cat("\nNormal termination\n", file = RterminatedOK)
    flush(RterminatedOK)
    close(RterminatedOK)

    try(sink()) ## in case we are bailing out from within sink
    save.image()
    ## if (is.loaded("mpi_initialize")){ 
    ##     if (mpi.comm.size(1) > 0){ 
    ##     try(print("Please use mpi.close.Rslaves() to close slaves."), silent = TRUE)
    ##     try(mpi.close.Rslaves() , silent = TRUE)
    ##     } 
    ##     try(print("Please use mpi.quit() to quit R"), silent = TRUE)
    ##     cat("\n\n Normal termination\n")
    ##     try(stopCluster(TheCluster), silent = TRUE)
    ##     ##        .Call("mpi_finalize")
    ##     try(mpi.quit(save = "no"), silent = TRUE)
    ## }
    ## try(stopCluster(TheCluster), silent = TRUE)
    cat("\n\n Normal termination\n")
    ## In case the CGI is not called (user kills browser)
    ## have a way to stop lam
##    try(system(paste("/http/mpi.log/killLAM.py", lamSESSION, "&")))
##    try(mpi.quit(save = "no"), silent = TRUE)
}

numcores <- 3 ## I can no longer afford these many

caughtUserError <- function(message) {
    sink(file = "pomelo.msg")
#  sink(file = "errorInput")
  cat(message)
    sink()
    quit(save = "no", status = 11, runLast = TRUE)
}


library(parallel)
library(survival)
## library(Rmpi)
## library(papply)

## mpi.spawn.Rslaves(nslaves = mpi.universe.size())
## mpi.remote.exec(rm(list = ls(env = .GlobalEnv), envir =.GlobalEnv))
## mpi.remote.exec(library(survival))

## this is not really necessary, but checking for the mpiOK file
## is in lots of places.
sink(file = "mpiOK")
cat("Dummy file so as to not trigger an mpi error message\n")
## cat("MPI started OK\n")
sink()


hostn <- system("hostname", intern = TRUE)
pid <- Sys.getpid()
sink(file = "current_R_proc_info")
cat(hostn)
cat("  ")
cat(pid)
cat("\n")
sink()


### FIXME: many tests below are not needed, since already in testInputCommon,
### testContinuous.R


trytime <- try(
             Time <- scan("class_labels", sep = "\t", strip.white = TRUE, nlines = 1))
if(class(trytime) == "try-error")
    caughtUserError("The time file is not of the appropriate format\n")
if(!length(Time)) caughtUserError("No survival time  file\n")
## to prevent problems with a space at end of classes
if(is.na(Time[length(Time)])) Time <- Time[-length(Time)]

tryevent <- 
    try(Event <- scan("censored_indicator", sep = "\t", strip.white = TRUE))
if(class(tryevent) == "try-error")
    caughtUserError("The status file is not of the appropriate format\n")

if(!length(Event)) caughtUserError("No censored indicator file\n")
if(is.na(Event[length(Event)])) Event <- Event[-length(Event)]



if (length(Time) != length(Event))
    caughtUserError("Survival time and event are not the same length\n")

sobject <- Surv(Time, Event)




num.cols.covariate <- count.fields("covarR", sep = "\t",
                                   quote = "",
                                   comment.char = "#")

if(length(unique(num.cols.covariate)) > 1) {
    message <-
    c("The number of columns in your covariate file\n",
          "is not the same for all rows (genes).\n",
          "We find the following number of columns\n",
          paste(num.cols.covariate, collapse = ", "))
    caughtUserError(message)
}

tryxdata <- try(
                xdata <- scan("covarR", what = double(0), sep = "\t")
                )
if(class(tryxdata) == "try-error") {
  if (length(grep("cannot allocate", tryxdata)) > 0) {
    caughtUserError(paste("Memory error.\n",
                        "Your data are too large for the current load of the servers.\n",
                        "You can try later, or get in touch with us.\n"))
    } else {
    caughtUserError("The array data file is not of the appropriate format. Most likely there are non-numeric values.\n")
  }
}

xdata <- matrix(xdata, nrow = length(num.cols.covariate), byrow = TRUE)

### FIXME: this should not be done this way!!!
system("cut -f1 covariate > geneNames")
geneNames <- read.table("geneNames",quote="", sep = "\t", stringsAsFactors = TRUE)[, 1]




## FIXME
## could use something for both forking and cluster
## as in ADaCGH2 and the distribute function. Later maybe

options(warn = 2) ## we trun coxfit warnings into erros, and deal with them

cox.parallel <- function(x, time, event, MaxIterationsCox = 200,
                         cores = detectCores(),
                         silent = TRUE) { 
    res.mat <- matrix(NA, nrow = ncol(x), ncol = 4)
    sobject <- Surv(time,event)
    options(warn = 2)
    
    funpap3 <- function (x, y, MaxIterationsCox) {
        ## naindex <- which(is.na(x))
        ## if(length(naindex)) {
        ##     x <- x[-naindex]
        ##     y <- y[-naindex, ]
        ## }
        x <- as.matrix(x)
        out1 <- try(coxph.fit(x, y,
                          strata = NULL,
                          ## weights and offset and init are missing, OK
                          ## as provision for that in the coxph.fit code
                          ##
                          method = "efron",
                          rownames = NULL,
                          control = coxph.control(iter.max = MaxIterationsCox)),
                    silent = silent)

        if(inherits(out1, "try-error")) {
            if(length(grep("Ran out of iterations", out1, fixed = TRUE))) {
                warnStatus <- 2
            } else if(length(grep("Loglik converged before", out1,
                                  fixed = TRUE))) {
                warnStatus <- 1
            } else {
                warnStatus <- 3
            }
        } else {
            warnStatus <- 0
        }
        
        if(warnStatus >= 1) {
            return(c(NA, NA, warnStatus))
        } else {
            sts <- out1$coef/sqrt(out1$var)
            return(c(out1$coef,
                     1- pchisq((sts^2), df = 1), 
                     warnStatus))
        }
    }
    
    tmp <- matrix(unlist(mclapply(as.data.frame(x),
                                  funpap3,
                                  y = sobject,
                                  MaxIterationsCox = MaxIterationsCox,
                                  mc.cores = cores)),
                  ncol = 3, byrow = TRUE)
    res.mat[, 1:3] <- tmp
    res.mat[, 4] <- p.adjust(tmp[, 2], method = "BH")
    res.mat[is.na(res.mat[, 2]), c(1, 2, 4)] <- 999
    colnames(res.mat) <- c("coeff", "p.value", "Warning", "FDR")
    return(res.mat)
}

save.image()


rescox <- cox.parallel(t(xdata), Time, Event, MaxIterationsCox = 200,
                       cores = numcores) ## can't afford these many  ##detectCores())  

### FIXME: the above can blow up, and we won't be properly notified.
### and it will continue "running" up to 8 hours. Bad.
### look at function did_lam_crash in adacgh2/cgi/runAndCheck.py
### and put that in the runAndCheck for Pomelo.

## back to normal
options(warn = 1)

p.values.original <- data.frame(
                                Row = 1:length(geneNames),
                                ID = geneNames,
                                unadj.p = rescox[, 2],
                                FDR_indep = rescox[, 4],
                                obs_stat = rescox[, 1], 
                                abs.obs_stat. = abs(rescox[, 1]),
                                Warning = rescox[, 3])

p.values.original <-
    p.values.original[order(p.values.original$unadj.p,
                            -p.values.original$abs.obs_stat.), ]
cat(rep("\n", 13), file = "multest_parallel.res")
    ## we have: Name, Row, p.value, adj.p.value, coef, abs.coef, warnings
write.table(file = "multest_parallel.res",
            p.values.original, row.names = FALSE,
            col.names = TRUE,
            quote = FALSE,
            sep = "\t",
            append = TRUE)


organism <- scan("organism", what = "char", n = 1)
idtype <- scan("idtype", what = "char", n = 1)
system(paste("../../../cgi/generate_table_Cox.py", idtype, organism))
## system(paste("/http/pomelo2/cgi/generate_table_Cox.py", idtype, organism))

cat("\nmultest_parallel.res\n", file = "pomelo.msg", append = TRUE)


#### launch as
## tryrrun = os.system('/http/mpi.log/tryRrun2.py ' + tmpDir +' 10 ' + 'PomeloII_cox &')



## Useful for testing

## Time2 <- rep(1, length(Time))
## Event2 <- rep(1, length(Time2))
## Event3 <- rep(0, length(Time2))

##  xdata[1, ] <- Time
##  xdata[2, ] <- Time2
##  xdata[3, ] <- Event
##  xdata[4, ] <- Event2
##  xdata[5, ] <- 1
##  xdata[6, ] <- 0
##  xdata[7, ] <- Event3

## rescox2 <- cox.parallel(t(xdata), Time, Event, MaxIterationsCox = 200,
##                        cores = detectCores(), silent = FALSE)  

## rescox3 <- cox.parallel(t(xdata), Time, Event, MaxIterationsCox = 200,
##                        cores = detectCores())

## rescox4 <- cox.parallel(t(xdata), Time2, Event3, MaxIterationsCox = 200,
##                        cores = detectCores())  



## Old, with papply
## cox.parallel.old <- function(x, time, event, MaxIterationsCox = 200) { 
##     res.mat <- matrix(NA, nrow = ncol(x), ncol = 4)
##     sobject <- Surv(time,event)
    
##     funpap3 <- function (x) {
##         out1 <- coxph.fit.pomelo0(x, sobject,
##                                   control = coxph.control(iter.max = MaxIterationsCox))
##         if(out1$warnStatus > 1) {
##             return(c(NA, NA, out1$warnStatus))
##         } else {
##             sts <- out1$coef/sqrt(out1$var)
##             return(c(out1$coef,
##                      1- pchisq((sts^2), df = 1), 
##                      out1$warnStatus))
##         }
##     }
    
##     tmp <- matrix(unlist(papply(as.data.frame(x),
##                                 funpap3,
##                                 papply_commondata =list(sobject = sobject))),
##                   ncol = 3, byrow = TRUE)
##     res.mat[, 1:3] <- tmp
##     res.mat[, 4] <- p.adjust(tmp[, 2], method = "BH")
##     res.mat[is.na(res.mat[, 2]), c(1, 2, 4)] <- 999
##     colnames(res.mat) <- c("coeff", "p.value", "Warning", "FDR")
##     return(res.mat)
## }
