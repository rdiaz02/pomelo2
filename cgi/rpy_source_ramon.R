### Try GDD
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

heatmap2<-function (x, Rowv = NULL, Colv = if (symm) "Rowv" else NULL,
    distfun = dist, hclustfun = hclust, reorderfun = function(d,
        w) reorder(d, w), add.expr, symm = FALSE, revC = identical(Colv,
        "Rowv"), scale = c("row", "column", "none"), na.rm = TRUE,
    margins = c(5, 5), ColSideColors, RowSideColors, cexRow = 0.2 +
        1/log10(nr), cexCol = 0.2 + 1/log10(nc), labRow = NULL,
    labCol = NULL, main = NULL, xlab = NULL, ylab = NULL, keep.dendro = FALSE,
    verbose = getOption("verbose"), im1, htmlname, ...)
{
    scale <- if (symm && missing(scale))
        "none"
    else match.arg(scale)
    if (length(di <- dim(x)) != 2 || !is.numeric(x))
        stop("'x' must be a numeric matrix")
    nr <- di[1]
    nc <- di[2]
    if (nr <= 1 || nc <= 1)
        stop("'x' must have at least 2 rows and 2 columns")
    if (!is.numeric(margins) || length(margins) != 2)
        stop("'margins' must be a numeric vector of length 2")
    doRdend <- !identical(Rowv, NA)
    doCdend <- !identical(Colv, NA)
    if (is.null(Rowv))
        Rowv <- rowMeans(x, na.rm = na.rm)
    if (is.null(Colv))
        Colv <- colMeans(x, na.rm = na.rm)
    if (doRdend) {
        if (inherits(Rowv, "dendrogram"))
            ddr <- Rowv
        else {
            hcr <- hclustfun(distfun(x))
            ddr <- as.dendrogram(hcr)
            if (!is.logical(Rowv) || Rowv)
                ddr <- reorderfun(ddr, Rowv)
        }
        if (nr != length(rowInd <- order.dendrogram(ddr)))
            stop("row dendrogram ordering gave index of wrong length")
    }
    else rowInd <- 1:nr
    if (doCdend) {
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
                ddc <- reorderfun(ddc, Colv)
        }
        if (nc != length(colInd <- order.dendrogram(ddc)))
            stop("column dendrogram ordering gave index of wrong length")
    }
    else colInd <- 1:nc
    x <- x[rowInd, colInd]
    labRow <- if (is.null(labRow))
        if (is.null(rownames(x)))
            (1:nr)[rowInd]
        else rownames(x)
    else labRow[rowInd]
    labCol <- if (is.null(labCol))
        if (is.null(colnames(x)))
            (1:nc)[colInd]
        else colnames(x)
    else labCol[colInd]
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
    lmat <- rbind(c(NA, 3), 2:1)
    lwid <- c(if (doRdend) 1 else 0.05, 4)
    lhei <- c((if (doCdend) 1 else 0.05) + if (!is.null(main)) 0.2 else 0,
        4)
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
    if (verbose) {
        cat("layout: widths = ", lwid, ", heights = ", lhei,
            "; lmat=\n")
        print(lmat)
    }
    op <- par(no.readonly = TRUE)
    on.exit(par(op))
    layout(lmat, widths = lwid, heights = lhei, respect = TRUE)
    if (!missing(RowSideColors)) {
        par(mar = c(margins[1], 0, 0, 0.5))
        image(rbind(1:nr), col = RowSideColors[rowInd], axes = FALSE)
    }
    if (!missing(ColSideColors)) {
        par(mar = c(0.5, 0, 0, margins[2]))
        image(cbind(1:nc), col = ColSideColors[colInd], axes = FALSE)
    }
    par(mar = c(margins[1], 0, 0, margins[2]))
    if (!symm || scale != "none")
        x <- t(x)
    if (revC) {
        iy <- nr:1
        ddr <- rev(ddr)
        x <- x[, iy]
    }
    else iy <- 1:nr
    image(1:nc, 1:nr, x, xlim = 0.5 + c(0, nc), ylim = 0.5 +
        c(0, nr), axes = FALSE, xlab = "", ylab = "", ...)
    for(i in 1:nr) {
	bly <- 0.5+(i-1)*1
	toprx <- nc + 0.5
	topry <- 1.5 +(i-1)*1
	addRegion(im1) <- imRect(0.5, bly, toprx, topry, href=labRow[i])
    }
    createIM(im1, file = htmlname)

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
    par(mar = c(margins[1], 0, 0, 0))
    if (doRdend)
        plot(ddr, horiz = TRUE, axes = FALSE, yaxs = "i", leaflab = "none")
    else frame()
    par(mar = c(0, 0, if (!is.null(main)) 1 else 0, margins[2]))
    if (doCdend)
        plot(ddc, axes = FALSE, xaxs = "i", leaflab = "none")
    else if (!is.null(main))
        frame()
    if (!is.null(main))
        title(main, cex.main = 1.5 * op[["cex.main"]])
    invisible(list(rowInd = rowInd, colInd = colInd, Rowv = if (keep.dendro &&
        doRdend) ddr, Colv = if (keep.dendro && doCdend) ddc))
}

 
## heatimagemap<-function (x, genenames, classname, pixelheight, pixelwidth, htmlname,imagename)
## {
## 	im1 <- imagemap(imagename, height = pixelheight, width = pixelwidth)
## 	options(warn=2)
## 	try(classname<-as.numeric(classname),silent=TRUE)
## 	options(warn=0)
## 	neworder<-order(classname)
## 	classname <- classname[neworder]
## 	x <- x[,neworder]
## 	row.dendro <- as.dendrogram(hclust(as.dist(1 - cor(t(x),use="pairwise")), method = "complete"))
## 	heatmap2(x, labRow=genenames, labCol=classname, col = topo.colors(50), im1=im1,htmlname=htmlname, margins=c(5,15),Colv=NA,Rowv=row.dendro)
## 	dev.off(im1$Device)
## }

### My modifications (R.D.-U.)



system("sed  '14 s/\t\t/\t/' multest_parallel.res > m1.res")
#results.file <- read.table("multest_parallel.res", header = TRUE, skip = 13)
results.file <- read.table("m1.res", header = TRUE, skip = 13, sep = "\t")
heatmapOpts <- read.table("heatmapOpts", header = TRUE, sep = "\t")

## testing
##save(file = "test.RData", results.file, heatmapOpts)
xdata <- scan("covarR", what = double(0), sep = "\t")
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

     tmp <- try(system('rm NoImagemapPossible'))
     x <- xdata[rowsuse[, 1], ]
     rownames(x) <- as.character(rowsuse$ID)
    genenames <- as.character(rowsuse$ID)

     heatimagemap<-function (classname, pixelheight, pixelwidth, htmlname, imagename)
     {    		       

    height <- max(15 * nrow(x), 800)
    width <- max(20 * ncol(x), 800)
    height <- width <- min(max(height, width), 1200)
	im1 <- imagemap(imagename, height = height, width = width)
	options(warn=2)
	try(classname<-as.numeric(classname),silent=TRUE)
	options(warn=0)
	neworder<-order(classname)
	classname <- classname[neworder]
	x <- x[,neworder]
	row.dendro <- as.dendrogram(hclust(as.dist(1 - cor(t(x),use="pairwise")), method = "complete"))
	heatmap2(x, labRow=genenames, labCol=classname, col = topo.colors(50),
                 im1=im1,htmlname=htmlname,
                 margins=c(5,15),
                 Colv=NA,Rowv=row.dendro)
	dev.off(im1$Device)
}
}
