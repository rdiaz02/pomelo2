library(imagemap)
library(gplots,verbose=FALSE,warn.conflicts = FALSE)
library(GDD)
imagemap <- function(filename,width=480,height=480,title='Imagemap from R'){
	  GDD(file = paste(filename,".png",sep=''),w=width, h=height,
	  type = "png", ps = 16)
  im <- list()
  im$Device <- dev.cur()
  im$Filename=filename
  im$Height=height
  im$Width=width
  im$Objects <- list()
  im$HTML <- list()
  im$title <- title

  class(im) <- "imagemap"
  im
}

heatmap.2.ed <- function (x, Rowv = NULL, Colv = if (symm) "Rowv" else NULL,
    distfun = dist, hclustfun = hclust, dendrogram = c("both",
        "row", "column", "none"), symm = FALSE, scale = c("none",
        "row", "column"), na.rm = TRUE, revC = identical(Colv,
        "Rowv"), add.expr, breaks, col = "heat.colors", colsep,
    rowsep, sepcolor = "white", sepwidth = c(0.05, 0.05), cellnote,
    notecex = 1, notecol = "cyan", na.color = par("bg"), trace = c("column",
        "row", "both", "none"), tracecol = "cyan", hline = median(breaks),
    vline = median(breaks), linecol = tracecol, margins = c(5,
        5), ColSideColors, RowSideColors, cexRow = 0.2 + 1/log10(nr),
    cexCol = 0.2 + 1/log10(nc), labRow = NULL, labCol = NULL,
    key = TRUE, density.info = c("histogram", "density", "none"),
    denscol = tracecol, symkey = TRUE, densadj = 0.25, main = NULL,
    xlab = NULL, ylab = NULL, im1, htmlname,...)
{
    scale01 <- function(x, low = min(x), high = max(x)) {
        x <- (x - low)/(high - low)
        x
    }
    scale <- if (symm && missing(scale))
        "none"
    else match.arg(scale)
    dendrogram <- match.arg(dendrogram)
    trace <- match.arg(trace)
    density.info <- match.arg(density.info)
    if (!missing(breaks) && (scale != "none"))
        warning("Using scale=\"row\" or scale=\"column\" when breaks are",
            "specified can produce unpredictable results.", "Please consider using only one or the other.")
    if (length(di <- dim(x)) != 2 || !is.numeric(x))
        stop("`x' must be a numeric matrix")
    nr <- di[1]
    nc <- di[2]
    if (nr <= 1 || nc <= 1)
        stop("`x' must have at least 2 rows and 2 columns")
    if (!is.numeric(margins) || length(margins) != 2)
        stop("`margins' must be a numeric vector of length 2")
    if (missing(cellnote))
        cellnote <- matrix("", ncol = ncol(x), nrow = nrow(x))
    if (is.null(Rowv))
        Rowv <- rowMeans(x, na.rm = na.rm)
    if (is.null(Colv))
##        Colv <- colMeans(x, na.rm = na.rm)
	Colv <- 1:nc  
    if (dendrogram %in% c("both", "row")) {
        if (inherits(Rowv, "dendrogram"))
            ddr <- Rowv
        else {
            hcr <- hclustfun(distfun(x))
            ddr <- as.dendrogram(hcr)
            if (!is.logical(Rowv) || Rowv)
                ddr <- reorder(ddr, Rowv)
        }
        rowInd <- order.dendrogram(ddr)
        if (nr != length(rowInd))
            stop("row dendrogram ordering gave index of wrong length")
    }
    else {
        rowInd <- order(Rowv)
    }
    if (dendrogram %in% c("both", "column")) {
        if (inherits(Colv, "dendrogram"))
            ddc <- Colv
        else if (identical(Colv, "Rowv")) {
            if (nr != nc)
                stop("Colv = \"Rowv\" but nrow(x) != ncol(x)")
            ddc <- ddr
        }
        else {
            hcc <- hclustfun(distfun(if (symm)
                x
            else t(x)))
            ddc <- as.dendrogram(hcc)
            if (!is.logical(Colv) || Colv)
                ddc <- reorder(ddc, Colv)
        }
        colInd <- order.dendrogram(ddc)
        if (nc != length(colInd))
            stop("column dendrogram ordering gave index of wrong length")
    }
    else {
        colInd <- order(Colv)
    }
    x <- x[rowInd, colInd]
    x.unscaled <- x
    cellnote <- cellnote[rowInd, colInd]
    if (is.null(labRow))
        labRow <- if (is.null(rownames(x)))
            (1:nr)[rowInd]
        else rownames(x)
    else labRow <- labRow[rowInd]
    if (is.null(labCol))
        labCol <- if (is.null(colnames(x)))
            (1:nc)[colInd]
        else colnames(x)
    else labCol <- labCol[colInd]
    if (scale == "row") {
        x <- sweep(x, 1, rowMeans(x, na.rm = na.rm))
        sx <- apply(x, 1, sd, na.rm = na.rm)
        x <- sweep(x, 1, sx, "/")
    }
    else if (scale == "column") {
        x <- sweep(x, 2, colMeans(x, na.rm = na.rm))
        sx <- apply(x, 2, sd, na.rm = na.rm)
        x <- sweep(x, 2, sx, "/")
    }
    if (missing(breaks) || is.null(breaks) || length(breaks) <
        1)
        if (missing(col))
            breaks <- 16
        else breaks <- length(col) + 1
    if (length(breaks) == 1) {
        breaks <- seq(min(x, na.rm = na.rm), max(x, na.rm = na.rm),
            length = breaks)
    }
    nbr <- length(breaks)
    ncol <- length(breaks) - 1
    if (class(col) == "function")
        col <- col(ncol)
    else if (is.character(col) && length(col) == 1)
        col <- do.call(col, list(ncol))
    min.breaks <- min(breaks)
    max.breaks <- max(breaks)
    x[] <- ifelse(x < min.breaks, min.breaks, x)
    x[] <- ifelse(x > max.breaks, max.breaks, x)
    lmat <- rbind(4:3, 2:1)
    lwid <- lhei <- c(1, 4)
    if (!missing(ColSideColors)) {
        if (!is.character(ColSideColors) || length(ColSideColors) !=
            nc)
            stop("'ColSideColors' must be a character vector of length ncol(x)")
        lmat <- rbind(lmat[1, ] + 1, c(NA, 1), lmat[2, ] + 1)
        lhei <- c(lhei[1], 0.2, lhei[2])
    }
    if (!missing(RowSideColors)) {
        if (!is.character(RowSideColors) || length(RowSideColors) !=
            nr)
            stop("'RowSideColors' must be a character vector of length nrow(x)")
        lmat <- cbind(lmat[, 1] + 1, c(rep(NA, nrow(lmat) - 1),
            1), lmat[, 2] + 1)
        lwid <- c(lwid[1], 0.2, lwid[2])
    }
    lmat[is.na(lmat)] <- 0
    op <- par(no.readonly = TRUE)
    on.exit(par(op))
    layout(lmat, widths = lwid, heights = lhei, respect = FALSE)
    if (!missing(RowSideColors)) {
        par(mar = c(margins[1], 0, 0, 0.5))
        image(rbind(1:nr), col = RowSideColors[rowInd], axes = FALSE)
    }
    if (!missing(ColSideColors)) {
        par(mar = c(0.5, 0, 0, margins[2]))
        image(cbind(1:nc), col = ColSideColors[colInd], axes = FALSE)
    }
    par(mar = c(margins[1], 0, 0, margins[2]))
    if (!symm || scale != "none") {
        x <- t(x)
        cellnote <- t(cellnote)
    }
    if (revC) {
        iy <- nr:1
        ddr <- rev(ddr)
        x <- x[, iy]
        cellnote <- cellnote[, iy]
    }
    else iy <- 1:nr

    image(1:nc, 1:nr, x, xlim = 0.5 + c(0, nc), ylim = 0.5 +
        c(0, nr), axes = FALSE, xlab = "", ylab = "", col = col,
        breaks = breaks, ...)

# Added by Edward Morrissey: Imagemap stuff ********************************************************
	for(i in 1:nr) {
	bly <- 0.5+(i-1)*1
	toprx <- nc + 0.5
	topry <- 1.5 +(i-1)*1
	addRegion(im1) <- imRect(0.5, bly, toprx, topry, href=labRow[i])
    }
    createIM(im1, file = htmlname)
# **************************************************************************************************
    if (!invalid(na.color) & any(is.na(x))) {
        mmat <- ifelse(is.na(x), 1, NA)
        image(1:nc, 1:nr, mmat, axes = FALSE, xlab = "", ylab = "",
            col = na.color, add = TRUE)
    }
    axis(1, 1:nc, labels = labCol, las = 2, line = -0.5, tick = 0,
        cex.axis = cexCol)
    if (!is.null(xlab))
        mtext(xlab, side = 1, line = margins[1] - 1.25)
    axis(4, iy, labels = labRow, las = 2, line = -0.5, tick = 0,
        cex.axis = cexRow)
    if (!is.null(ylab))
        mtext(ylab, side = 4, line = margins[2] - 1.25)
    if (!missing(add.expr))
        eval(substitute(add.expr))
    if (!missing(colsep))
        for (csep in colsep) rect(xleft = csep + 0.5, ybottom = rep(0,
            length(csep)), xright = csep + 0.5 + sepwidth[1],
            ytop = rep(ncol(x) + 1, csep), lty = 1, lwd = 1,
            col = sepcolor, border = sepcolor)
    if (!missing(rowsep))
        for (rsep in rowsep) rect(xleft = 0, ybottom = (ncol(x) +
            1 - rsep) - 0.5, xright = ncol(x) + 1, ytop = (ncol(x) +
            1 - rsep) - 0.5 - sepwidth[2], lty = 1, lwd = 1,
            col = sepcolor, border = sepcolor)
    min.scale <- min(breaks)
    max.scale <- max(breaks)
    x.scaled <- scale01(t(x), min.scale, max.scale)
    if (trace %in% c("both", "column")) {
        for (i in colInd) {
            if (!is.null(vline)) {
                vline.vals <- scale01(vline, min.scale, max.scale)
                abline(v = i - 0.5 + vline.vals, col = linecol,
                  lty = 2)
            }
            xv <- rep(i, nrow(x.scaled)) + x.scaled[, i] - 0.5
            xv <- c(xv[1], xv)
            yv <- 1:length(xv) - 0.5
            lines(x = xv, y = yv, lwd = 1, col = tracecol, type = "s")
        }
    }
    if (trace %in% c("both", "row")) {
        for (i in rowInd) {
            if (!is.null(hline)) {
                hline.vals <- scale01(hline, min.scale, max.scale)
                abline(h = i + hline, col = linecol, lty = 2)
            }
            yv <- rep(i, ncol(x.scaled)) + x.scaled[i, ] - 0.5
            yv <- rev(c(yv[1], yv))
            xv <- length(yv):1 - 0.5
            lines(x = xv, y = yv, lwd = 1, col = tracecol, type = "s")
        }
    }
    if (!missing(cellnote))
        text(x = c(row(cellnote)), y = c(col(cellnote)), labels = c(cellnote),
            col = notecol, cex = notecex)
    par(mar = c(margins[1], 0, 0, 0))
    if (dendrogram %in% c("both", "row")) {
        plot(ddr, horiz = TRUE, axes = FALSE, yaxs = "i", leaflab = "none")
    }
    else plot.new()
    par(mar = c(0, 0, if (!is.null(main)) 5 else 0, margins[2]))
    if (dendrogram %in% c("both", "column")) {
        plot(ddc, axes = FALSE, xaxs = "i", leaflab = "none")
    }
    else plot.new()
    if (!is.null(main))
        title(main, cex.main = 1.5 * op[["cex.main"]])
    if (key) {
        par(mar = c(5, 4, 2, 1), cex = 0.75)
        if (symkey) {
            max.raw <- max(abs(x), na.rm = TRUE)
            min.raw <- -max.raw
        }
        else {
            min.raw <- min(x, na.rm = TRUE)
            max.raw <- max(x, na.rm = TRUE)
        }
        z <- seq(min.raw, max.raw, length = length(col))
        image(z = matrix(z, ncol = 1), col = col, breaks = breaks,
            xaxt = "n", yaxt = "n")
        par(usr = c(0, 1, 0, 1))
        lv <- pretty(breaks)
        xv <- scale01(as.numeric(lv), min.raw, max.raw)
        axis(1, at = xv, labels = lv)
        if (scale == "row")
            mtext(side = 1, "Row Z-Score", line = 2)
        else if (scale == "column")
            mtext(side = 1, "Column Z-Score", line = 2)
        else mtext(side = 1, "Value", line = 3)
        if (density.info == "density") {
            dens <- density(x, adjust = densadj, na.rm = TRUE)
            omit <- dens$x < min(breaks) | dens$x > max(breaks)
            dens$x <- dens$x[-omit]
            dens$y <- dens$y[-omit]
            dens$x <- scale01(dens$x, min.raw, max.raw)
            lines(dens$x, dens$y/max(dens$y) * 0.95, col = denscol,
                lwd = 1)
            axis(2, at = pretty(dens$y)/max(dens$y) * 0.95, pretty(dens$y))
            title("Color Key\nand Density Plot")
            par(cex = 0.5)
            mtext(side = 2, "Density", line = 2)
        }
        else if (density.info == "histogram") {
            h <- hist(x, plot = FALSE, breaks = breaks)
            hx <- scale01(breaks, min.raw, max.raw)
            hy <- c(h$counts, h$counts[length(h$counts)])
            lines(hx, hy/max(hy) * 0.95, lwd = 1, type = "s",
                col = denscol)
            axis(2, at = pretty(hy)/max(hy) * 0.95, pretty(hy))
            title("Color Key\nand Histogram")
            par(cex = 0.5)
            mtext(side = 2, "Count", line = 2)
        }
        else title("Color Key")
    }
    else plot.new()
    invisible(list(rowInd = rowInd, colInd = colInd))
}

