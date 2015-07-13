import sys, time, ast 

from java.lang import String
from java.util import Arrays
from org.apache.commons.collections.list import FixedSizeList;
from com.xhaus.jyson import JysonCodec as json


from overtherepy import SshConnectionOptions, OverthereHost, OverthereHostSession
from lm.ConfigRTCServerUtil import ConfigRTCServerUtil
from lm.ConfigRTCRepoUtil import ConfigRTCRepoUtil

class RTCWorkspace(object):
    
    def __init__(self, config, client_server):
        self.repo      = ConfigRTCRepoUtil.createConfigRTCRepo(config['username'],config['password'], config['RTC_REPO'], client_server, config['COMPONENT'])
	self.name      = config['WORKSPACE']
        self.uuid      = None
        self.stream    = config['STREAM']
        self.component = config['COMPONENT']

    @staticmethod
    def createRTCWorkspace(config, client_server):
        ws = RTCWorkspace(config, client_server)
        ws.initialize()
        return ws

    def initialize(self):
        print "initialize"
        self.create()	
    	self.add_component()
    	self.set_target()
    	self.load()

    def read_file(self, file_name):
	try:
	  response = self.repo.get_file_as_string(file_name)
        except Exception:
          raise Exception('Unable to read file')
        return response

    def get_uuid(self):
    	if self.uuid is None:
    	  response = self.create()
          print response
    	  self.uuid = response['uuid']
        return self.uuid

    def create(self):
    	response = self.execute("create workspace","%s -e" % self.name)
        self.uuid = response['uuid']

    def destroy(self):
    	if self.uuid is not None:
    	  response = self.execute("delete workspace", self.uuid, False)

    def add_component(self):
        self.execute("workspace add-component", "-s %s %s %s " % (self.stream, self.get_uuid(), self.component), False)
	
    def set_target(self):
        self.execute("change-target workspace", "%s %s" % (self.get_uuid(), self.stream), False)

    def load(self):
    	self.execute("load", "%s -d <work_dir> --all -q" % (self.get_uuid()), False)
 

    def execute(self, command, properties, use_json=True, run_in_workdirectory=False):
        try:
	  if use_json:
	    response = self.repo.execute_lscm_command(command, properties, use_json, run_in_workdirectory)
            string_response = ""
	    for line in response.stdout:
              string_response = "%s %s" % (string_response, line)
            json_response = json.loads(string_response)
	    return json_response
	  else:
	    response = self.repo.execute_lscm_command(command, properties, use_json, run_in_workdirectory)
	  return response
        except Exception:   
          self.destroy()
          raise Exception('unfable to execute command ')

  
  
