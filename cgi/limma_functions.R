# ****************************************************************************************************
# ******************************    Functions start here    ******************************************

# Output error to file
caughtError <- function(message) {
    sink(file = "pomelo.msg")
    cat(message)
    sink()
    quit(save = "no", status = 11, runLast = TRUE)
}

## not estimable?

not.estim <- function() {
## for previous versions of limma, that left "not estimable" as warning
  lw <- warnings()
  warn.string <- paste(paste(names(lw), collapse = " "),
                       paste(lw, collapse = " "),
                       sep = " ")
  problema <- length(grep("not estimable",
                          warn.string))
  if(problema) {
###    print("uuu")
    caughtError("Some coefficients of your design are not estimable. This is not a problem of Pomelo but of your design. You should talk to a statistican.")
  }
}

not.estim2 <- function(lw) {
  problema <- length(grep("not estimable",
                          lw))
  if(problema) {
###    print("uuu")
    caughtError("Some coefficients of your design are not estimable. This is not a problem of Pomelo but of your design. You should talk to a statistican.")
  }
}




# Recieve class labels, look for covariables and return model matrix 
covariables.model.matrix <- function(class.labels, test.type){
  tryread.covars <- try(
                        Chosen.covariables <- scan("COVARIABLES/chosen_covariables", sep = "\t", what = "char", strip.white = TRUE)
                        ) 
  # Make factor
  Class <- factor(class.labels)
  # Make model matrix. Either just class labels or covariables and class labels
  if (test.type=="t"){
      design.matrix <- model.matrix(~ Class)
      design.list   <- list(design.matrix)
  }
  if (test.type=="anova"){
    if (class(tryread.covars)=="try-error"){
      design.matrix.NO.intercept <- model.matrix(~ Class + 0)
      design.matrix.intercept    <- model.matrix(~ Class)
      design.list                <- list(design.matrix.intercept, design.matrix.NO.intercept)
    }else{
      
      covariables.table          <-  read.table("COVARIABLES/covariables", header= TRUE, sep="\t",
                                                strip.white = TRUE)
      covariable.columns         <- which(colnames(covariables.table)%in% Chosen.covariables)
      if(length(covariable.columns) < 1) {
        caughtError("The names of the chosen do not match the names of the additional covariates. Most likely, your add. covars. did not have a first row with names.")
      }
      if(length(Class) != dim(covariables.table[covariable.columns])[1]) {
        caughtError("Different number of samples in array data and additional covariates. Most likely, your add. covars. did not have a first row with names.")
      }
      
      covariables.matrix         <- cbind(Class, covariables.table[covariable.columns])
      ## make sure we do not get numeric values that are way out there
      numeric.vars <- which(unlist(lapply(covariables.matrix, function(x) is.numeric(x))))
      if(length(numeric.vars > 0)) {
        scales <- sd(covariables.matrix[, numeric.vars])
        scales[scales == 0] <- 1 ## prevent dividing by 0
        covariables.matrix[, numeric.vars] <- scale(covariables.matrix[, numeric.vars], scale = scales)
      }
      design.matrix.NO.intercept <- model.matrix(~ . + 0, covariables.matrix)
      design.matrix.intercept    <- model.matrix(~ .    , covariables.matrix)
      design.list                <- list(design.matrix.intercept, design.matrix.NO.intercept)
    }
  }
  return(design.list)
}

# T-test using limma
t.test.limma <- function(edf1, class.labels){  
  design.list <- covariables.model.matrix(class.labels, "t")
  fit         <- lmFit(edf1, design.list[[1]])
  fit         <- eBayes(fit)
  return(fit)
}

# Paired T-test limma
paired.t.test.limma <- function(edf1, class.labels, paired.vector){  
  Class  <- factor(class.labels)
  paired <- factor(paired.vector)
  design <- model.matrix(~ Class + paired)
  fit    <- lmFit(edf1, design)
  fit    <- eBayes(fit)
  return(fit)
}

# Anova test limma
anova.test.limma <- function(edf1, class.labels){  
    design.list <- covariables.model.matrix(class.labels, "anova")
    fit    <- lmFit(edf1, design.list[[2]])
    save(fit, file="fitdata.Rdata")
    # Make factor
    #arreglado class labels con numeros por clases
    class.labels.aux <- paste("Class",class.labels,sep="")
    Class <- factor(class.labels.aux)    
 #   Class <- factor(class.labels)
    d0     <- design.list[[1]]
    #This is the part for obtaining the contrasts 
    colnames(d0)[1:nlevels(Class)] <- c("Intercept", levels(Class)[-1])

    constructContrasts <- paste("makeContrasts(",
                                paste(levels(Class)[-1], collapse = ", "),
                                ", levels = d0)", collapse = "")
  
    contrasts.d0   <- eval(parse(text = constructContrasts))
    # End  part for obtaining the contrasts
    lima.mod.0    <- lmFit(edf1, d0)
    lima.mod.0.cr <- contrasts.fit(lima.mod.0, contrasts.d0)
    fit.A         <- eBayes(lima.mod.0.cr)
 # }
  return(fit.A)

    ### yes, the above is all correct, the fitting of models with and without
    ### and the obtentino of the F statistic
    ### And the examples of numerical testing do check it in yet another way.
}

