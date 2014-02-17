__author__ = 'subadmin'

import paramiko
import libvirt
from classes.xml_generator import domXML_create, Dom0_XML
from classes.ip import CloudIP
import random
import time

class CloudVM(CloudIP):

    Nodes = {}
    VMs = {}
    disks_path = ""

    COMMANDDICT = {"none":0, "modify":1, "delete":2, "add-first":4}
    SECTIONDICT = {"none":0, "bridge":1, "domain":2, "ip":3, "ip-dhcp-host":4, \
                 "ip-dhcp-range":5, "forward":6, "forward-interface":7,\
               "forward-pf":8, "portgroup":9, "dns-host":10, "dns-txt":11,\
               "dns-srv":12}
    FLAGSDICT = {"current":0, "live":1, "config": 2}

    def _get_mac(self):
        return ':'.join(map(lambda x: "%02x" % x, [ 0x00, 0x16, 0x3E, random.randint(0x00, 0x7F), random.randint(0x00, 0xFF), random.randint(0x00, 0xFF) ]))

    def __init__(self, disks_path = "/tmp/"):
        CloudIP.__init__(self)
        self.disks_path = disks_path

    def __inspect_new_node(self,node_name,net):
        net_obj = self.Nodes[node_name][0].networkLookupByName(net)
        dom0_XML = Dom0_XML(net_obj.XMLDesc(0))
        print "Old router: %s" % dom0_XML.get_default_router()
        if self.isIPInUse(dom0_XML.get_default_router()) or not self.isInSubnet(dom0_XML.get_default_router()):
            self.__instect_used_ip()
            print "Creating New Router"
            status, ip = self.get_ip()
            if status:
                net_obj.destroy()
                dom0_XML.set_default_router(ip)
                dom0_XML.del_range()
                net_obj = self.Nodes[node_name][0].networkDefineXML(dom0_XML.get_XML_dom0_net())
                net_obj.create()
            else:
                print ip
        print "New route: %s" % dom0_XML.get_default_router()
        self.add_ip_as_used(dom0_XML.get_default_router())
        dom0_XML.reset_xml(self.Nodes[node_name][0].getCapabilities())
        emulator = dom0_XML.get_emulator()
        self.Nodes[node_name].append(emulator)

    def test_libvirt_connection(self, hode_name):
        conn = self.Nodes[hode_name][0]
        hostname = self.Nodes[hode_name][4]
        if not conn.isAlive():
            return libvirt.open("qemu+ssh://root@%s/system" % hostname)
        return conn

    def __del_vm_ip(self,vm_name,net = 'default'):
        net_obj = self.Nodes[self.VMs[vm_name][1]][0].networkLookupByName(net)
        dom0_XML = Dom0_XML()
        net_obj.update(self.COMMANDDICT['delete'],self.SECTIONDICT['ip-dhcp-host'],0,dom0_XML.set_static_ip(self.VMs[vm_name][3],self.VMs[vm_name][2],vm_name),self.FLAGSDICT['live'])
        self.releace_ip(self.VMs[vm_name][2])
        self.VMs[vm_name][2] = None

    def __set_vm_ip(self, vm_name, net = 'default'):
        if self.VMs[vm_name][2] == None:
            self.__instect_used_ip()
            status, ip = self.get_ip()
            if status:
                self.VMs[vm_name][2] = ip
        net_obj = self.Nodes[self.VMs[vm_name][1]][0].networkLookupByName(net)
        dom0_XML = Dom0_XML()
        net_obj.update(self.COMMANDDICT['add-first'],self.SECTIONDICT['ip-dhcp-host'],0,dom0_XML.set_static_ip(self.VMs[vm_name][3],self.VMs[vm_name][2],vm_name),self.FLAGSDICT['live'])

    def __instect_used_ip(self,file = "/var/lib/libvirt/dnsmasq/default.leases",net = 'default'):
        for node in self.Nodes:
            print "Inspect node %s" % node
            file_obj = self.read_remote_file(node,file)
            for line in file_obj:
                print "Used IP %s" % line.split(' ')[2]
                self.add_ip_as_used(line.split(' ')[2])
            dom0_XML = Dom0_XML(self.Nodes[node][0].networkLookupByName(net).XMLDesc(0))
            ips = dom0_XML.get_ip_in_network()
            del dom0_XML
            for ip in ips:
                print "Defined IP %s" % ip
                self.add_ip_as_used(ip)

    def get_vm_strim(self,vm_name):
        return self.Nodes[self.VMs[vm_name][1]][0].newStream(0)

    def add_node(self,hostname,user,password, net = 'default'):
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname,username=user,password=password)
        conn = libvirt.open("qemu+ssh://root@%s/system" % hostname)
        net = conn.networkLookupByName()
        net.update("add","ip-dhcp-host",0,"",0)
        self.Nodes.update({conn.getHostname(): [conn,ssh,user,password,hostname]})
        self.__inspect_new_node(conn.getHostname(),net)
        return conn.getHostname()

    def live_memory_resize(self,vm_name,new_size):
        return self.get_vm(vm_name).setMemory(new_size)

    def suspend_vm(self,vm_name):
        return self.get_vm(vm_name).suspend()

    def resume_vm(self,vm_name):
        return self.get_vm(vm_name).resume()

    def destroy_vm(self,vm_name):
        self.__del_vm_ip(vm_name)
        return self.get_vm(vm_name).destroy()

    def undefine_vm(self,vm_name):
        if self.get_vm(vm_name).isActive():
            self.destroy_vm(vm_name)
        else:
            self.__del_vm_ip(vm_name)
        self.get_vm(vm_name).undefine()
        del self.VMs[vm_name][0]
        del self.VMs[vm_name]

    def live_resize_disk(self,vm_name,new_size):
        vm = self.get_vm(vm_name)
        vm.blockResize("%s%s.qcow2" %(self.disks_path,vm_name.replace(' ','')),new_size,0)
        pty = self.VMs[vm_name][0].get_sirial_pty_from_xml(vm.XMLDesc(0))
        self.exec_command(self.VMs[vm_name][1],'echo -e "\n\necho -e \'\nd\nn\n\n\n\n\n\nw\n\' | fdisk /dev/vda\n\n" | socat - %s' % pty)
        time.sleep(1)
        self.exec_command(self.VMs[vm_name][1],'echo -e "\n\npartprobe /dev/vda\n\n" | socat - %s' % pty)
        time.sleep(1)
        self.exec_command(self.VMs[vm_name][1],'echo -e "\n\nresize2fs /dev/vda1\n\n" | socat - %s' % pty)
        time.sleep(1)


    def get_vm(self,vm_name):
        return self.Nodes[self.VMs[vm_name][1]][0].lookupByName(vm_name)

    def exec_command(self,node_name,command):
        return self.Nodes[node_name][1].exec_command(command)

    def read_remote_file(self,node_name,file):
        file_object = []
        print "Open file %s on node %s" % (file,node_name)
        sftp = self.Nodes[node_name][1].open_sftp()
        file_remote = sftp.open(file, 'r')
        for line in file_remote:
            file_object.append(line)
        file_remote.close()
        sftp.close()
        return file_object

    def create_vm(self,name,ram,cpu,node_name):
        self.__instect_used_ip()
        status, ip = self.get_ip()
        if status:
            self.VMs.update({name: [domXML_create(name,ram,cpu,emulator=self.Nodes[node_name][5]), node_name, ip,self._get_mac()]})
            return True
        return False

    def add_disk(self,vm_name, path_to_image, disk_size):
        self.exec_command(self.VMs[vm_name][1],"qemu-img create -f qcow2 -b %s %s%s.qcow2 %sG" % (path_to_image, self.disks_path,vm_name.replace(' ',''),disk_size))
        self.test_libvirt_connection(self.VMs[vm_name][1])
        self.VMs[vm_name][0].add_file_disk("%s%s.qcow2" % (self.disks_path,vm_name.replace(' ','')))

    def add_interface(self,vm_name,net_name = 'default'):
        self.VMs[vm_name][0].add_interface(self.VMs[vm_name][3], net_name)

    def define_vm(self,vm_name):
        self.Nodes[self.VMs[vm_name][1]][0].defineXML(self.VMs[vm_name][0].create())

    def start_vm(self,vm_name):
        self.__set_vm_ip(vm_name)
        vm = self.get_vm(vm_name)
        vm.create()

    def get_vm_stat(self,vm_name):
        vm = self.Nodes[self.VMs[vm_name][1]][0].lookupByName(vm_name)
        return vm.isActive()

    def __add_firewall_rule(self):
        pass