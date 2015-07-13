#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
import time
import pprint
import xml.etree.ElementTree as ET

def merge_xml(old_xml, new_xml):
 #print old_xml
 #old_xml_hash =  ET.fromstring(old_xml)
 #print old_xml_hash
 new_xml_hash =  ET.fromstring(new_xml)  
 print new_xml_hash
 

 for ci in new_xml_hash.findall('ci'):
    print ci

from lm.ConfigFsServerUtil import ConfigFsServerUtil

server = ConfigFsServerUtil.createConfigFsServer(configFsServer)

new_config_xml = server.get_file_contents(remotePathOnFs)
print new_config_xml
config_xml = merge_xml(current_config_xml, new_config_xml)



#setup connection object





#find the file 


#read the file


#push contents to output
