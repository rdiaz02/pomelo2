library(GDD)
#library(car)
##################################  Functions #################################

# Output error to file
caughtError <- function(message) {
    sink(file = "errCovariables")
    cat(message)
    sink()
    quit(save = "no", status = 11, runLast = TRUE)
}
###############################################################################
# Remove old covariate_summary 
dummy.var <- try(system("rm covariable_summary"))

num.cols.covariables <- count.fields("covariables", sep = "\t",
                                   quote = "",
                                   comment.char = "#",
                                   blank.lines.skip = TRUE, skip=1)

# Check all rows have same number of columns
if(length(unique(num.cols.covariables)) > 1) {
    message <-
    paste("The number of columns in your covariables file\n",
          "is not the same for all rows (subjects).\n",
          "We find the following number of columns\n",
          paste(num.cols.covariables, collapse = ", "))
    caughtError(message)
}

# Try to read data
trycovarb <- try(
                 covariables.table <- read.table("covariables", header= TRUE,
                                                 sep="\t",
                                                 strip.white = TRUE)
                 )

# If data is not read terminate
if(class(trycovarb) == "try-error")
  caughtError("Unable to read covariables file. Please check you have introduced a valid file.")

if( dim(covariables.table)[1] < 1)
  caughtError("File is either empty or has an invalid format.")

if (any(is.na(covariables.table)) || any(covariables.table == "na") ||
  any(covariables.table == "NA" ) || any(covariables.table == ""))
  caughtError("Covariables file contains missing values. Either remove that covariable (column) or correct this problem.")

# Get data dimensions
table.dimensions <- dim(covariables.table)
# Get covariable names
covariable.names <- colnames(covariables.table)

# Write covariable names to file
sink("names_covariables")
cat(paste(covariable.names,collapse="\t"))
sink()


Class <- factor(scan("../class_labels", sep = "\t", what = "char", strip.white = TRUE))
# To prevent problems with a space at end of classes
if(Class[length(Class)] == "") Class <- factor(Class[-length(Class)])

num.subjects <- length(Class)

# If not same number of subjects terminate
if (table.dimensions[1] != num.subjects) {
  err.message <-
    paste("The number of subjects in the covariables file (",
          table.dimensions[1],") is not the same as the number of subjects in the expression file (",
          num.subjects,").")
  caughtError(err.message)
  
}
# Write summary of each covariable
#sink("covariable_summary",append=TRUE)
for (i in 1:table.dimensions[2]){
  sink("covariable_summary",append=TRUE)
  cat(paste(covariable.names[i],"\n"))
  cat(paste(is.factor(covariables.table[,i]),"\n"))
  print(summary(covariables.table[,i]))
  sink()
  GDD(file = paste(covariable.names[i],".png",sep=""), w=880, h=300,
      type = "png", ps = 6)
  par(mfrow=c(1,2))
  par(cex.lab = 1.6)
  par(cex.axis = 1.6)
  par(cex.main = 1.6)
  if (is.factor(covariables.table[,i])){
    tmpt <- table(covariables.table[, i],
                  Class)
    aux.factor <- covariables.table[,i]
    levels (aux.factor) <- abbreviate(levels (aux.factor))
    #rownames(tmpt) <- abbreviate(rownames(tmpt))
    plot(aux.factor,
          main = "Total number of samples",
         xlab = covariable.names[i],
         ylab = "Number of samples",
         col  = terrain.colors(nrow(tmpt)))
    mtmpt <- max(tmpt)
    barplot(tmpt, beside = TRUE,
            xlab = "Class", ylab = "Number of samples",
            col = terrain.colors(nrow(tmpt)), main =
            "Number of samples per class")
    
  }else{
    plot(density(covariables.table[,i]),
         main= "Probability density",xlab=covariable.names[i] )
    boxplot(covariables.table[, i] ~ Class,
            ylab = covariable.names[i],
            xlab = "Class",
            main = "Box plot by class",
            col = terrain.colors(nlevels(Class))) 

  }
  ## plot(covariables.table[,i],Class)
  dev.off()
}
#sink()

#GDD(file = "scatterPlot.png", w=820, h=800, type = "png", ps = 7)
#scatterplot.matrix(covariables.table, diagonal = "density")
#dev.off()

# Remove old error message if it exists
dummy.var <- try(system("rm errCovariables"))



