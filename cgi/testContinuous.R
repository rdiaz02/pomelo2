CGIDIR <- "../../../cgi"

source(paste(CGIDIR, "/testInputCommon.R", sep = ""))


## zz: que leemos aqui????
trycl <- try(
             Class <- scan("class_labels", sep = "\t", what = double(0), strip.white = TRUE,
                           nlines = 1)
             )
## to prevent problems with a space at end of classes
if(is.na(Class[length(Class)])) Class <- Class[-length(Class)]


if(class(trycl) == "try-error")
    caughtUserError("The continuous dependent variable (or survival time) file is not of the appropriate format (most likely, it is a non-numeric variable)\n")



if(any(Class == ""))
  caughtUserError("The continuous dependent variable (or survival time)
file contains blank/empty values; that is not allowed.
Maybe there are trailing tabs or spaces at the end of the file?\n")

if(any(is.na(Class)))
   caughtUserError("The continuous dependent variable (or survival time)
file contains missing values; that is not allowed.
Maybe there are trailing tabs or spaces at the end of the file?\n")



#if(any(is.na(Class)))
#    caughtUserError("The continuous dependent variable (or survival time)
#file contain missing values; that is not allowed\n")

if(length(Class) != dim(xdata)[2]) {
    emessage <- paste("The class file and the covariate file\n",
                      "do not agree on the number of arrays: \n",
                      length(Class), " arrays according to the class file but \n",
                      dim(xdata)[2], " arrays according to the covariate data.\n",
                      "Please fix this problem and try again.\n")
    caughtUserError(emessage)  
}

if(!(is.numeric(Class))) {
    caughtUserError("Your continuous dep. variable file contains non-numeric data. \n That is not allowed.\n")
}

vararray <- apply(xdata, 1, var, na.rm = TRUE)

if(any(vararray < 1e-9)) {
    caughtUserError(paste("Some genes are constant for all samples. This leads to",
                          "variances = 0 and is probably not what you want. Please",
                          "remove these genes and try again.",
                          "The genes with constat values are in positions ",
                          paste(which(vararray < 1e-9), collapse = " ")))
}

write.table(xdata, file = "outcovarR", sep = "\t", na = "nan", quote = FALSE,
            row.names = FALSE, col.names = FALSE)

