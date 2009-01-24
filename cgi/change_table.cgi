#!/usr/bin/python
import cgi
import sys
form = cgi.FieldStorage()

### I add a try, to preven KeyError exceptions
try:
	new_table = form['file_name'].value
except:
	sys.exit()
	
## I think the following is wrong. Index will throw an exception
##if new_table.index("html")==-1:
if new_table.find("html") == -1:
	sys.exit()
file=open(new_table)
text_map1=file.read()
file.close()
print "Content-type: text/html;charset=utf-8\r\n"
print text_map1
