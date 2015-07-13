import sys, time, ast, os
sys.modules.clear()
import xml.parsers.expat
import xml.etree.ElementTree as ET

import pprint

from java.lang import String
from java.util import Arrays

from lmDarBuilder.DarBuildServerUtil import DarBuildServerUtil
 
def get_deployable_element(dName, dType, dXml, fileName):
    deployable =  ET.Element(dType, name="%s" % dName, fileName="%s/%s" %(dName, fileName))
    if dXml: 
      addons = ET.fromstring(dXml)
      for addon in addons:
        print addon.tag, addon.attrib
        deployable.append(addon)
    return deployable


server = DarBuildServerUtil.createDarBuildServer(darBuildServer)

# get the physical ear file
server.import_ear(appName, appVersion, deployableName, deployableUrl)

# do the xml bit
output = server.read_manifest(appName, appVersion)
pprint.pprint(output)

root = ET.fromstring(output)

deployable = get_deployable_element(deployableName, deployableType, deployableXml, os.path.basename(deployableUrl))
for child in root:
  print child.tag, child.attrib
  print deployable.tag
  print deployable.attrib
  if child.tag == "deployables":
    child.append(deployable)
    print child.tag, child.attrib

updatedXml = ET.tostring(root,encoding="us-ascii")

server.write_manifest(appName, appVersion, updatedXml)
