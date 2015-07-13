import sys, time, ast
sys.modules.clear()

from java.lang import String
from java.util import Arrays

from lmDarBuilder.DarBuildServerUtil import DarBuildServerUtil

server = DarBuildServerUtil.createDarBuildServer(darBuildServer)

server.init_dar(appName, appVersion)

