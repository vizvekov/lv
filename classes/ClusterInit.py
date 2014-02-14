__author__ = 'subadmin'

import libvirt
from classes.ClusterPool import ClusterPool

class ClusterInit(ClusterPool):

    vmInCluster = {}

    __states = {
    libvirt.VIR_DOMAIN_NOSTATE: 'no state',
    libvirt.VIR_DOMAIN_RUNNING: 'running',
    libvirt.VIR_DOMAIN_BLOCKED: 'blocked on resource',
    libvirt.VIR_DOMAIN_PAUSED: 'paused by user',
    libvirt.VIR_DOMAIN_SHUTDOWN: 'being shut down',
    libvirt.VIR_DOMAIN_SHUTOFF: 'shut off',
    libvirt.VIR_DOMAIN_CRASHED: 'crashed',
    }

    def __init__(self,poolConfig):
        ClusterPool.__init__(poolConfig)

    def add_node(self,ip):
        conn = libvirt.open("qemu+ssh://root@%s/system" % ip)
        self.vmInCluster.update({conn.getHostname(): conn})
        self.__inspest_node(conn)

    def __inspest_node(self,node_conn):
        pools = node_conn.listDefinedStoragePools()
        if self.get_pool_name() not in pools:
            storage = node_conn.storagePoolDefineXML(self.get_pool_xml(),0)
            storage.build(0)
            storage.create(0)

    def __get_valid_host(self):
        return self.vmInCluster[0]

    def __init_vm(self,vm_name,disk_size):
        vol_xml = self.create_volume_xml(vm_name,disk_size)
        conn = self.__get_valid_host()


    def is_vm_run(self,state):
        if self.__states.get(state, state) == 'running':
            return True
        return False

    def get_vm_in_cluster(self,run_only = False, get_by = "name" ):
        vms = {}
        for host in self.vmInCluster:
            for id in self.vmInCluster[host].listDomainsID():
                dom = self.vmInCluster[host].lookupByID(id)
                [state, maxmem, mem, ncpu, cputime] = dom.info()
                if (run_only and self.is_vm_run(state)) or not run_only:
                    if get_by == "status":
                        vms.update({self.__states.get(state, state): dom})
                    else:
                        vms.update({dom.name(): dom})
        return vms