#!/usr/bin/python
import cgi
import sys
form = cgi.FieldStorage()

new_table = form['file_name'].value
if new_table.index("html")==-1:
	sys.exit()
file=open(new_table)
text_map1=file.read()
file.close()
print "Content-type: text/html;charset=utf-8\r\n"
print text_map1