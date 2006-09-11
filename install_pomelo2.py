#!/usr/bin/python
import os
f=open("file_names.txt");file_lines = f.readlines();f.close()
new_path = os.getcwd()
print "Application will now be installed in " + new_path + "\n"
new_URL  = raw_input("Please introduce new url, do not write slashes, http or www. \n")
for line in file_lines:
    line = line.strip()
    if line.find("url") != -1:
        replace_this = "pomelo2.bioinfo.cnio.es"
        replace_for  = new_URL
        print "\nChanging script urls"
    elif line.find("route") != -1:
        replace_this = "/http"
        replace_for  = new_path
        print "\nChanging script paths"
    else:
        print ".",
        # Read file text 
        f=open(line,"r");file_text = f.read();f.close()
        # Substitute string in text
        file_text = file_text.replace(replace_this, replace_for)
        # Write new text to old file
        f=open(line,"w");f.write(file_text);f.close()

        
print "------------------------------------------------------------------"
print "Pomelo2 files have been modified to run on your computer\n \
at the current location and with the selected URL. To be able to\n \
access the web application you must add this text to your httpd.conf\n \
file and restart apache: "
print "\n\n\n\n"
       
apache_text = """<VirtualHost url_name>

 ServerName url_name
 DocumentRoot \"file_route/pomelo2/www\"
 ErrorLog file_route/log/pomelo2_error.log
 TransferLog file_route/log/pomelo2_access.log

 ScriptAlias /cgi-bin \"file_route/pomelo2/cgi\"

 <Directory \"file_route/pomelo2/www\">
    Options -Indexes FollowSymLinks
    IndexOptions FancyIndexing NameWidth=*
    AllowOverride All
    Order allow,deny
    Allow from all
#    Options ExecCGI FollowSymLinks
    AddHandler cgi-script .cgi .py
    DirectoryIndex /index.html
 </Directory>
</VirtualHost>"""

apache_text = apache_text.replace("url_name",new_URL)
apache_text = apache_text.replace("file_route",new_path)
print apache_text
print "\n\n\n\n"
