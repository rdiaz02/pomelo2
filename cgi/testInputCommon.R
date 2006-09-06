caughtUserError <- function(message) {
    ## Function that prints the string it recieves, writes it to a file and
    ## terminates R script 
    sink(file = "errorInput")
    cat(message)
    sink()
    quit(save = "no", status = 11, runLast = TRUE)
}

caughtOurError <- function(message) {
    ## Function that prints the string it recieves, writes it to a file and
    ## terminates R script
    message1 <- "Please let us know so we can fix it."
    sink(file = "errorInput")
    cat(message)
    cat(message1)
    sink()
    quit(save = "no", status = 11, runLast = TRUE)
}


num.cols.covariate <- count.fields("covarR", sep = "\t",
                                   quote = "",
                                   comment.char = "#",
                                   blank.lines.skip = TRUE)

gene.names  <- scan("gene_names", what='character(0)', sep="\t", quote = "")


# Check all rows have same number of columns
if(length(unique(num.cols.covariate)) > 1) {
    message <-
    paste("The number of columns in your covariate file\n",
          "is not the same for all rows (genes).\n",
          "We find the following number of columns\n",
          paste(num.cols.covariate, collapse = ", "))
    caughtUserError(message)
}

# Check no repeated gene names
if(length(unique(gene.names)) != length(gene.names)) {
    message <-
    paste("At least one of the gene names in the gene\n",
          "expression data file is repeated.\n",
          "Please fix this problem and try again.\n")
    caughtUserError(message)
}

if(length(gene.names) != length(num.cols.covariate)) {
    caughtOurError("Pomelo parsing error: length(num.cols.covarite) != length(gene.names)")
}

if(length(gene.names) < 1)
    caughtUserError("You need at least one gene to use Pomelo II.")


## Try read covariate data
tryxdata <- try(
                xdata <- scan("covarR", what = double(0), sep = "\t")
                )

# If error data does not have good format
if(class(tryxdata) == "try-error")
    caughtUserError("The array data file is not of the appropriate format. Most likely there are non-numeric characters\n")

if((length(xdata) %% length(gene.names)))
    caughtOurError("Pomelo error: length(xdata) not integer multiple of length(num.genes)")


## Transform covariates to matrix
xdata <- matrix(xdata, nrow = length(num.cols.covariate), byrow = TRUE)

# Check covariate contains only numeric data
if(!(is.numeric(xdata))) {
    caughtUserError("Your covariate file contains non-numeric data. \n That is not allowed.\n")
}

# Get total number of missing values
num.mis <- apply(xdata, 1, function(x) sum(is.na(x)))

# Check all elements in a row are not missing 
if (any(num.mis) == dim(xdata)[2]) {
    caughtUserError(paste("\n Some genes have all values missings.",
                          "This is not allowed.\n",
                          "\The genes that show this problem are ",
                          paste(which(num.mis == dim(xdata)[2]), collapse = " "), "\n"))
}
