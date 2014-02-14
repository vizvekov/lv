__author__ = 'subadmin'
## storage_xml = """
##<pool type='dir'>
##  <name>%s</name>
##  <capacity>0</capacity>
##  <allocation>0</allocation>
##  <available>0</available>
##  <source>
##  </source>
##  <target>
##    <path>%s</path>
##    <permissions>
##      <mode>0755</mode>
##      <owner>123</owner>
##      <group>234</group>
##    </permissions>
##  </target>
##</pool>""" % ( name, path )

class ClusterPool():

    __PoolName = str()
    __PoolPath = str()
    __storage_xml = str()
    def __init__(self,config = {"name": "pool1","path": "/tmp"}):
        self.__PoolName = config['name']
        self.__PoolPath = config['path']
        self.storage_xml = """
<pool type='dir'>
  <name>%s</name>
  <capacity>0</capacity>
  <allocation>0</allocation>
  <available>0</available>
  <source>
  </source>
  <target>
    <path>%s</path>
    <permissions>
      <mode>0755</mode>
      <owner>123</owner>
      <group>234</group>
    </permissions>
  </target>
</pool>""" % ( self.__PoolName, self.__PoolPath )

    def create_volume_xml(self,vol_name,size):
        vol_xml = """<volume>
         <name>%s</name>
         <key>%s/%s</key>
         <source>
         </source>
         <capacity unit='GiB'>%s</capacity>
         <allocation unit='GiB'>%s</allocation>
       </volume>""" %(vol_name,self.__PoolName,vol_name,size,size)
        return vol_xml

    def get_pool_name(self):
        return self.__PoolName

    def get_pool_path(self):
        return self.__PoolPath

    def get_pool_xml(self):
        return self.__storage_xml

