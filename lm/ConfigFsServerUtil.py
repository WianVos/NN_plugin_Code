from lm.ConfigFsServer import ConfigFsServer

class ConfigFsServerUtil(object):

    @staticmethod
    def createConfigFsServer(server, username="None", password="None"):
     client =  ConfigFsServer.createServer(server, username, password)
     return client


