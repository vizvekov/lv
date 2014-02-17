__author__ = 'subadmin'

import xml.etree.cElementTree as ET

class domXML_create:

    def __init__(self, name, ram, cpu, os_type = "pc", arch = "x86_64", emulator = "/usr/libexec/qemu-kvm"):
        self.disk_names = ['vda','vdb','vdc','vdd']
        self.interfaces_name = ['net0','net1','net2','net3']
        self.domain = ET.Element("domain")
        self.domain.set("type", "kvm")
        ET.SubElement(self.domain,"name").text = name
        xml_mem = ET.SubElement(self.domain,"memory")
        xml_mem.set("unit","MiB")
        xml_mem.text = "%i" % (ram * 2)
        del xml_mem
        xml_curr_mem = ET.SubElement(self.domain,"currentMemory")
        xml_curr_mem.set("unit","MiB")
        xml_curr_mem.text = "%i" % ram
        del xml_curr_mem
        xml_vcpu = ET.SubElement(self.domain,"vcpu")
#        xml_vcpu.set("placement","static")
        xml_vcpu.text = "%i" % cpu
        del xml_vcpu
        self.domain_os = ET.SubElement(self.domain,"os")
        d_type = ET.SubElement(self.domain_os,"type")
        d_type.set("arch",arch)
        d_type.set("machine", os_type)
        d_type.text = "hvm"
        del d_type
        ET.SubElement(self.domain_os,"boot").set("dev","hd")
        ET.SubElement(self.domain_os,"boot").set("dev","cdrom")
        features = ET.SubElement(self.domain,"features")
        ET.SubElement(features,"acpi")
        ET.SubElement(features,"apic")
        ET.SubElement(features,"pae")
        del features
        ET.SubElement(self.domain,"clock").set("offset","utc")
        ET.SubElement(self.domain,"on_poweroff").text = "destroy"
        ET.SubElement(self.domain,"on_reboot").text = "restart"
        ET.SubElement(self.domain,"on_crash").text = "restart"
        self.dom_devices = ET.SubElement(self.domain,"devices")
        print "Set emulator: %s" % emulator
        ET.SubElement(self.dom_devices,"emulator").text = emulator
        self.__dev_init(name)


    def __dev_init(self,g_name):
        channel = ET.SubElement(self.dom_devices,"channel")
        channel.set("type","unix")
        chan_source = ET.SubElement(channel,"source")
        chan_source.set("mode","bind")
        chan_source.set("path","/var/lib/libvirt/qemu/%s.libguestfs" % g_name)
        del chan_source
        chan_target = ET.SubElement(channel,"target")
        chan_target.set("type","virtio")
        chan_target.set("name","org.libguestfs.channel.0")
        del chan_target
        dev_graphics = ET.SubElement(self.dom_devices,"graphics")
        dev_graphics.set("type","vnc")
        dev_graphics.set("port","5900")
        dev_graphics.set("autoport","yes")
        dev_graphics.set("listen","127.0.0.1")
        dev_graphics_listen = ET.SubElement(dev_graphics,"listen")
        dev_graphics_listen.set("type","address")
        dev_graphics_listen.set("address","127.0.0.1")
        del dev_graphics
        del dev_graphics_listen
        controller = ET.SubElement(self.dom_devices,"controller")
        controller.set("type","usb")
        controller.set("index","0")
        ET.SubElement(controller,"alias").set("name","usb0")
        del controller
        serial = ET.SubElement(self.dom_devices,"serial")
        serial.set("type","pty")
        ET.SubElement(serial,"source").set("path","/dev/pts/1")
        ET.SubElement(serial,"target").set("port","1")
        console = ET.SubElement(self.dom_devices,"console")
        console.set("type","pty")
        ET.SubElement(console,"source").set("path","/dev/pts/1")
        cons_target = ET.SubElement(console,"target")
        cons_target.set("type","virtio")
        cons_target.set("port","0")
        del cons_target
        del console
        dev_input = ET.SubElement(self.dom_devices,"input")
        dev_input.set("type","tablet")
        dev_input.set("bus","usb")
        ET.SubElement(dev_input,"alias").set("name","input0")
        dev_input = ET.SubElement(self.dom_devices,"input")
        dev_input.set("type","mouse")
        dev_input.set("bus","ps2")
        del dev_input
        video = ET.SubElement(self.dom_devices,"video")
        model = ET.SubElement(video,"model")
        model.set("type","cirrus")
        model.set("vram","9216")
        model.set("heads","1")
        del model
        ET.SubElement(video,"alias").set("name","video0")
        del video
        memballoon = ET.SubElement(self.dom_devices,"memballoon")
        memballoon.set("model","virtio")
        ET.SubElement(memballoon,"alias").set("name","balloon0")
        del memballoon

    def add_file_disk(self,disk_path,cache = "none"):
        disk = ET.SubElement(self.dom_devices,"disk")
        disk.set("type","file")
        disk.set("device","disk")
        driver = ET.SubElement(disk,"driver")
        driver.set("name","qemu")
        driver.set("type","qcow2")
        driver.set("cache", cache)
        del driver
        ET.SubElement(disk,"source").set("file",disk_path)
        target = ET.SubElement(disk,"target")
        target.set("dev",self.__get_next_disk())
