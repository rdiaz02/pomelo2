def write_to_file(cgi_dict, imagename):
    """Write the cgi_dict values to be read by R later"""
    ## First define a set of predefined values. Will overwrite with
    ## stuff from the cgi, o.w. write those to the file
    
    maxUnadjp   = 0.05
    maxFDR      = 0.15
    minAbsObsrv = 0.0
    minObsrv    = -9999999999999
    maxObsrv    = 9999999999999
    maxGenes    = 50
    size        = "auto"
    var_colour  = "gr"

    if ( cgi_dict.has_key("below_unadj-p") ):
	maxUnadjp = float( cgi_dict["below_unadj-p"].value )
    if ( cgi_dict.has_key("below_FDR") ):
	maxFDR = float( cgi_dict["below_FDR"].value )
    if ( cgi_dict.has_key("above_abs_obs_stat") ):
	minAbsObsrv = float( cgi_dict["above_abs_obs_stat"].value )
    if ( cgi_dict.has_key("above_obs_stat") ):
	minObsrv = float( cgi_dict["above_obs_stat"].value )
    if ( cgi_dict.has_key("below_obs_stat") ):
	maxObsrv = float( cgi_dict["below_obs_stat"].value )
    if ( cgi_dict.has_key("max_genes") ):
	maxGenes    = int( cgi_dict["max_genes"].value )
    if ( cgi_dict.has_key("colour") ):
	var_colour  = cgi_dict["colour"].value
    if ( cgi_dict.has_key("pixels") ):
	size        = cgi_dict["pixels"].value
    
    heatmapOpts = open('heatmapOpts', mode = 'w')
    heatmapOpts.write('maxUnadjp\tmaxFDR\tminAbsObsrv\tminObsrv\tmaxObsrv\tmaxGenes\tPixels\tColour\timg_name\n')
    heatmapOpts.write(''.join([str(maxUnadjp), '\t', str(maxFDR), '\t',
                               str(minAbsObsrv), '\t', str(minObsrv), '\t',
			       str(maxObsrv), '\t', str(maxGenes),'\t',
			       size,'\t',var_colour,'\t',imagename,'\n']))
    heatmapOpts.close()
