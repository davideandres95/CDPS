#!usr/bin/env python
import sys
import fileinput
import subprocess

subprocess.call("sudo mkdir /var/www/dom1", shell=True)

def initIndex():
	test = open('/var/www/dom1/index.html', 'a+')
	write('// Fichero index.html en dom1'+'\n'+'<html>'+'\n'+'<h1> Primer servidor </h1>'+'\n'+'</html>')
	test.close()
	return

initIndex()