#        target.set("dev","vda")
        target.set("bus","virtio")
        del target
        del disk

    def get_sirial_pty_from_xml(self,clear_xml):
        return ET.fromstring(clear_xml).findall("./devices/serial/source")[0].attrib['path']

    def __get_next_disk(self):
        val = self.disk_names[0]
        del self.disk_names[0]
        return val

    def __get_next_interface(self):
        val = self.interfaces_name[0]
        del self.interfaces_name[0]
        return val

    def add_interface(self,mac,net_name = "default"):
        interface = ET.SubElement(self.dom_devices,"interface")
        interface.set("type",'network')
        ET.SubElement(interface,"source").set("network",net_name)
        ET.SubElement(interface,"mac").set("address", mac)
        del interface

    def create(self):
#        tree = ET.ElementTree(self.domain)
        #tree.write("filename.xml")
        print ET.tostring(self.domain)
        return ET.tostring(self.domain)

class Dom0_XML():

    def __init__(self,xml_clear = None):
        if xml_clear == None:
            pass
        else:
            self.__xml = ET.fromstring(xml_clear)

    def reset_xml(self,xml_clear):
        self.__xml = ET.fromstring(xml_clear)

    def set_static_ip(self,mac,ip,vm_name):
        return "<host mac='%s' name='%s' ip='%s' />" % (mac,vm_name,ip)

    def get_emulator(self):
        return self.__xml.findall("./guest/arch/emulator")[0].text

    def del_static_ip(self,ip):
        hosts = self.__xml.findall("./ip/dhcp/host")
        for host in hosts:
            if host.attrib['ip'] == ip:
                dhcp = self.__xml.findall("./ip/dhcp")[0]
                dhcp.remove(host)

    def del_range(self):
        dhcp = self.__xml.findall("./ip/dhcp")
        ran = self.__xml.findall("./ip/dhcp/range")
        if dhcp and ran:
            dhcp[0].remove(ran[0])

    def set_default_router(self,ip):
        router = self.__xml.findall("./ip")[0]
        router.set("address",ip)

    def get_default_router(self):
        return self.__xml.findall("./ip")[0].attrib['address']

    def get_ip_in_network(self):
        ips = []
        hosts = self.__xml.findall("./ip/dhcp/host")
        if hosts:
            for host in hosts:
                ips.append(host.attrib['ip'])
        return ips

    def get_XML_dom0_net(self):
        return ET.tostring(self.__xml)

    def set_net_default_gw(self,gw):
        for child in self.__xml:
            if child.tag == "ip":
                child.set("address", gw)
        return self.__xml

