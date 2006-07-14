### timings: 30000 x 100: scan: 20 sec; read.table: 140 sec;







caughtUserError <- function(message) {
    sink(file = "errorInput")
    cat(message)
    sink()
    quit(save = "no", status = 11, runLast = TRUE)
}


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
if(class(tryxdata) == "try-error")
    caughtUserError("The array data file is not of the appropriate format. Most likely there are non-numeric values.\n")

xdata <- matrix(xdata, nrow = length(num.cols.covariate), byrow = TRUE)


## zz: que leemos aqui????
trycl <- try(
             Class <- scan("class_labels", sep = "\t", what = double(0), strip.white = TRUE)
             )
## to prevent problems with a space at end of classes

if(class(trycl) == "try-error")
    caughtUserError("The continuous dependent variable (or survival time) file is not of the appropriate format (most likely, it is a non-numeric variable)\n")

if(Class[length(Class)] == "") Class <- factor(Class[-length(Class)])

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

if(!(is.numeric(Class))) {
    caughtUserError("Your continuous dep. variable file contains non-numeric data. \n That is not allowed.\n")
}


num.mis <- apply(xdata, 1, function(x) sum(is.na(x)))

if (any(num.mis == dim(xdata)[2])) {
    caughtUserError(paste("\n Some genes have all values missings.",
                          "This is not allowed.\n",
                          "\The genes that show this problem are ",
                          paste(which(num.mis == dim(xdata)[2]), collapse = " "), "\n"))
}

vararray <- apply(xdata, 1, var)

if(any(vararray < 1e-9)) {
    caughtUserError(paste("Some genes are constant for all samples. This leads to",
                          "variances = 0 and is probably not what you want. Please",
                          "remove these genes and try again.",
                          "The genes with constat values are in positions ",
                          paste(which(vararray < 1e-9), collapse = " ")))
}

write.table(xdata, file = "outcovarR", sep = "\t", na = "nan", quote = FALSE,
            row.names = FALSE, col.names = FALSE)

