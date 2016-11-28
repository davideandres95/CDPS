#!usr/bin/env python
import subprocess
import sys
import fileinput

name = sys.argv[1]
subprocess.call("sudo cp /etc/apache2/sites-available/000-default.conf  /etc/apache2/sites-available/"+name+".conf", shell=True)

def confServer():
	tempFile = open( '/etc/apache2/sites-available/"+name+".conf', 'r+' )
	textToSearch='DocumentRoot /var/www/html'
	textToReplace='DocumentRoot /var/www/'+name+'\n'+'ServerName '+name+'.cdps'+'\n'+ 'ServerAlias www.'+name+'.cdps'
	for line in fileinput.input( tempFile ):
    	tempFile.write( line.replace( textToSearch, textToReplace ) )
	tempFile.close()
	return

def initIndex():
	index = open('/var/www/'+name+'/index.html', 'r+')
	write('// Fichero index.html en'+name+'\n'+'<html>'+'\n'+'<h1> Servidor de'+name+'</h1>'+'\n'+'</html>')
	index.close()
	return

confServer();

#confiuguramos el nombre
confServer()
subprocess.call('sudo mkdir /var/www/'+name, shell=True)
initIndex()
#Aplicamos configuracion
subprocess.call('sudo a2ensite '+name+'.conf', shell=True)
subprocess.call('service apache2 reload', shell=True)	