__author__ = 'subadmin'

from classes.CloudVM import CloudVM as cvm


cl1 = cvm()
hostname = cl1.add_node("localhost","root","7q2mu47v")
cl1.add_subnet("192.168.122.0/24")
if cl1.create_vm("test2",1024,1,hostname):
    cl1.add_disk("test2","/home/subadmin/PycharmProjects/libvirt_ha/ubuntu_image.qcow2","50")
    cl1.add_interface("test2")
    cl1.define_vm("test2")
    cl1.start_vm("test2")
    if cl1.get_vm_stat("test2"):
        print "Running"
    else:
        print "Stop"



