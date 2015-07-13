import sys, time, ast

from java.lang import String
from java.util import Arrays
from org.apache.commons.collections.list import FixedSizeList;



from overtherepy import SshConnectionOptions, OverthereHost, OverthereHostSession
from lm.ConfigRTCServerUtil import ConfigRTCServerUtil

class ConfigRTCRepo(object):
    def __init__(self, username, password, url, client_server,component):
        self.server              = ConfigRTCServerUtil.createConfigRTCServer(client_server, component)
        self.rtc_username        = username
        self.rtc_password        = password
        self.rtc_repo            = url
        
    @staticmethod
    def createRepo(username,password,url, client_server, component):
        return ConfigRTCRepo(username,password,url, client_server, component)   

    def execute_lscm_command(self, command, properties, json=True, run_in_workdirectory=False):
      print "execute_lsmc_command"
      if json: 
        return self.server.execute_lscm_command("%s %s %s --json" % (command, self.rtc_command_credentials(), properties), run_in_workdirectory)
      else:
        return self.server.execute_lscm_command("%s %s %s" % (command, self.rtc_command_credentials(), properties), run_in_workdirectory)

    def get_file_as_string(self, file_name):
      return self.server.get_file_contents(file_name)

            
    def rtc_command_credentials(self):
        return " -u %s -P %s -r %s" % (self.rtc_username, self.rtc_password, self.rtc_repo)
     
    def get_server(self):
        return self.server

   
