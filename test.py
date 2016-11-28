#!usr/bin/env python
import subprocess
import sys
import fileinput

def test():
	tempFile = open( 'test.txt', 'r+' )
	textToSearch='AQUI VA LA PRUEBA'
	textToReplace='ServerName dominio1.cdps'+'\n'+ 'ServerAlias www. dominio1.cdps'
	for line in fileinput.input():
    		tempFile.write( line.replace( textToSearch, textToReplace ) )
	tempFile.close()
	return
test()

