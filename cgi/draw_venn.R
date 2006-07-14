library(limma)
library(GDD)
vennDiagram <- function (object, include = "both", names, col =col, mar = rep(1, 4), cex = 1.5,
    ...)
{
    if (!is(object, "VennCounts"))
        object <- vennCounts(object, include = include)
    nsets <- ncol(object) - 1
    if (nsets > 3)
        stop("Can't plot Venn diagram for more than 3 sets")
    if (missing(names))
        names <- colnames(object)[1:nsets]
    counts <- object[, "Counts"]
    theta <- 2 * pi * (1:360)/360
    xcentres <- list(0, c(-1, 1), c(-1, 1, 0))[[nsets]]
    ycentres <- list(0, c(0, 0), c(1/sqrt(3), 1/sqrt(3), -2/sqrt(3)))[[nsets]]
    r <- c(1.5, 1.5, 1.5)[nsets]
    xtext <- list(-1.2, c(-1.2, 1.2), c(-1.2, 1.2, 0))[[nsets]]
    ytext <- list(1.8, c(1.8, 1.8), c(2.4, 2.4, -3))[[nsets]]
    old.par <- par(mar = mar)
    on.exit(par(old.par))
    plot(x = 0, y = 0, type = "n", xlim = c(-4, 4), ylim = c(-4,
        4), xlab = "", ylab = "", axes = FALSE, ...)
    for (circle in 1:nsets) {
        lines(xcentres[circle] + r * cos(theta), ycentres[circle] +
            r * sin(theta))
        text(xtext[circle], ytext[circle], names[circle], cex = cex, col=col)
    }
    switch(nsets, {
        rect(-3, -2.5, 3, 2.5)
        text(2.3, -2.1, counts[1], cex = cex)
        text(0, 0, counts[2], cex = cex)
    }, {
        rect(-3, -2.5, 3, 2.5)
        text(2.3, -2.1, counts[1], cex = cex, col = 1)
        text(1.5, 0.1, counts[2], cex = cex, col = col)
        text(-1.5, 0.1, counts[3], cex = cex, col = col)
        text(0, 0.1, counts[4], cex = cex, col=col)
    }, {
        rect(-3, -3.5, 3, 3.3)
        text(2.5, -3, counts[1], cex = cex, col = 1)
        text(0, -1.7, counts[2], cex = cex, col = col)
        text(1.5, 1, counts[3], cex = cex, col = col)
        text(0.75, -0.35, counts[4], cex = cex, col = col)
        text(-1.5, 1, counts[5], cex = cex, col = col)
        text(-0.75, -0.35, counts[6], cex = cex, col = col)
        text(0, 0.9, counts[7], cex = cex, col = col)
        text(0, 0, counts[8], cex = cex, col = col)
    })
    invisible()
}

venn.table    <- read.table("venncontrsTable", header = TRUE, sep="\t")
venn.table    <- as.matrix(venn.table)
file.names    <- scan("vennNames", sep="\t",nlines = 1, what="character(0)")
columns.use   <- scan("vennNames", sep="\t",nlines = 1, skip = 1, what=integer(0))
names.compare <- scan("venncontrsTable", sep="\t",nlines = 1, what="character(0)")
names.compare <- names.compare[columns.use]
venn.table    <- venn.table[,columns.use]

GDD(file = file.names[1], w=370, h=320, type = "png", ps = 16)
vennDiagram(venn.table, names = names.compare, col = 1,cex=0.5, include="both")
dev.off()

diagram.names <-  sub(" vs "," > ",names.compare)
GDD(file = file.names[2], w=370, h=320, type = "png", ps = 16)
vennDiagram(venn.table,names = diagram.names, col="darkgreen",cex=0.5,include="up")
dev.off()

diagram.names <-  sub(" vs "," < ",names.compare)
GDD(file = file.names[3], w=370, h=320, type = "png", ps = 16)
vennDiagram(venn.table, names = diagram.names,col="red",cex=0.5,include="down")
dev.off()
