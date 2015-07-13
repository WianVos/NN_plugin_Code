from lmDarBuilder.DarBuildServer import DarBuildServer

class DarBuildServerUtil(object):

    @staticmethod
    def createDarBuildServer(server):
     server =  DarBuildServer.createServer(server)
     return server


