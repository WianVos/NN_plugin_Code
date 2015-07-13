from lm.ConfigRTCServer import ConfigRTCServer

class ConfigRTCServerUtil(object):

    @staticmethod
    def createConfigRTCServer(server, dirname):
     client =  ConfigRTCServer.createServer(server, dirname)
     return client


