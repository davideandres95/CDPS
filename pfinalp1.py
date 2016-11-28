#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import os
import sys
import subprocess
from lxml import etree
from subprocess import Popen

# Definición de funciones
def create(name1, name2):
	os.system('qemu-img create -f qcow2 -b cdps-vm-base-p3.qcow2 '+name1+'.qcow2')
	os.system('cp plantilla-vm-p3.xml '+name1+'.xml')
	tree = etree.parse('/mnt/tmp/pfinal/'+name1+'.xml')
	root = tree.getroot()
	doc = etree.ElementTree(root)
	name = root.find("name")
	source = root.find("./devices/disk/source")
	interface = root.find("./devices/interface/source")
	name.text = name2
	source.set("file", "/mnt/tmp/pfinal/"+name1+".qcow2")
	if name1 == 'c1':
		interface.set("bridge", "LAN1")
	elif name1 == 'lb':
		interface.set("bridge", "LAN1")
		interface2 = root.find("devices")
		writeinterface2 = etree.SubElement(interface2, 'interface', type='bridge')
		writesource2 = etree.SubElement(writeinterface2, 'source', bridge='LAN2')
		writemodel2 = etree.SubElement(writesource2, 'model', type='virtio')
	else:
		interface.set("bridge", "LAN2")
	outFile = open(name1+'.xml', 'w')
	doc.write(outFile)
def start(mv, name1, name2):
	if name1 != 'host':
		os.chdir("/mnt/tmp/pfinal")
		os.system('sudo vnx_mount_rootfs -s -r '+name1+'.qcow2 mnt')
		hostname = name2
		os.chdir("/mnt/tmp/pfinal/mnt/etc")
		dochostname = open("hostname", "w")
		dochostname.write(hostname)
		dochostname.close()
		hosts(hostname)
		os.chdir("/mnt/tmp/pfinal/mnt/etc/network")
		interface(mv)
		os.chdir("/mnt/tmp/pfinal")
		os.system('sudo vnx_mount_rootfs -u mnt')
		if subprocess.call(["sudo","virsh","create",name1+".xml"]) != 0:
			os.chdir("/mnt/tmp/pfinal")
			os.system('sudo virsh create '+name1+'.xml')
			terminal = "sudo virsh console "+name2
			p1 = Popen(['xterm', '-e', terminal])
	else:
		os.system("sudo ifconfig LAN1 10.0.1.3/24")
		os.system("sudo ip route add 10.0.0.0/16 via 10.0.1.1")
def stop(name2):
	os.system('sudo virsh shutdown '+name2)
def stopd(name2):
	os.system('sudo virsh destroy '+name2)
def destroy(name1):
	os.system('rm '+name1+'.qcow2 -f')
	os.system('rm '+name1+'.xml -f')
def monitor():
	mvs = [0,0,0,0,0,0,0,0]
	monitor = 0
	print "\nMONITORIZACIÓN DEL ESCENARIO: información sobre las MVs\n"
	print "="*55
	print "Estado de las MVs:"
	print "="*55
	for i in range(5+1):
		if i != 0:
			if escenario('s'+str(i),'S'+str(i)):
				mvs[i]=1
	if escenario('c1','C1'):
		mvs[6]=1
	if escenario('lb','LB'):
		mvs[7]=1
	print "\n"
	for i in range(7+1):
		if mvs[i] == 1:
			monitor = 1
	if monitor == 1: # Hay mvs arrancadas para obtener su información
		for i in range(5+1):
			if i != 0 and mvs[i] == 1:
				print "*"*55+"\n"
				print "Información sobre la máquina virtual S"+str(i)+":\n"
				print "="*55
				print "Domstate:"
				print "="*55+"\n"
				os.system('sudo virsh domstate S'+str(i))
				print "="*55
				print "Dominfo:"
				print "="*55+"\n"
				os.system('sudo virsh dominfo S'+str(i))
				print "="*55
				print "Cpu-Stats:"
				print "="*55+"\n"
				os.system('sudo virsh cpu-stats S'+str(i))
		if mvs[6] == 1:
			print "*"*55+"\n"
			print "Información sobre la máquina virtual C1:\n"
			print "="*55
			print "Domstate:"
			print "="*55+"\n"
			os.system('sudo virsh domstate C1')
			print "="*55
			print "Dominfo:"
			print "="*55+"\n"
			os.system('sudo virsh dominfo C1')
			print "="*55
			print "Cpu-Stats:"
			print "="*55+"\n"
			os.system('sudo virsh cpu-stats C1')
		if mvs[7] == 1:
			print "*"*55+"\n"
			print "Información sobre la máquina virtual LB:\n"
			print "="*55
			print "Domstate:"
			print "="*55+"\n"
			os.system('sudo virsh domstate LB')
			print "="*55
			print "Dominfo:"
			print "="*55+"\n"
			os.system('sudo virsh dominfo LB')
			print "="*55
			print "Cpu-Stats:"
			print "="*55+"\n"
			os.system('sudo virsh cpu-stats LB')
