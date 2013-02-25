#!/usr/bin/python

import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir) 

from tools.vmware_init import client_init, find_object_id_by_name, get_object, get_property_by_name
from secret import username,password
from suds.sudsobject import Property

client, ServiceContent, SessionManager = client_init('https://vmware1.mif', username,password)

folder = get_property_by_name(client, ServiceContent, "Folder", "VIRTUALIZACIJOS PASKAITOS")
tpl = get_property_by_name(client, ServiceContent, "VirtualMachine", "VIRT_LINUX_000_TPL")

locationSpec = client.factory.create('ns0:VirtualMachineRelocateSpec')

locationSpec.host = None
locationSpec.datastore = None
locationSpec.transform = None
pool = Property('resgroup-1405')
pool._type = 'ResourcePool'

locationSpec.pool = pool

cloneSpec = client.factory.create('ns0:VirtualMachineCloneSpec')
cloneSpec.powerOn = True
cloneSpec.template = False
cloneSpec.location = locationSpec
cloneSpec.snapshot = None

start_id = 1

for i in range(start_id, start_id+40):
    client.service.CloneVM_Task(tpl, folder, "VIRT_LINUX_"+str(i).zfill(3)+".A", cloneSpec)
    client.service.CloneVM_Task(tpl, folder, "VIRT_LINUX_"+str(i).zfill(3)+".B", cloneSpec)