# Get results table and produce multest_parallel.res file with the
# same layout as other Pomelo II outputs.
results.to.file <- function(results.table, test.type, num.genes, num.columns){
  sink("multest_parallel.res")
  cat(" Function call:                   \tlimma_functions.R\n")
  cat(" Data file:                    \t\tcovariate\n")
  cat(" Class file:                   \t\tclass_labels\n")
  text.numVariables <- paste(" Number of variables or genes:\t\t", num.genes, "\n")
  cat(text.numVariables)
  text.numColumns   <- paste(" Number of columns:     \t\t", num.columns, "\n")
  cat(text.numColumns)
  text.testType     <- paste(" Type of test:             \t\t", test.type, "\n")
  cat(text.testType)
  cat(" MinP or MaxT?:                \t\tmaxT\n")
  cat(" Permutations used:            \t\tNon permutation method\n")
  cat(" Random seed:                  \t\tNone\n\n")
  cat("###############################################################\n\n\n")
  if ( test.type=="Anova_limma")
    cat("Row\tID\tunadj.p\tFDR_indep\tobs_stat\tabs(obs_stat)\n")
  else
    cat("Row\tID\tunadj.p\tFDR_indep\tobs_stat\tabs(obs_stat)\tB\n")
  sink()
  write.table( results.table, 'multest_parallel.res', quote=FALSE,
               sep='\t'     , append=TRUE           , col.names=FALSE )
}
# ******************************    End of functions    **********************************************
# ****************************************************************************************************
options(contrasts = c("contr.treatment", "contr.poly"))
library(limma)
sink("mpiOK")
cat("Dummy file so as to not trigger an mpi error message\n")
sink()
# Read gene expression data and class labels
# tryCovar <- try (edf1          <- read.table("covariate", sep = "\t",
#                                             row.names = 1, quote=""))
# if(class(tryCovar) == "try-error")
#   caughtError("Multest crashed trying to run limma Anova test.\n This is most likely due to invalid data (Such as repeated gene names,etc).\n") 

load("edf1.for.limma.RData")



class.labels  <- factor(scan("class_labels", sep = "\t", what = "char", strip.white = TRUE, nlines = 1))
if (class.labels[length(class.labels)] == ""){ class.labels <- class.labels[-length(class.labels)] }

# Get test type
test.type     <- scan("testtype", what='character(0)')
# Calculate number of genes and classes
covariate.dim <- dim(edf1)
num.genes     <- covariate.dim[1]
num.columns   <- covariate.dim[2]

# If test type is t_limma do t_limma test
if (test.type == "t_limma"){
  tryTest <- try(fit <- t.test.limma(edf1, class.labels))
  if(class(tryTest) == "try-error") {
    if (length(grep("cannot allocate", tryTest)) > 0) {
      caughtError(paste("Memory error.\n",
                        "Your data are too large for the current load of the servers.\n",
                        "You can try later, or get in touch with us.\n"))
    } else {
      caughtError("Multest crashed trying to run limma t test.\n This is most likely due to invalid data.\n")
    }
  }
}

# If test type is t_limma_paired do t_limma_paired test
if (test.type == "t_limma_paired"){
  paired.vector <- scan("paired_indicator")
  tryTest <- try(fit <- paired.t.test.limma(edf1, class.labels, paired.vector))
  if(class(tryTest) == "try-error") {
    if (length(grep("cannot allocate", tryTest)) > 0) {
      caughtError(paste("Memory error.\n",
                        "Your data are too large for the current load of the servers.\n",
                        "You can try later, or get in touch with us.\n"))
    } else {
      caughtError("Multest crashed trying to run paired limma t test.\n This is most likely due to invalid data.\n")
    }
  }
}

# If test type is Anova_limma do Anova_limma test
if (test.type == "Anova_limma"){
  lw <- capture.output(tryTest <- try(fit <- anova.test.limma(edf1, class.labels)))
  if(class(tryTest) == "try-error") {
    if (length(grep("cannot allocate", tryTest)) > 0) {
      caughtError(paste("Memory error.\n",
                        "Your data are too large for the current load of the servers.\n",
                        "You can try later, or get in touch with us.\n"))
    } else {
      caughtError("Multest crashed trying to run Anova limma test.\n This is most likely due to invalid data.\n")
    } 
  }
  
}

not.estim()
not.estim2(lw)

# Create results table (either F test or t test)
array.rownum  <- sequence(num.genes)
if (test.type == "Anova_limma"){
  results.table <- cbind(unadj.p   = fit$F.p.value,
                         FDR_indep = round(p.adjust(fit$F.p.value, method ="BH"),8),
                         obs_stat  = fit$F,
                         obs_stat  = abs(fit$F))
}else{
  results.table <- cbind(unadj.p   = fit$p.value[,2],
                         FDR_indep = round(p.adjust(fit$p.value[,2], method ="BH"),8),
                         obs_stat  = fit$t[,2],
                         obs_stat  = abs(fit$t[,2]),
                         B         = fit$lods[,2])
}

gene.names    <- fit$genes
results.table <- cbind(gene.names, results.table)
rownames(results.table) <- array.rownum

# Write table to file
results.to.file(results.table, test.type, num.genes, num.columns)





  