def escenario(name, hostname):
	print "\n"
	if arrancada(name, hostname) == 1:
		print "Máquina virtual "+hostname+" está arrancada"
		return 1
	elif creada (name, hostname) == 1:
		print "Máquina virtual "+hostname+" está creada pero no está arrancada"
		return 0
	else:
		print "Máquina virtual "+hostname+" no está creada"
		return 0
	print "\n"
def arrancada(name, hostname):
	if os.system("sudo virsh list | grep -q "+hostname) == 0:
		return 1
	else:
		return 0
def creada(name, hostname):
	if os.path.exists("/mnt/tmp/pfinal/"+name+".qcow2"):
		return 1
	else:
		return 0
def hosts(hostname):
	dochosts = open("hosts", "w")
	dochosts.write("127.0.0.1	localhost"+"\n")
	dochosts.close()
	dochosts = open("hosts", "a")
	dochosts.write("127.0.1.1	"+hostname+"\n")
	dochosts.write("# The following lines are desirable for IPv6 capable hosts"+"\n")
	dochosts.write("::1     localhost ip6-localhost ip6-loopback"+"\n")
	dochosts.write("ff02::1 ip6-allnodes"+"\n")
	dochosts.write("ff02::2 ip6-allrouters")
	dochosts.close()
def interface(mv):
	if  (mv >= 1 and mv <= 5):
		docinterface = open("interfaces", "w")
		docinterface.write("# The loopback network interface"+"\n")
		docinterface.close()
		docinterface2 = open("interfaces", "a")
		docinterface2.write("auto lo"+"\n")
		docinterface2.write("iface lo inet loopback"+"\n")
		docinterface2.write("# The primary network interface"+"\n")
		docinterface2.write("auto eth0"+"\n")
		docinterface2.write("iface eth0 inet static"+"\n")
		docinterface2.write("address 10.0.2.1"+str(mv)+"\n")
		docinterface2.write("netmask 255.255.255.0"+"\n")
		docinterface2.write("network 10.0.2.0"+"\n")
		docinterface2.write("broadcast 10.0.2.255"+"\n")
		docinterface2.write("gateway 10.0.2.1"+"\n")
		docinterface2.close()
	elif mv == 6:
		docinterface = open("interfaces", "w")
		docinterface.write("# The loopback network interface"+"\n")
		docinterface.close()
		docinterface2 = open("interfaces", "a")
		docinterface2.write("auto lo"+"\n")
		docinterface2.write("iface lo inet loopback"+"\n")
		docinterface2.write("# The primary network interface"+"\n")
		docinterface2.write("auto eth0"+"\n")
		docinterface2.write("iface eth0 inet static"+"\n")
		docinterface2.write("address 10.0.1.2"+"\n")
		docinterface2.write("netmask 255.255.255.0"+"\n")
		docinterface2.write("network 10.0.1.0"+"\n")
		docinterface2.write("broadcast 10.0.1.255"+"\n")
		docinterface2.write("gateway 10.0.1.1"+"\n")
		docinterface2.close()
	elif mv == 7:
		docinterface = open("interfaces", "w")
		docinterface.write("# The loopback network interface"+"\n")
		docinterface.close()
		docinterface2 = open("interfaces", "a")
		docinterface2.write("auto lo"+"\n")
		docinterface2.write("iface lo inet loopback"+"\n")
		docinterface2.write("# The primary network interface"+"\n")
		docinterface2.write("auto eth0"+"\n")
		docinterface2.write("iface eth0 inet static"+"\n")
		docinterface2.write("address 10.0.1.1"+"\n")
		docinterface2.write("netmask 255.255.255.0"+"\n")
		docinterface2.write("network 10.0.1.0"+"\n")
		docinterface2.write("broadcast 10.0.1.255"+"\n")
		docinterface2.write("gateway 10.0.1.1"+"\n")
		docinterface2.write("# The secundary network interface"+"\n")
		docinterface2.write("auto eth1"+"\n")
		docinterface2.write("iface eth1 inet static"+"\n")
		docinterface2.write("address 10.0.2.1"+"\n")
		docinterface2.write("netmask 255.255.255.0"+"\n")
		docinterface2.write("network 10.0.2.0"+"\n")
		docinterface2.write("broadcast 10.0.2.255"+"\n")
		docinterface2.write("gateway 10.0.2.1"+"\n")
		docinterface2.close()
		os.system("sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /mnt/tmp/pfinal/mnt/etc/sysctl.conf")
	else:
		print "Solamente se pueden arrancar 7 máquinas virtuales como máximo"

