#!/usr/bin/python

import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir) 

from tools.vmware_init import client_init, get_object_list_by_folder
from secret import username,password

client, ServiceContent, SessionManager = client_init('https://vmware1.mif', username,password)

list = get_object_list_by_folder(client, ServiceContent, "VIRTUALIZACIJOS PASKAITOS", "VirtualMachine", ["name","summary.guest.ipAddress"])

vm_info = {}

for vm in list:
    if 'VIRT_LINUX_' in vm['name']:
        name = str(vm['name']).replace('VIRT_LINUX_','').split('.')
        if len(name)==2:
            id, code = name
            if 'summary.guest.ipAddress' in vm:
                if not vm_info.has_key(id): vm_info[id] = {}
                vm_info[id][code] = vm['summary.guest.ipAddress']
            
        
import csv
with open('vms.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for i in sorted(vm_info):
        for code in vm_info[i]:
            writer.writerow([i, code, vm_info[i][code], ''])
