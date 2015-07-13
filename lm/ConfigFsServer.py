import sys, time, ast

from java.lang import String
from java.util import Arrays
from org.apache.commons.collections.list import FixedSizeList;



from overtherepy import SshConnectionOptions, OverthereHost, OverthereHostSession

class ConfigFsServer(object):
    def __init__(self, server, username=None, password=None):
        self.sshOpts = SshConnectionOptions(server['host'], username=server['username'],password=server['password'])
        self.host = OverthereHost(self.sshOpts)
        self.session = OverthereHostSession(self.host)
 

    def __del__(self):
        self.session.close_conn() 


    @staticmethod
    def createServer(server, username=None, password=None):
        return ConfigFsServer(server, username, password)

    def get_file_contents(self, file_path):
        response = self.session.read_file(file_path)
        return response
     

