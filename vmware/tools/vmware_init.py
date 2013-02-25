#!/usr/bin/python

from suds.client import Client
from suds.sudsobject import Property

import logging

def client_init(url, username, password):
         
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('suds.client').setLevel(logging.INFO)
    logging.getLogger('suds.wsdl').setLevel(logging.INFO)
    
    client = Client(url+'/sdk/vimService?wsdl')
    
    client.set_options(location=url+'/sdk')
    
    mo_ServiceInstance = Property('ServiceInstance')
    mo_ServiceInstance._type = 'ServiceInstance'
    
    ServiceContent = client.service.RetrieveServiceContent(mo_ServiceInstance)
    
    mo_SessionManager = Property(ServiceContent.sessionManager.value)
    mo_SessionManager._type = 'SessionManager'
    
    SessionManager = client.service.Login(mo_SessionManager, username, password)
    
    return client, ServiceContent, SessionManager

def get_object_properties(client, ServiceContent, propFilterSpec):
    mo_PropertyCollector = Property(ServiceContent.propertyCollector.value)
    mo_PropertyCollector._type = 'PropertyCollector'
    return client.service.RetrieveProperties(mo_PropertyCollector, propFilterSpec)
     

def get_property_by_name(client, ServiceContent, type, name):
    id = find_object_id_by_name(client, ServiceContent, type, name)
    p = Property(id)
    p._type = type
    return p

def find_object_id_by_name(client, ServiceContent, type, name):
    for obj in get_object_list_simple(client, ServiceContent, type):
        if obj['name']==name: return obj['mo_ref']

def get_object_list_simple(client, ServiceContent, type):
    return get_object_list(client, ServiceContent, type, "name")

def get_object_list(client, ServiceContent, type, fields):
    
    pfs = client.factory.create('ns0:PropertyFilterSpec')
    pfs.propSet = [ select_object_attributes(client,type,fields) ]
    pfs.objectSet = [ select_object_spec(client, ServiceContent) ]
    
    objContent = get_object_properties(client, ServiceContent, pfs)
   
    return map(properties_to_dict, objContent)

def get_object_simple(client, ServiceContent, type, id):
    return get_object(client, ServiceContent, type, id, ["name"])

def get_object(client, ServiceContent, type, id, fields):
    
    obj = client.factory.create('ns0:ManagedObjectReference')
    obj._type = type
    obj.value = id
    
    object_spec = client.factory.create('ns0:ObjectSpec')
    object_spec.obj = obj
    
    pfs = client.factory.create('ns0:PropertyFilterSpec')
    pfs.propSet = [select_object_attributes(client,type,fields)]
    pfs.objectSet = [object_spec]
    
    objContent = get_object_properties(client, ServiceContent, pfs)
   
    return objContent[0]
    
 
def select_object_attributes(client, object_name, attributes):
    
    propSpec = client.factory.create('ns0:PropertySpec')
    propSpec.all = True if attributes==True else False
    if attributes!=True: propSpec.pathSet = attributes
    propSpec.type = object_name
    
    return propSpec

def get_object_list_by_folder(client, ServiceContent, folder_name, object_type, fields):
    
    folder_id = find_object_id_by_name(client, ServiceContent, "Folder", folder_name)
    folder = get_object(client, ServiceContent, "Folder", folder_id, ["name"])
    
    #for vm in list['childEntity']['ManagedObjectReference']:
    #if vm['_type']=="VirtualMachine":
    #    print vm['value']
    #return folder
    
    FolderTraversalSpec, DatacenterVMTraversalSpec  = select_traversal_spec(client, ServiceContent)
    
    mo_RootFolder = Property(folder_id)
    mo_RootFolder._type = 'Folder'
    
    objSpec = client.factory.create('ns0:ObjectSpec')
    objSpec.obj = mo_RootFolder
    objSpec.selectSet = [ FolderTraversalSpec, DatacenterVMTraversalSpec ]
    
    pfs = client.factory.create('ns0:PropertyFilterSpec')
    pfs.propSet = [ select_object_attributes(client, object_type, fields) ]
    pfs.objectSet = [ objSpec ]
    
    objContent = get_object_properties(client, ServiceContent, pfs)
   
    list = map(properties_to_dict, objContent)
    
    return list

def select_traversal_spec(client, ServiceContent):
    # Traversal Specs
    FolderTraversalSpec = client.factory.create('ns0:TraversalSpec')
    DatacenterVMTraversalSpec = client.factory.create('ns0:TraversalSpec')
    
    FolderSelectionSpec = client.factory.create('ns0:SelectionSpec')
    DatacenterVMSelectionSpec = client.factory.create('ns0:SelectionSpec')
    
    FolderSelectionSpec.name = "FolderTraversalSpec"
    DatacenterVMSelectionSpec.name = "DatacenterVMTraversalSpec"
    
    DatacenterVMTraversalSpec.name = "DatacenterVMTraversalSpec"
    DatacenterVMTraversalSpec.type = "Datacenter"
    DatacenterVMTraversalSpec.path = "vmFolder"
    DatacenterVMTraversalSpec.skip = True
    
    FolderTraversalSpec.name = "FolderTraversalSpec"
    FolderTraversalSpec.type = "Folder"
    FolderTraversalSpec.path = "childEntity"
    FolderTraversalSpec.skip = True
    
    DatacenterVMTraversalSpec.selectSet = [FolderSelectionSpec]
    FolderTraversalSpec.selectSet = [DatacenterVMSelectionSpec, FolderSelectionSpec]
    
    return FolderTraversalSpec, DatacenterVMTraversalSpec 

def select_object_spec(client, ServiceContent):
    
    FolderTraversalSpec, DatacenterVMTraversalSpec  = select_traversal_spec(client, ServiceContent)
    
    # Object Spec
    mo_RootFolder = Property(ServiceContent.rootFolder.value)
    mo_RootFolder._type = 'Folder'
    
    objSpec = client.factory.create('ns0:ObjectSpec')
    objSpec.obj = mo_RootFolder
    objSpec.selectSet = [ FolderTraversalSpec, DatacenterVMTraversalSpec ]
    
    return objSpec

# maps dynamic properties to object as dict
def properties_to_dict(entity):
        props = {}

        props['_type'] = entity.obj._type
        props['mo_ref'] = entity.obj.value

        for dynProp in entity.propSet:
                props[dynProp.name] = dynProp.val

        return props