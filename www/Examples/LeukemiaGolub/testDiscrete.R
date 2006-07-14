caughtUserError <- function(message) {
    sink(file = "errorInput")
    cat(message)
    sink()
    quit(save = "no", status = 11, runLast = TRUE)
}


num.cols.covariate <- count.fields("covarR", sep = "\t",
                                   quote = "",
                                   comment.char = "#",
                                   blank.lines.skip = TRUE)

if(length(unique(num.cols.covariate)) > 1) {
    message <-
    paste("The number of columns in your covariate file\n",
          "is not the same for all rows (genes).\n",
          "We find the following number of columns\n",
          paste(num.cols.covariate, collapse = ", "))
    caughtUserError(message)
}

tryxdata <- try(
                xdata <- scan("covarR", what = double(0), sep = "\t")
                )
if(class(tryxdata) == "try-error")
    caughtUserError("The array data file is not of the appropriate format. Most likely there are non-numeric characters\n")

xdata <- matrix(xdata, nrow = length(num.cols.covariate), byrow = TRUE)



trycl <- try(
             Class <- factor(scan("class_labels", sep = "\t", what = "char", strip.white = TRUE))
             )
## to prevent problems with a space at end of classes

if(class(trycl) == "try-error")
    caughtUserError("The class file is not of the appropriate format\n")

if(Class[length(Class)] == "") Class <- factor(Class[-length(Class)])

tclass <- table(Class)

tryttype <- try(
	 ttype <- scan("testtype", what = "char")
	 )
if((ttype == "t") & (length(tclass) > 2)) {
 	  emessage <- paste("For a t-test your data can only have two classes\n",
	  	   "but your data have ", length(tclass), ". Please fix this\n",
		   "problem and try again.")
	  caughtUserError(emessage)
	  }

if(length(Class) != dim(xdata)[2]) {
    emessage <- paste("The class file and the covariate file\n",
                      "do not agree on the number of arrays: \n",
                      length(Class), " arrays according to the class file but \n",
                      dim(xdata)[2], " arrays according to the covariate data.\n",
                      "Please fix this problem and try again.\n")
    caughtUserError(emessage)  
}

if(!(is.numeric(xdata))) {
    caughtUserError("Your covariate file contains non-numeric data. \n That is not allowed.\n")
}

if (min(tclass) < 2) {
    caughtUserError("At least one class has less than 2 samples. This is not allowed")
}

num.mis <- apply(xdata, 1, function(x) sum(is.na(x)))

if (any(num.mis) == dim(xdata)[2]) {
    caughtUserError(paste("\n Some genes have all values missings.",
                          "This is not allowed.\n",
                          "\The genes that show this problem are ",
                          paste(which(num.mis == dim(xdata)[2]), collapse = " "), "\n"))
}

if (any(num.mis >= (min(tclass) - 1))) {
    caughtUserError(paste(" Some genes have as many missings as the size ",
                          "of the smallest class minus 1. This is not allowed ",
                          "because you can end up with samples of size 1 for ",
                          "one class in some permutations.",
                          "The genes that show this problem are ",
                          paste(which(num.mis >= (min(table(tclass)) - 1)), collapse = " ")))
}
    
vararray <- apply(xdata, 1, var, na.rm = TRUE)

if(any(vararray < 1e-9)) {
    caughtUserError(paste("Some genes are constant for all samples. This leads to",
                          "variances = 0 and is probably not what you want. Please",
                          "remove these genes and try again.",
                          "The genes with constat values are in positions ",
                          paste(which(vararray < 1e-9), collapse = " ")))
}

#write.table(xdata, file = "outcovarR", sep = "\t", na = "nan", quote = FALSE,
#            row.names = FALSE, col.names = FALSE)
