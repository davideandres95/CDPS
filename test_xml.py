#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
import os
import sys
import subprocess
from lxml import etree
from subprocess import Popen



def defineMachines(n_servers):
    for x in range(1 , n_servers):
        subprocess.call('qemu-img create -f qcow2 -b cdps-vm-base-p3.qcow2 s' + str(x) +'.qcow2')
        print('Fichero de definicion de la maquina virtual s' + str(x) + ' creado con exito' )
    subprocess.call('qemu-img create -f qcow2 -b cdps-vm-base-p3.qcow2 lb.qcow2')
    print('Fichero de definicion del balanceador creado con exito' )

def writeTemplates(n_servers):
    #Copiamos y escribimos las plantillas
    for x in range(1, n_servers):
        subprocess.call('cp plantilla-vm-p3.xml s' + str(x) + '.xml', shell=True)
        #Cargamos el fichero xml
        tree = etree.parse('s' + str(x) + '.xml')
        root = tree.getroot()
        #Buscamos la etiqueta 'nombre' y cambiamos su valor
        name = root.find('name')
        name.text = 'Servidor'+str(x)
        #Buscamos el archivo de destino y cambiamos file
        source_file = root.find('./devices/disk/source')
        source_file.set('file', 'mnt/tmp/pfinal/s' + str(x) + '.qcow2')
        #Configuramos el bridge
        source_bridge = root.find('./devices/interface/source')
        source_bridge.set('bridge', 'LAN1')
        print('plantilla de la maquina virtual s' + str(x) + ' creada con exito' )
    #Escribimos la plantilla del balanceador
    subprocess.call('cp plantilla-vm-p3.xml ' + 'lb.xml', shell=True)
    #Cargamos el fichero xml
    tree = etree.parse('lb.xml')
    root = tree.getroot()
    #Buscamos la etiqueta 'nombre' y cambiamos su valor
    name = root.find('name')
    name.text = 'Balanceador'
    #Buscamos el archivo de destino y cambiamos file
    source_file = root.find('./devices/disk/source')
    source_file.set('file', 'mnt/tmp/pfinal/lb.qcow2')
    #Configuramos los bridges
    source_inteface = root.find('./devices/interface/source')
    source_inteface.set('bridge', 'LAN1')
    interface2 = root.find('./devices/interface')
    writeinterface2 = etree.SubElement(interface2, 'interface', type='bridge')
    writesource2 = etree.SubElement(writeinterface2, 'source', bridge='LAN2')
    writemodel2 = etree.SubElement(writesource2, 'model', type='virtio')
    outFile = open('lb.xml', 'w')
	doc.write(outFile)
    print('plantilla del balanceador creada con exito' )

def startMachines(n_servers):
    #Arrancamos los servidores
    for x in range(1, n_servers):
        os.system('sudo virsh create s' + str(x) + '.xml')
        print 'La máquina Servidor'+ str(x) +' se ha arrancado'
        terminal = 'sudo virsh console Servidor' + str(x)
        p1 = Popen(['xterm', '-e', terminal])
    #Arrancamos el balanceador
    os.system('sudo virsh create lb.xml')
    print 'El balanceador se ha arrancado'
    terminal = 'sudo virsh console Balanceador'
    p1 = Popen(['xterm', '-e', terminal])

def stop(machine_name):
	os.system('sudo virsh shutdown '+ machine_name)

def stopDestroying(nmachine_name):
	os.system('sudo virsh destroy '+ machine_name)

#main process
if len(sys.argv) >= 2:
    orden = sys.argv[1]
    if orden == "create":
        if len(sys.argv) == 3:
            n_servers = int(sys.argv[2])
            if (n_servers>0 or n_servers<6):
                defineMachines(n_servers)
                writeTemplates(n_servers)
            else:
                print "Para poder crear los ficheros .qcow2 y xml de cada MV el número de servidores web debe estar entre 1 y 5"
        else:
            print "Para poder crear los ficheros .qcow2 y xml de cada MV se necesita un tercer parametro que indique el número de servidores web a configurar"
    elif orden == "start":
        if len(sys.argv) == 3:
            n_servers = int(sys.argv[2])
            startMachines(n_servers)
        else:
            print "Para arrancar las MVs y mostrar su consola se necesita un tercer parametro que indique el número de servidores web a arrancar"
    elif orden == "stop":
        numero_de_maquinas = raw_input("Por favor indique con un numero del 1 al 5 el numero de maquinas creadas: (1-5)")
        confirmacion = raw_input("Va a parar también el balanceador de trafico además de las" + numero_de_maquinas + "maquinas. ¿Desea Constinuar? (y/n)")
        if confirmacion == 'y':
            for x in range (1, numero_de_maquinas):
                stop('Servidor'+str(x))
                print('Se ha parado el Servidor'+str(x))
            stop('Balanceador')
        else:
            print ('Se ha cancelado la parada de maquinas')
    elif orden == "destroy"
        numero_de_maquinas = raw_input("Por favor indique con un numero del 1 al 5 el numero de maquinas creadas: (1-5)")
        confirmacion = raw_input("Va a destruir también el balanceador de tráfico además de las" + numero_de_maquinas + "maquinas. ¿Desea Continuar? (y/n)")
        if confirmacion == 'y':
            for x in range (1, numero_de_maquinas):
                stopDestroying('Servidor'+str(x))
                print('Se ha destruido el Servidor'+str(x))
            stopDestroying('Balanceador')
        else:
            print ('Se ha cancelado la destruccion de maquinas')
    else:
        print "Este programa necesita un parametro para la orden de ejecucion y otro que indique el número de servidores web a crear/arrancar/parar/destruir"
else:
    print "Este programa necesita un parametro para la orden de ejecucion y otro que indique el número de servidores web a crear/arrancar/parar/destruir"
