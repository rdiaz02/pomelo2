def covars_header_results(covar_filename, header_filename, results_filename):
	f     = open(covar_filename)
	lines = f.readlines()
	f.close()
	gene_names = []
	covar      = []
	for line in lines:
		
		#Esto lo acabo de meter
		line = line.replace("NA","nan")
		line = line.replace("\t\t","\tnan\t")
		parts = line.split("\t")
		#parts = line.split()
		gene_names.append(parts[0])
		covar.append(map(float, parts[1:]))
	
	f = open(header_filename)
	header_line = f.readline()
	f.close()
	header = header_line.split()
	
	f     = open(results_filename)
	lines = f.readlines()
	f.close()
	results_lines = lines[14:]
	result_row_id = []
	results = []
	for line in results_lines:
		parts = line.split("\t")
		#parts = line.split()
		result_row_id.append(int(parts[0])-1)
		#result_row_id.append(parts[0])
		results.append(map(float, parts[2:]))
	
	return covar, gene_names, header, results, result_row_id

def filter_covars(covar, gene_names, results, result_row_id, cgi_dict, def_max_genes):
	if ( cgi_dict.has_key("below_unadj-p") ):
		max_unadjp = float( cgi_dict["below_unadj-p"].value )
		results_loop = results[:]
		for row in results_loop:
			if row[0] >= max_unadjp:
				row_index = results.index(row)
				dummy1 = results.pop(row_index)
				dummy2 = result_row_id.pop(row_index)
	if ( cgi_dict.has_key("below_FDR") ):
		max_FDR = float( cgi_dict["below_FDR"].value )
		results_loop = results[:]
		for row in results_loop:
			if row[2] >= max_FDR:
				row_index = results.index(row)
				dummy1 = results.pop(row_index)
				dummy2 = result_row_id.pop(row_index)	
	if ( cgi_dict.has_key("above_abs_obs_stat") ):
		min_abs_obsrv = float( cgi_dict["above_abs_obs_stat"].value )
		results_loop  = results[:]
		for row in results_loop:
			if row[5] <= min_abs_obsrv:
				row_index = results.index(row)
				dummy1 = results.pop(row_index)
				dummy2 = result_row_id.pop(row_index)	
	if ( cgi_dict.has_key("above_obs_stat") ):
		min_obsrv = float( cgi_dict["above_obs_stat"].value )
		results_loop  = results[:]
		for row in results_loop:
			if row[4] <= min_obsrv:
				row_index = results.index(row)
				dummy1 = results.pop(row_index)
				dummy2 = result_row_id.pop(row_index)	
	if ( cgi_dict.has_key("below_obs_stat") ):
		max_obsrv = float( cgi_dict["below_obs_stat"].value )
		results_loop  = results[:]
		for row in results_loop:
			if row[4] >= max_obsrv:
				row_index = results.index(row)
				dummy1 = results.pop(row_index)
				dummy2 = result_row_id.pop(row_index)	
	max_genes = def_max_genes
	if ( cgi_dict.has_key("max_genes") ):
		max_genes    = int( cgi_dict["max_genes"].value )
		
	results_loop = results[:]
	dict         = {}
	FDR_array    = []
	for row, loop_row_ID in zip(results_loop, result_row_id):
		if dict.has_key(row [2]):
			dict[row [2]] = dict[row [2]] + [loop_row_ID]
		else:
			dict[row [2]] = [loop_row_ID]
			FDR_array.append(row [2])
	FDR_array.sort()
	FDR_array     = FDR_array[-1*max_genes:]
	result_row_id = []
	for FDR_loop in FDR_array:
		result_row_id = result_row_id + dict[FDR_loop]
		
	result_row_id = result_row_id[-1*max_genes:]
		
	filtered_covar      = []
	filtered_gene_names = []
	for row_num in result_row_id:
		filtered_covar.append(covar[row_num])
		filtered_gene_names.append(gene_names[row_num])

	return filtered_covar, filtered_gene_names

