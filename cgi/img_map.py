import cgitb;cgitb.enable()

def id_converter_lite_link (geneName, idtype, organism):
    return "#"

# This is the old one, but we are not longer using idclight    
# def id_converter_lite_link (geneName, idtype, organism):
# 	if idtype == 'None' or organism == 'None':
# # 		return geneName
# 		return "#"
# 	else:
# 		geneName = geneName.split("(")[0].strip()
# 		return ''.join(['https://idclight.bioinfo.cnio.es/IDClight.prog?idtype=', idtype, '&id=', geneName, '&internal=0&org=', organism,'" target="icl_window'])

def change_image (file_name, last_pixel, idtype, organism):
	# Read html file
	file       = open(file_name)
	text_lines = file.readlines()
	file.close()
	# Pixel that indicates where the image map will finish (depends on image size)
	# last_pixel = "690"
	last_pixel=str(last_pixel)
# 	idtype = "cnio"
# 	organism = "hs"
	# Loop over html lines
	for line in text_lines:
		# Try to find coords in the line and if not continue to next line
		try:
			# Get interval that contains the actual coords 
			fst_quote  = line.index("coords=") + 8
			scnd_quote = line.index("\"",fst_quote)
			aux_coord  = line[fst_quote:scnd_quote]
			
			# Split the coords, reoder and correct them
			coord_old  = aux_coord.split(",")
			#coord_new  = coord_old[2] + "," + coord_old[1] + "," + last_pixel + "," + coord_old[3]
			coord_new  = coord_old[0] + "," + coord_old[1] + "," + last_pixel + "," + coord_old[3]			

			# Define new line with the new coords
			new_line   = line[:fst_quote] + coord_new + line[scnd_quote:]
			
			# Get interval that contains the actual link 
			fst_quote      = new_line.index( "href=" ) + 6
			scnd_quote     = new_line.index( "\"", fst_quote )
			
			aux_gene_name  = new_line[fst_quote:scnd_quote]
			bracket_index  = aux_gene_name.find(" ")
			gene_name      = aux_gene_name[:bracket_index]
			
			# Define new line with the new link
			id_link    = id_converter_lite_link(gene_name, idtype, organism)
			new_line   = new_line[:fst_quote] + id_link + "\" title=\"" + aux_gene_name + new_line[scnd_quote:]
			# new_line   = new_line[:fst_quote+1] + "Subst" + gene_name + new_line[scnd_quote:]
			# Find line to substitute in text and substitute it with new line
			line_index = text_lines.index(line)
			text_lines[line_index] = new_line
		except ValueError:
			pass
		
	# Open new html file and print contents of modified html
	file=open("heat_new.html","w")
	file.writelines(text_lines)
	file.close()
