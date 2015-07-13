import sys, time, ast, os
sys.modules.clear()
import xml.parsers.expat
import xml.etree.ElementTree as ET

import pprint

from java.lang import String
from java.util import Arrays

from lmDarBuilder.DarBuildServerUtil import DarBuildServerUtil

server = DarBuildServerUtil.createDarBuildServer(darBuildServer)

server.package_dar(appName, appVersion)

server.upload_dar_package(appName, appVersion, xldeployServer)