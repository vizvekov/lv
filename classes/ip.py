__author__ = 'subadmin'

from IPy import IP


class CloudIP():
    __subnets = []
    __alloc_ip = ['']

    def __init__(self):
        pass

    def get_net_mask(self,subnet_index):
        return IP(self.__subnets[subnet_index].netmask())

    def add_subnet(self, subnet):
        self.__subnets.append(subnet)

    def list_subnets(self):
        return self.__subnets

    def isInSubnet(self,ip,subnet_index=None):
        if subnet_index != None:
            ips = IP(self.__subnets[subnet_index])
            ip_list = [str(x) for x in ips]
            if ip in ip_list:
                return True
            return False
        else:
            for subnet in self.__subnets:
                ips = IP(subnet)
                ip_list = [str(x) for x in ips]
                if ip in ip_list:
                     return True
                return False

    def __bust_ip(self, subnet_index):
        ips = IP(self.__subnets[subnet_index])
        ip_list = [str(x) for x in ips]
        for ip in ip_list:
            if (ip not in self.__alloc_ip) and (ip != ips.broadcast().strCompressed()) and (ip != ips.net().strCompressed()):
                self.__alloc_ip.append(ip)
                return True, ip
        return False, "No free IP in subnet %s" % self.__subnets[subnet_index]

    def isIPInUse(self, ip):
        if ip in self.__alloc_ip:
            return True
        return False

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