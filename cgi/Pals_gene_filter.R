# Read results file and 
results.file <- read.table("multest_parallel.res", header = TRUE, skip = 13, sep="\t", quote="")
PalsOpts  <- read.table("Pals_Opts", header = TRUE, sep = "\t")
rowsuse <- subset(results.file,(unadj.p < PalsOpts$maxUnadjp) & (FDR_indep < PalsOpts$maxFDR) &
                               (obs_stat > PalsOpts$minObsrv) & (obs_stat < PalsOpts$maxObsrv) &
			       (abs.obs_stat. > PalsOpts$minAbsObsrv))
if (dim(rowsuse)[1]<1){
  sink("gene.list.txt")
  cat("No genes coincide with the parameters you have chosen.<br> Please select less restrictive parameters.")
  sink()
}else{
  genenames <- as.character(rowsuse$ID)
  write.table( genenames, 'gene.list.txt'   , quote     = FALSE,
               sep='\n' ,  col.names = FALSE, row.names = FALSE)
}
