### Just a test; not completed. R.D.-U.

source("/http/pomelo2/cgi/rpy_source.R")

xdata <- scan("covarR", what = double(0), sep = "\t")
num.cols.covariate <- count.fields("covarR", sep = "\t",
                                   quote = "",
                                   comment.char = "#",
                                   blank.lines.skip = TRUE)
xdata <- matrix(xdata, nrow = length(num.cols.covariate), byrow = TRUE)

Class <- scan("class_labels", sep = "\t", what = "char",
              strip.white = TRUE, nlines = 1)
if(Class[length(Class)] == "") Class <- Class[-length(Class)]

rows.to.use <- scan("result_row_id.txt", what = double(0))
x <- xdata[rows.to.use]

heatimagemap(x, genename[rows.to.use], 
