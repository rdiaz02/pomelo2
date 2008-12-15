CGIDIR <- "../../../cgi"

source(paste(CGIDIR, "/testInputCommon.R", sep = ""))


check.class.size <- function(x, xdata.matrix, Class) {
    cols.class   <- which(Class==x)
    number.cases <- length(cols.class)
    xdata.class  <- xdata.matrix[,cols.class]
    num.mis      <- apply(xdata.class, 1, function(x) sum(is.na(x))) 
    if (any(number.cases-num.mis<2)){
      caughtUserError(paste("At least one gene has less than two cases for one class.",
                            "This is not allowed.\n", "The class is: ", x,"\n",
                            "The genes are in rows:\n ",
                            paste(which(number.cases-num.mis<2), collapse = " "), "\n"))
    }
  
}

# Read class data
trycl <- try(
             Class <- factor(scan("class_labels", sep = "\t", what = "char", strip.white = TRUE,
                                  nlines = 1))
             )

# Check class read worked
if(class(trycl) == "try-error")
    caughtUserError("The class file is not of the appropriate format\n")


# To prevent problems with a space at end of classes
if(Class[length(Class)] == "") Class <- factor(Class[-length(Class)])



if(any(Class == ""))
  caughtUserError("The class variable 
file contains blank/empty values; that is not allowed.
Maybe there are trailing tabs or spaces at the end of the file?\n")

if(any(is.na(Class)))
   caughtUserError("The class variable
file contains missing values; that is not allowed.
Maybe there are trailing tabs or spaces at the end of the file?\n")



tclass <- table(Class)


tryttype <- try(
	 ttype <- scan("testtype", what = "char")
         )

# Check each class has more than two samples
if (min(tclass) < 2) {
    caughtUserError("At least one class has less than 2 samples. This is not allowed")
}

if (ttype == "t_limma"||ttype == "t_limma_paired" || ttype == "Anova_limma" ){
    
    if(length(gene.names) < 2)
        caughtUserError("For all limma tests you need at least two genes")
    Classes <- levels(Class)
    sapply(Classes,function(x,xdata,Class)
           check.class.size(x,xdata,Class), xdata = xdata, Class = Class)
 
}

# Generic t-test specific conditions
if((ttype == "t"||ttype == "t_limma"||ttype == "t_limma_paired" ) & (length(tclass) > 2)) {
 	  emessage <- paste("For a t-test your data can only have two classes\n",
	  	   "but your data has ", length(tclass), ". Please fix this\n",
		   "problem and try again.")
	  caughtUserError(emessage)
	  }

# Make sure class labels have same length as number of covariate columns
if(length(Class) != dim(xdata)[2]) {
    emessage <- paste("The class file and the covariate file\n",
                      "do not agree on the number of arrays: \n",
                      length(Class), " arrays according to the class file but \n",
                      dim(xdata)[2], " arrays according to the covariate data.\n",
                      "Please fix this problem and try again.\n")
    caughtUserError(emessage)  
  }

# For permutation tests check no permutation can leave a class with a
# single value (due to missing values) 
if ((ttype != "FisherIxJ" && ttype != "t_limma" && ttype != "t_limma_paired" && ttype != "Anova_limma") & (any(num.mis >= (min(tclass) - 1)))) {
    caughtUserError(paste(" Some genes have as many missings as the size ",
                          "of the smallest class minus 1. This is not allowed ",
                          "because you can end up with samples of size 1 for ",
                          "one class in some permutations.",
                          "The genes that show this problem are ",
                          paste(which(num.mis >= (min(table(tclass)) - 1)), collapse = " ")))
}


# Find gene variance
if( (ttype != "FisherIxJ")) {
    vararray <- apply(xdata, 1, var, na.rm = TRUE)

# Check gene variance is not too small (close to zero) 
    if(any(vararray < 1e-9)) {
        caughtUserError(paste("Some genes are constant for all samples. This leads to",
                              "variances = 0 and is probably not what you want. Please",
                              "remove these genes and try again.",
                              "The genes with constat values are in positions ",
                              paste(which(vararray < 1e-9), collapse = " ")))
    }
}

# Data tests sepcific to paired limma t-test
if(ttype == "t_limma_paired") {
  
  # Read paired indicator file and remove "" from end
  trypaired <- try(
              paired.indicator<- factor(scan("paired_indicator", sep = "\t", what = integer(0), strip.white = TRUE))
             )
  # Check read worked
  if(class(trypaired) == "try-error")
    caughtUserError("The paired indicator file is not of the appropriate format\n")
  
  # To prevent problems with a space at end of classes
  if( is.na(paired.indicator[length(paired.indicator)]) ) paired.indicator <- factor(paired.indicator[-length(paired.indicator)])

  # Get table with value frequency
  paired.freq <- table(paired.indicator)
  
  # Check two values per factor
  if (any(paired.freq!=2)){
    
    caughtUserError(paste("\n Paired indicator must contain only pairs of values.",
                          "This is not the case.\n",
                          "The numbers that have more or less than two values are: ",
                          paste(names(which(paired.freq!=2)), collapse = " "), "\n"))
  }
  
  # Check size paired indicator equal size class labels
  if (length(paired.indicator) != length(Class)){

    emessage <- paste("The class file and paired indicator file\n",
                      "do not agree on the number of arrays: \n",
                      length(Class), " arrays according to the class file but \n",
                      length(paired.indicator), " arrays according to the paired indicator.\n",
                      "Please fix this problem and try again.\n")
    caughtUserError(emessage)

  }
}


# Data tests sepcific to Fisher test
if(ttype == "FisherIxJ") {
	 minX <- min(xdata) 
	 maxX <- max(xdata)
	 
	 if(minX != 0) 
	 	 caughtUserError(paste("For Fisher's test, the data should be consecutive integers that start at 0;",
		 "Your data start at ", minX))
	 if(maxX > ((ncol(xdata) * nrow(xdata)) - 1)) 
	 	 caughtUserError("Your data are not made of consecutive integers that start at 0")
	
	 ddu <- diff(sort(as.vector(xdata)))
	 if(max(ddu) > 1)
	      caughtUserError("Your data are not made of consecutive integers")
}

# Data tests sepcific to Annova limma test
if(ttype == "Anova_limma") {
  different.classes <- levels(Class)
  sink("diff_classes")
  cat(paste(different.classes, collapse="\t"))
  sink()
}

# Data tests sepcific to Annova limma test
if(ttype == "Anova") {
  if(length(tclass) < 3){
    emessage <- paste("For an Annova permutation test your data must have more than two classes.\n",
                      "If you wish to analyse two classes you could use a t-test.\n")
    caughtUserError(emessage)
  }
}


if (ttype == "t_limma"||ttype == "t_limma_paired" || ttype == "Anova_limma" ){
  edf1 <- as.data.frame(xdata)
  rownames(edf1) <- gene.names
  save(file = "edf1.for.limma.RData", edf1)
}  
