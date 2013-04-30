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
    if (is.loaded("mpi_initialize")){ 
        if (mpi.comm.size(1) > 0){ 
        try(print("Please use mpi.close.Rslaves() to close slaves."), silent = TRUE)
        try(mpi.close.Rslaves() , silent = TRUE)
        } 
        try(print("Please use mpi.quit() to quit R"), silent = TRUE)
        cat("\n\n Normal termination\n")
        try(stopCluster(TheCluster), silent = TRUE)
        ##        .Call("mpi_finalize")
        try(mpi.quit(save = "no"), silent = TRUE)
    }
    try(stopCluster(TheCluster), silent = TRUE)
    cat("\n\n Normal termination\n")
    ## In case the CGI is not called (user kills browser)
    ## have a way to stop lam
    try(system(paste("/http/mpi.log/killLAM.py", lamSESSION, "&")))
    try(mpi.quit(save = "no"), silent = TRUE)
}


caughtUserError <- function(message) {
    sink(file = "pomelo.msg")
#  sink(file = "errorInput")
  cat(message)
    sink()
    quit(save = "no", status = 11, runLast = TRUE)
}



library(survival)
library(Rmpi)
library(papply)

mpi.spawn.Rslaves(nslaves = mpi.universe.size())
mpi.remote.exec(rm(list = ls(env = .GlobalEnv), envir =.GlobalEnv))
mpi.remote.exec(library(survival))
sink(file = "mpiOK")
cat("MPI started OK\n")
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
geneNames <- read.table("geneNames",quote="", sep = "\t")[, 1]

coxph.fit.pomelo0 <- function (x, y, init = NULL,
                              control, method = "efron",  rownames = NULL) {
    warnStatus <- 0
    naindex <- which(is.na(x))
    if(length(naindex)) {
        x <- x[-naindex]
        y <- y[naindex, ]
    }
    x <- as.matrix(x) ## this ain't very efficient
    n <- nrow(y)
    if (is.matrix(x)) 
        nvar <- ncol(x)
    else if (length(x) == 0) 
        nvar <- 0
    else nvar <- 1
    time <- y[, 1]
    status <- y[, 2]
    sorted <- order(time)
    newstrat <- as.integer(rep(0, n))
    
    offset <- rep(0, n)
    weights <- rep(1, n)

    stime <- as.double(time[sorted])
    sstat <- as.integer(status[sorted])
    if (nvar == 0) {
        x <- as.matrix(rep(1, n))
        nullmodel <- TRUE
        nvar <- 1
        init <- 0
        maxiter <- 0
    }
    else {
        nullmodel <- FALSE
        maxiter <- control$iter.max
        if (!missing(init) && !is.null(init)) {
            if (length(init) != nvar) 
                stop("Wrong length for inital values")
        }
        else init <- rep(0, nvar)
    }
    coxfit <- .C("coxfit2", iter = as.integer(maxiter), as.integer(n), 
        as.integer(nvar), stime, sstat, x = x[sorted, ], as.double(offset[sorted] - 
            mean(offset)), as.double(weights), newstrat, means = double(nvar), 
        coef = as.double(init), u = double(nvar), imat = double(nvar * 
            nvar), loglik = double(2), flag = integer(1), double(2 * 
            n + 2 * nvar * nvar + 3 * nvar), as.double(control$eps), 
        as.double(control$toler.chol), sctest = as.double(method == 
            "efron"), PACKAGE = "survival")
    if (nullmodel) {
        score <- exp(offset[sorted])
        coxres <- .C("coxmart", as.integer(n), as.integer(method == 
            "efron"), stime, sstat, newstrat, as.double(score), 
            as.double(weights), resid = double(n), PACKAGE = "survival")
        resid <- double(n)
        resid[sorted] <- coxres$resid
        names(resid) <- rownames
        list(loglik = coxfit$loglik[1], linear.predictors = offset, 
            residuals = resid, method = c("coxph.null", "coxph"))
    }
    else {
        var <- matrix(coxfit$imat, nvar, nvar)
        coef <- coxfit$coef
        if (coxfit$flag < nvar) 
            which.sing <- diag(var) == 0
        else which.sing <- rep(FALSE, nvar)
        infs <- abs(coxfit$u %*% var)
        if (maxiter > 1) {
            if (coxfit$flag == 1000) {
              ## I comment out the warnings: we don't need
              ## them and they fill up the logs
##                warning("Ran out of iterations and did not converge")
                warnStatus <- 2
            }
            else {
                infs <- ((infs > control$eps) & infs > control$toler.inf * 
                  abs(coef))
                if (any(infs)) {
##                  warning(paste("Loglik converged before variable ", 
##                    paste((1:nvar)[infs], collapse = ","), "; beta may be infinite. "))
                  warnStatus <- 1
              }
            }
        }
        names(coef) <- dimnames(x)[[2]]
        lp <- c(x %*% coef) + offset - sum(coef * coxfit$means)
        score <- exp(lp[sorted])
        coef[which.sing] <- NA
        list(coefficients = coef, var = var, warnStatus = warnStatus,
             loglik = coxfit$loglik)
    }
}


mpi.bcast.Robj2slave(coxph.fit.pomelo0)


## what follows is for pomelo
cox.parallel <- function(x, time, event, MaxIterationsCox = 200) { 
    res.mat <- matrix(NA, nrow = ncol(x), ncol = 4)
    sobject <- Surv(time,event)
    
    funpap3 <- function (x) {
        out1 <- coxph.fit.pomelo0(x, sobject,
                                  control = coxph.control(iter.max = MaxIterationsCox))
        if(out1$warnStatus > 1) {
            return(c(NA, NA, out1$warnStatus))
        } else {
            sts <- out1$coef/sqrt(out1$var)
            return(c(out1$coef,
                     1- pchisq((sts^2), df = 1), 
                     out1$warnStatus))
        }
    }
    
    tmp <- matrix(unlist(papply(as.data.frame(x),
                                funpap3,
                                papply_commondata =list(sobject = sobject))),
                  ncol = 3, byrow = TRUE)
    res.mat[, 1:3] <- tmp
    res.mat[, 4] <- p.adjust(tmp[, 2], method = "BH")
    res.mat[is.na(res.mat[, 2]), c(1, 2, 4)] <- 999
    colnames(res.mat) <- c("coeff", "p.value", "Warning", "FDR")
    return(res.mat)
}

save.image()

rescox <- cox.parallel(t(xdata), Time, Event, MaxIterationsCox = 200)  

### FIXME: the above can blow up, and we won't be properly notified.
### and it will continue "running" up to 8 hours. Bad.
### look at function did_lam_crash in adacgh2/cgi/runAndCheck.py
### and put that in the runAndCheck for Pomelo.


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
system(paste("/http/pomelo2/cgi/generate_table_Cox.py", idtype, organism))

cat("\nmultest_parallel.res\n", file = "pomelo.msg", append = TRUE)


#### lanzar como:
## tryrrun = os.system('/http/mpi.log/tryRrun2.py ' + tmpDir +' 10 ' + 'PomeloII_cox &')
