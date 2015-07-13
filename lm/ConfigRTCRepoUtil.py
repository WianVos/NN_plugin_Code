from lm.ConfigRTCRepo import ConfigRTCRepo

class ConfigRTCRepoUtil(object):

    @staticmethod
    def createConfigRTCRepo(username, password, url, client_server, component):
     repo =  ConfigRTCRepo.createRepo(username, password, url, client_server, component)
     return repo