# imagename<-"image_test"
# height<-900
# width<-900
# im1 <- imagemap(imagename, height = height, width = width)
# xdata <- scan("covarR", what = double(0), sep = "\t")
# num.cols.covariate <- count.fields("covarR", sep = "\t",quote = "",comment.char = "#",blank.lines.skip = TRUE)
# xdata <- matrix(xdata, nrow = length(num.cols.covariate), byrow = TRUE)
# 
# heatmap.2.ed(xdata, col=redgreen(75), scale="row",key=TRUE, symkey=FALSE, density.info="none", trace="none",im1=im1,htmlname="prueba_html2.html")
# 
# dev.off(im1$Device)


### My modifications (R.D.-U.)



results.file <- read.table("multest_parallel.res", header = TRUE, skip = 13, sep="\t", comment.char = "",quote="")
heatmapOpts  <- read.table("heatmapOpts", header = TRUE, sep = "\t")
#class.names  <- read.table("class_labels", header = FALSE, sep = "\t")
class.names <- scan("class_labels", sep = "\t", what = "char", strip.white = TRUE)
if(class.names[length(class.names)] == "") class.names <- class.names[-length(class.names)]

# Add FDR value to gene name
FDR.changed  <- round(results.file$FDR_indep,3)
FDR.changed[which(FDR.changed<0.001)] <- '<0.001'
#results.file$ID <- paste(results.file$ID,"(" ,results.file$FDR_indep,")",sep="")
results.file$ID <- paste(results.file$ID,"(" ,FDR.changed,")",sep="")


