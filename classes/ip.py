__author__ = 'subadmin'

from IPy import IP


class CloudIP():
    __subnets = []
    __alloc_ip = ['192.168.122.1']

    def __init__(self):
        pass

    def add_subnet(self, subnet):
        self.__subnets.append(subnet)

    def get_subnets(self):
        return self.__subnets

    def __bust_ip(self, subnet_index):
        ips = IP(self.__subnets[subnet_index])
        ip_list = [str(x) for x in ips]
        for ip in ip_list:
            if (ip not in self.__alloc_ip) and (ip.split('.')[3] != '0') and (ip.split('.')[3] != '255'):
                self.__alloc_ip.append(ip)
                return True, ip
        return False, "No free IP in subnet %s" % self.__subnets[subnet_index]

    def add_ip_as_used(self,ip):
        if ip not in self.__alloc_ip:
            self.__alloc_ip.append(ip)

    def releace_ip(self,ip):
        if ip in self.__alloc_ip:
            del self.__alloc_ip[self.__alloc_ip.index(ip)]

    def get_ip(self, subnet_index=None):
        if subnet_index != None:
            return self.__bust_ip(subnet_index)
        else:
            for subnet in self.__subnets:
                status, ip = self.__bust_ip(self.__subnets.index(subnet))
                if status:
                    return True, ip
            return False, "No Free IPs"