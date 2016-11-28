#!/usr/bin/python
from lxml import etree
import subprocess

n_servers = sys.argv[1]

def createMachines():
    for x in range(1,n_servers):
        subprocess.call('qemu-img create -f qcow2 -b cdps-vm-base-p3.qcow s' + str(x) +'.qcow2')
        print('Fichero de definicion de la maquina virtual s' + str(x) + ' creado con exito' )
    return
    subprocess.call('qemu-img create -f qcow2 -b cdps-vm-base-p3.qcow lb.qcow2')

def writeTemplates():
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
    return

def startMachines():

    return

    
#main process
createMachines()
writeTemplates()
subprocess.call('sudo brctl addbr LAN1')
subprocess.call('sudo ifconfig LAN1 up')
