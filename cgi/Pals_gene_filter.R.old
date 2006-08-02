# Hay que pillar el nombre de los genes, asi que habra que cambiar la lectura.

results.file <- read.table("multest_parallel.res", header = TRUE, skip = 13, sep="\t")
PalsOpts  <- read.table("Pals_Opts", header = TRUE, sep = "\t")
#class.names  <- read.table("class_labels", header = FALSE, sep = "\t")
class.names <- scan("class_labels", sep = "\t", what = "char", strip.white = TRUE)
if(class.names[length(class.names)] == "") class.names <- class.names[-length(class.names)]

# Add FDR value to gene name
results.file$ID <- paste(results.file$ID,"(" ,results.file$FDR_indep,")")

## testing
##save(file = "test.RData", results.file, PalsOpts)
xdata <- scan("covarR", what = double(0), sep = "\t", quiet = TRUE)
num.cols.covariate <- count.fields("covarR", sep = "\t",
                                   quote = "",
                                   comment.char = "#",
                                   blank.lines.skip = TRUE)
xdata <- matrix(xdata, nrow = length(num.cols.covariate), byrow = TRUE)


rowsuse <- subset(results.file, (unadj.p < PalsOpts$maxUnadjp) & (FDR_indep < PalsOpts$maxFDR) &
                               (obs_stat > PalsOpts$minObsrv) & (obs_stat < PalsOpts$maxObsrv) &
			       (abs.obs_stat. > PalsOpts$minAbsObsrv))

if(dim(rowsuse)[1] > PalsOpts$maxGenes) {
		    rowsuse <- rowsuse[order(rowsuse$FDR_indep, rowsuse$unadj.p, -rowsuse$abs.obs_stat), ]
		    rowsuse <- rowsuse[1:PalsOpts$maxGenes, c(1, 2)]
	    	}

if(dim(rowsuse)[1] < 2 ) {
		   system('touch NoImagemapPossible')
		   heatimagemap <- function(classname, pixelheight,
		   		   pixelwidth, htmlname, imagename){}
		   } else {

	tmp         <- try(system('rm NoImagemapPossible',ignore.stderr = TRUE), silent=TRUE)
	x           <- xdata[rowsuse[, 1], ]
	rownames(x) <- as.character(rowsuse$ID)
	genenames   <- as.character(rowsuse$ID)

# 	classname <- as.vector(class.names)

	htmlname  <- "heat.html"
	imagename <- PalsOpts$img_name

	if (PalsOpts$Pixels=="auto"){
		height <- max(15 * nrow(x), 800)
		width  <- max(20 * ncol(x), 800)
		height <- width <- min(max(height, width), 1200)
	}
	else{
		height <- width <- PalsOpts$Pixels
	}
	im1 <- imagemap(imagename, height = height, width = width)
# ******* Write number of pixels to file (for python)
	sink("numberPixels")
	cat(width)
	sink()
# ******* Use "try" to transform array of strings to numbers if possible, to do so must change warnings to errors
	options(warn=2)
	try(class.names<-as.numeric(class.names),silent=TRUE)
	options(warn=0)
# ***************************************************************************************************************
	neworder  <-order(class.names)
	x <- x[, neworder]
	if (PalsOpts$Colour=="rg") {var_colour <- redgreen(75)}
        else if (PalsOpts$Colour=="gr") {var_colour <- greenred(75)}
	else{var_colour <- topo.colors(75)}
	row.dendro <- as.dendrogram(hclust(as.dist(1 - cor(t(x),use="pairwise")), method = "complete"))

        x
        
	heatmap.2.ed(x, labRow = genenames, labCol = class.names[neworder], col = var_colour, 
			scale = "none", key = TRUE, symkey= FALSE, density.info = "none", 
			trace = "none", im1 = im1, htmlname = htmlname, margins = c(4,20), 
			dendrogram = "row", Rowv = row.dendro, Colv = NULL)
##			dendrogram = "both", Rowv = row.dendro, Colv = col.dendro)
## To add a column dendrogram, use heatmap.2.ed with the above commented line, and doing
## a dendrogram for columns


       dev.off(im1$Device)

}