# Comienzo del desarrollo
if len(sys.argv) >= 2:
	orden = sys.argv[1]
	if orden == "create":
		if len(sys.argv) == 3:
			try:
				nservsweb = int(sys.argv[2])
				os.chdir("/mnt/tmp/pfinal")
				if nservsweb >= 1 and nservsweb <= 5:
					first = 1
					# Crear los sistemas de ficheros COW que utilizará cada una de las MVs del escenario
					# Crear los ficheros XML de especificación de cada MV partiendo de la plantilla
					# Editar los ficheros XML (utilizar lxml)
					for i in range(nservsweb+1):
						if i != 0:
							if creada('s'+str(i),'S'+str(i)) == 0:
								print "Se crea la máquina S"+str(i)
								create('s'+str(i),'S'+str(i))
							else:
								first = 0
								tecla = raw_input("La máquina S"+str(i)+" ya estaba creada. ¿Desea sobreescribir? (y/n)")
								if tecla == "y":
									print "Se va a sobreescribir sobre la máquina S"+str(i)
									create('s'+str(i),'S'+str(i))
								else:
									print "Se mantiene la máquina S"+str(i)+" creada"
					if creada('c1','C1') == 0:
						print "Se crea la máquina C1"
						create('c1','C1')
					else:
						first = 0
						tecla = raw_input("La máquina C1 ya estaba creada. ¿Desea sobreescribir? (y/n)")
						if tecla == "y":
							print "Se va a sobreescribir sobre la máquina C1"
							create('c1','C1')
						else:
							print "Se mantiene la máquina C1 creada"
					if creada('lb','LB') == 0:
						print "Se crea el balanceador LB"
						create('lb','LB')
					else:
						first = 0
						tecla = raw_input("El balanceador LB ya estaba creado. ¿Desea sobreescribir? (y/n)")
						if tecla == "y":
							print "Se va a sobreescribir sobre el balanceador LB"
							create('lb','LB')
						else:
							print "Se mantiene el balanceador LB creado"
					# Crear los bridges correspondientes a las dos redes virtuales
					if first == 1:
						os.system('sudo brctl addbr LAN1')
						os.system('sudo brctl addbr LAN2')
						os.system('sudo ifconfig LAN1 up')
						os.system('sudo ifconfig LAN2 up')
				else:
		        		print "Para poder crear los ficheros .qcow2 y xml de cada MV el número de servidores web debe estar entre 1 y 5"
			except ValueError:
				print "Para poder crear los ficheros .qcow2 y xml de cada MV el número de servidores web debe estar entre 1 y 5"
		else:
           		print "Para poder crear los ficheros .qcow2 y xml de cada MV se necesita un tercer parámetro que indique el número de servidores web a configurar"
	elif orden == "start":
	    	if len(sys.argv) == 3:
			try:
		    		nservsweb = int(sys.argv[2])
				os.chdir("/mnt/tmp/pfinal")
				if not os.path.exists("mnt"):
					os.system('mkdir mnt')
		    		# Arrancar el gestor de MVs para monitorizar el arranque de las mismas
		    		os.system('HOME=/mnt/tmp sudo virt-manager')
				# MEJORA DE CONFIGURACIÓN
				# Antes de arrancar cada MV se monta su sistema de ficheros en un directorio del host para poder modificarlo directamente desde el host
				# Configurar cada MV modificando los ficheros /etc/hostname (nombre) y /etc/network/interfaces
				# Terminadas las modificaciones, se debe desmontar la imagen de la MV con 'sudo vnx_mount_rootfs -u mnt'
		    		# Arrancar las MVs utilizando el comando virsh y mostrar las consolas textuales de las MVs del escenario
		    		# Arrancar las MVs utilizando el comando virsh y mostrar las consolas textuales de las MVs del escenario
		    		if nservsweb >= 1 and nservsweb <= 5:
					for i in range(nservsweb+1):
						if i == 0:
							start(0,'host','HOST')
						if i != 0:
							if creada('s'+str(i),'S'+str(i)) == 1 and arrancada('s'+str(i),'S'+str(i)) == 0:
								start(i,'s'+str(i),'S'+str(i))
							else:
								if arrancada('s'+str(i),'S'+str(i)) == 1:
									print "La máquina S"+str(i)+" ya estaba arrancada"
								else:
									print "La máquina S"+str(i)+" no está creada; no intente arrancar más máquinas de las que se hayan creado previamente con la orden create"
					if arrancada('c1','C1') == 0:
						start(6,'c1','C1')
					else:
						print "La máquina C1 ya estaba arrancada"
					if arrancada('lb','LB') == 0:
						start(7,'lb','LB')
					else:
						print "El balanceador LB ya estaba arrancado"
				else:
					print "Para poder arrancar las MVs el número de servidores web debe estar entre 1 y 5"
			except ValueError:
				print "Para poder arrancar las MVs el número de servidores web debe estar entre 1 y 5"
	    	else:
			print "Para arrancar las MVs y mostrar su consola se necesita un tercer parámetro que indique el número de servidores web a arrancar (el LB y el C1 se arrancarán también además de los servidores deseados)"
	elif orden == "stop":
	    	if len(sys.argv) == 3:
			try:
		    		nservsweb = int(sys.argv[2])
				os.chdir("/mnt/tmp/pfinal")
		    		# Detener las MVs parándolas de forma ordenada
				if nservsweb >= 1 and nservsweb <= 5:
					n = 1
					tecla = raw_input("¿Desea parar también el balanceador de tráfico y la máquina de cliente? (y/n) ")
					if tecla == "y":
						for i in range(5+1):
							if i != 0 and n <= nservsweb:
								if arrancada('s'+str(i),'S'+str(i)) == 1:
									stop('S'+str(i))
									n = n + 1
								else:
									print "La máquina S"+str(i)+" no estaba arrancada"
						if arrancada('c1','C1') == 1:
							stop('C1')
						else:
							print "La máquina C1 no estaba arrancada"
						if arrancada('lb','LB') == 1:
							stop('LB')
						else:
							print "El balanceador LB no estaba arrancado"
					elif tecla == "n":
						for i in range(5+1):
							if i != 0 and n <= nservsweb:
								if arrancada('s'+str(i),'S'+str(i)) == 1:
									stop('S'+str(i))
									n = n + 1
								else:
									print "La máquina S"+str(i)+" no estaba arrancada"
				else:
					print "Para poder parar las MVs el número de servidores web debe estar entre 1 y 5"
			except ValueError:
				print "Para poder parar las MVs el número de servidores web debe estar entre 1 y 5"
	    	elif len(sys.argv) == 4:
			try:
		    		nservsweb = int(sys.argv[2])
				os.chdir("/mnt/tmp/pfinal")
		    		# Parámetro adicional para parar las MVs de forma destructiva
		    		if sys.argv[3] == "-d":
					if nservsweb >= 1 and nservsweb <= 5:
						n = 1
						tecla = raw_input("¿Desea destruir también el balanceador de tráfico y la máquina de cliente? (y/n) ")
						if tecla == "y":
							for i in range(5+1):
								if i != 0 and n <= nservsweb:
									if arrancada('s'+str(i),'S'+str(i)) == 1:
										stopd('S'+str(i))
										n = n + 1
									else:
										print "La máquina S"+str(i)+" no estaba arrancada"
							if arrancada('c1','C1') == 1:
								stopd('C1')
							else:
								print "La máquina C1 no estaba arrancada"
							if arrancada('lb','LB') == 1:
								stopd('LB')
							else:
								print "El balanceador LB no estaba arrancado"
						elif tecla == "n":
							for i in range(5+1):
								if i != 0 and n <= nservsweb:
									if arrancada('s'+str(i),'S'+str(i)) == 1:
										stopd('S'+str(i))
										n = n + 1
									else:
										print "La máquina S"+str(i)+" no estaba arrancada"
					else:
						print "Para poder parar las MVs el número de servidores web debe estar entre 1 y 5"
				else:
		    			print "Para parar las MVs se necesita un tercer parámetro que indique el número de servidores web a parar y opcionalmente el parámetro -d para pararlas de forma destructiva"
			except ValueError:
				print "Para poder parar las MVs el número de servidores web debe estar entre 1 y 5"
		else:
			print "Para parar las MVs se necesita un tercer parámetro que indique el número de servidores web a parar y opcionalmente el parámetro -d para pararlas de forma destructiva"
	elif orden == "destroy":
    		if len(sys.argv) == 3:
			try:
	    			nservsweb = int(sys.argv[2])
				os.chdir("/mnt/tmp/pfinal")
	    			# Eliminar todos los ficheros
				if nservsweb >= 1 and nservsweb <= 5:
					n = 1
					tecla = raw_input("¿Desea eliminar también el balanceador de tráfico y la máquina de cliente? (y/n) ")
					if tecla == "y":
						for i in range(5+1):
							if i != 0 and n <= nservsweb:
								if creada('s'+str(i),'S'+str(i)) == 1 and arrancada('s'+str(i),'S'+str(i)) == 0:
									print "Se han borrado los archivos de la máquina S"+str(i)
									destroy('s'+str(i))
									n = n + 1
								elif creada('s'+str(i),'S'+str(i)) == 1 and arrancada('s'+str(i),'S'+str(i)) == 1:
									tecla = raw_input("La máquina S"+str(i)+" sigue ejecutándose, ¿desea eliminar los ficheros de la máquina igualmente? (y/n) ")
									if tecla == "y":
										print "Se han borrado los archivos de la máquina S"+str(i)
										destroy('s'+str(i))
									n = n + 1 # No eliminar la siguiente MV en su lugar
								else:
									print "La máquina S"+str(i)+" no estaba creada"
						if creada('c1','C1') == 1 and arrancada('c1','C1') == 0:
							print "Se han borrado los archivos de la máquina C1"
							destroy('c1')
						elif creada('c1','C1') == 1 and arrancada('c1','C1') == 1:
							tecla = raw_input("La máquina C1 sigue ejecutándose, ¿desea eliminar los ficheros de la máquina igualmente? (y/n) ")
							if tecla == "y":
								print "Se han borrado los archivos de la máquina C1"
								destroy('c1')
						else:
							print "La máquina C1 no estaba creada"
						if creada('lb','LB') == 1 and arrancada('lb','LB') == 0:
							print "Se han borrado los archivos del balanceador LB"
							destroy('lb')
						elif creada('lb','LB') == 1 and arrancada('lb','LB') == 1:
							tecla = raw_input("La máquina LB sigue ejecutándose, ¿desea eliminar los ficheros de la máquina igualmente? (y/n) ")
							if tecla == "y":
								print "Se han borrado los archivos del balanceador LB"
								destroy('lb')
						else:
							print "El balanceador LB no estaba creado"
					elif tecla == "n":
						for i in range(5+1):
							if i != 0 and n <= nservsweb:
								if creada('s'+str(i),'S'+str(i)) == 1 and arrancada('s'+str(i),'S'+str(i)) == 0:
									print "Se han borrado los archivos de la máquina S"+str(i)
									destroy('s'+str(i))
									n = n + 1
								elif creada('s'+str(i),'S'+str(i)) == 1 and arrancada('s'+str(i),'S'+str(i)) == 1:
									tecla = raw_input("La máquina S"+str(i)+" sigue ejecutándose, ¿desea eliminar los ficheros de la máquina igualmente? (y/n) ")
									if tecla == "y":
										print "Se han borrado los archivos de la máquina S"+str(i)
										destroy('s'+str(i))
									n = n + 1 # No eliminar la siguiente MV en su lugar
								else:
									print "La máquina S"+str(i)+" no estaba creada"
				else:
					print "Para poder destruir las MVs el número de servidores web debe estar entre 1 y 5"
			except ValueError:
				print "Para poder destruir las MVs el número de servidores web debe estar entre 1 y 5"
    		else:
        		print "Para liberar el escenario y borrar todos los ficheros creados se necesita el párametro de la orden (destroy) y un tercer parámetro que indique el número de servidores web a destruir"
	# MEJORA DE MONITORIZACIÓN DEL ESCENARIO
	elif orden == "monitor":
		if len(sys.argv) == 2:
			os.chdir("/mnt/tmp/pfinal")
			monitor()
			"""
			dominfo domain
				   Returns basic information about the domain.
			domstate domain [--reason]
				   Returns state about a domain.  --reason tells virsh to also print
				   reason for the state.
			cpu-stats domain [--total] [start] [count]
				   Provide cpu statistics information of a domain. The domain should
				   be running. Default it shows stats for all CPUs, and a total. Use
				   --total for only the total stats, start for only the per-cpu stats
				   of the CPUs from start, count for only count CPUs' stats.
			"""
		else:
        		print "Para obtener información de las MVs del escenario solo se necesita el párametro de la orden (monitor)"
	# MEJORA DE PRUEBA DE CONECTIVIDAD DEL HOST CON LOS SERVIDORES ARRANCADOS
	elif orden == "conectividad":
		if len(sys.argv) == 2:
			os.chdir("/mnt/tmp/pfinal")
			conect = 0
			for i in range(5+1):
				if arrancada('s'+str(i),'S'+str(i)) == 1:
					conect = 1
			if conect == 1:
				for i in range(5+1):
					if arrancada('s'+str(i),'S'+str(i)) == 1:
						print "Prueba de conectividad con el servidor S"+str(i)+":"
						os.system("traceroute 10.0.2.1"+str(i))
			else:
				print "No hay ningún servidor arrancado para probar la conectividad"
		else:
        		print "Para obtener información sobre la conectividad del host con los servidores del escenario solo se necesita el párametro de la orden (conectividad)"
	else:
    		print "Este programa necesita un parámetro para la orden de ejecución y otro que indique el número de servidores web a configurar/arrancar/parar/destruir"
else:
	print "Este programa necesita un parámetro para la orden de ejecución y otro que indique el número de servidores web a configurar/arrancar/parar/destruir"
