#!usr/bin/env python
import subprocess
import sys
import fileinput



def confNet():
	tempFile = open( '/etc/network/interfaces', 'r+' )
	textToSearch='iface eth0 inet dhcp'
	textToReplace = 'iface eth0 inet static'+'\n'+'address 192.168.122.241'+'\n'+'netmask 255.255.255.0'+'\n'+'gateway 192.168.122.1'+'\n'+'dns-nameservers 192.168.122.1'
	for line in fileinput.input( tempFile ):
    	tempFile.write( line.replace( textToSearch, textToReplace ) )
	tempFile.close()
	return

def confServer():
	tempFile = open( '/etc/apache2/sites-available/dominio1.conf', 'r+' )
	textToSearch='DocumentRoot /var/www/html'
	textToReplace='DocumentRoot /var/www/dom1'+'\n'+'ServerName dominio1.cdps'+'\n'+ 'ServerAlias www. dominio1.cdps'
	for line in fileinput.input( tempFile ):
    	tempFile.write( line.replace( textToSearch, textToReplace ) )
	tempFile.close()
	return

def initIndex():
	index = open('/var/www/dom1/index.html', 'r+')
	write('// Fichero index.html en dom1'+'\n'+'<html>'+'\n'+'<h1> Primer servidor </h1>'+'\n'+'</html>')
	index.close()
	return

confNet()
#Instalamos el entorno
subprocess.call("sudo apt-get update", shell=True)
subprocess.call("sudo apt-get install apache2", shell=True)
subprocess.call("sudo apt-get install lynx", shell=True)
subprocess.call("sudo apt-get install wget", shell=True)
subprocess.call("sudo apt-get install curl", shell=True)
#Hacemos una copia de seguridad
subprocess.call("sudo cp /etc/apache2/sites-available/000-default.conf  /etc/apache2/sites-available/dominio1.conf", shell=True)
#confiuguramos el nombre
confServer()
subprocess.call("sudo mkdir /var/www/dom1", shell=True)
initIndex()
#Aplicamos configuracion
subprocess.call("sudo a2ensite dominio1.conf", shell=True)
subprocess.call("service apache2 reload", shell=True)