## testing
##save(file = "test.RData", results.file, heatmapOpts)
xdata <- scan("covarR", what = double(0), sep = "\t", quiet = TRUE)
num.cols.covariate <- count.fields("covarR", sep = "\t",
                                   quote = "",
                                   comment.char = "#",
                                   blank.lines.skip = TRUE)
xdata <- matrix(xdata, nrow = length(num.cols.covariate), byrow = TRUE)


rowsuse <- subset(results.file, (unadj.p < heatmapOpts$maxUnadjp) & (FDR_indep < heatmapOpts$maxFDR) &
                               (obs_stat > heatmapOpts$minObsrv) & (obs_stat < heatmapOpts$maxObsrv) &
			       (abs.obs_stat. > heatmapOpts$minAbsObsrv))

if(dim(rowsuse)[1] > heatmapOpts$maxGenes) {
		    rowsuse <- rowsuse[order(rowsuse$FDR_indep, rowsuse$unadj.p, -rowsuse$abs.obs_stat), ]
		    rowsuse <- rowsuse[1:heatmapOpts$maxGenes, c(1, 2)]
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
	imagename <- heatmapOpts$img_name

	if (heatmapOpts$Pixels=="auto"){
		height <- max(15 * nrow(x), 800)
		width  <- max(20 * ncol(x), 800)
		height <- width <- min(max(height, width), 1200)
	}
	else{
		height <- width <- heatmapOpts$Pixels
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
	if (heatmapOpts$Colour=="rg") {var_colour <- redgreen(75)}
        else if (heatmapOpts$Colour=="gr") {var_colour <- greenred(75)}
	else{var_colour <- topo.colors(75)}
	row.dendro <- as.dendrogram(hclust(as.dist(1 - cor(t(x),use="pairwise")), method = "complete"))

	heatmap.2.ed(x, labRow = genenames, labCol = class.names[neworder], col = var_colour, 
			scale = "none", key = TRUE, symkey= FALSE, density.info = "none", 
			trace = "none", im1 = im1, htmlname = htmlname, margins = c(4,20), 
			dendrogram = "row", Rowv = row.dendro, Colv = NULL)
##			dendrogram = "both", Rowv = row.dendro, Colv = col.dendro)
## To add a column dendrogram, use heatmap.2.ed with the above commented line, and doing
## a dendrogram for columns


       dev.off(im1$Device)

}

