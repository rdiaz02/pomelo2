# Get results table and produce contrast file with the
# same layout as other Pomelo II outputs.
contrast.to.file <- function(results.table, test.type, num.genes, num.columns){
  filename <- paste( test.type,'.res', sep="")
  sink(filename)
  cat(" Function call:                   \tcalculate_contrasts.R\n")
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
  cat("Row\tID\tunadj.p\tFDR_indep\tobs_stat\tabs(obs_stat)\tB\n")
  sink()
  
  
  write.table( results.table, filename , quote=FALSE,
               sep='\t'     , append=TRUE           , col.names=FALSE )
}
# Function sign returns zero if value is zero,
# this function returns +1
my.sign <- function(value){
  value.sign <- sign(value)
  value.sign[value.sign== 0] <- 1
  return (value.sign)
}

library(limma)
# Load linear model data 
load("fitdata.Rdata")
# Read contrast
# Use sep \t to coerce scan to read a single value
contrast.def     <- scan("contrast_classes", what='character(0)', sep="\t")
# Create contrast matrix
contrast.matrix  <- makeContrasts(contrast.def, levels=fit$design)
# Calculate contrast
fit2             <- contrasts.fit(fit, contrast.matrix)
# Call empirical Bayes function
fit2             <- eBayes(fit2)
# Find differentially expressed genes
results          <- decideTests(fit2)
# Define test name
test.type        <- contrast.def

results.table    <- cbind(  unadj.p       = fit2$p.value,
                            FDR.indep     = round(p.adjust(fit2$p.value, method ="BH"),8),
                            obs.stat      = fit2$t,
                            abs.obs.stat  = abs(fit2$t),
                            B             = fit2$lods)
# Get gene names
gene.names              <- fit2$genes
# Get number of genes
num.genes               <- length(gene.names)
# Add gene names and numbers to table
results.table           <- cbind(gene.names, results.table)
# Name rows with numbers
array.rownum            <- sequence(num.genes)
rownames(results.table) <- array.rownum
# Number of contrasts
num.columns             <- "1" 

# Write table to file
contrast.to.file (results.table, test.type, num.genes, num.columns)


non.zero.FDR <- as.numeric(results.table[,3])

non.zero.FDR[ non.zero.FDR== 0] <- 0.0000001
  
#FDR.by.sign.p <- as.numeric(results.table[,3])*sign(as.numeric(results.table[,4]))
FDR.by.sign.p <- non.zero.FDR*my.sign(as.numeric(results.table[,4]))

# See if contrast_compare.res exists
tryTest  <- try(header.string              <- scan(file="contrast_compare.res",sep ="\t",what="character(0)",nlines=1))
tryTest  <- try(contrast.compare           <- read.table(file="contrast_compare.res",sep = "\t",row.names=1,skip=1))
tryDummy <- try(colnames(contrast.compare) <- header.string)

if(class(tryTest) == "try-error"){
  contrast.table           <- cbind(gene.names, FDR.by.sign.p)
  colnames(contrast.table) <- c("Gene name", test.type)
}else{
  contrast.table           <- cbind(FDR.by.sign.p)
  colnames(contrast.table) <- test.type
  contrast.table           <- cbind(contrast.compare , contrast.table)
}

write.table( contrast.table, 'contrast_compare.res', quote     = FALSE,
             sep='\t'      ,  row.names=TRUE       , col.names = TRUE )

