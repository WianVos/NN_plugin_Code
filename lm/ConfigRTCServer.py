import sys, time, ast,datetime

from java.lang import String
from java.util import Arrays
from org.apache.commons.collections.list import FixedSizeList;
 


from overtherepy import SshConnectionOptions, OverthereHost, OverthereHostSession

class ConfigRTCServer(object):
    def __init__(self, server, dirname="tmp"):
        self.sshOpts = SshConnectionOptions(server['host'], username=server['username'],password=server['password'])
        self.host = OverthereHost(self.sshOpts)
        self.session = OverthereHostSession(self.host)
        self.WorkDirBase = server['filesystemLocation']
        self.WorkDirTimeStamp = int(time.time())
        self.WorkDirName = dirname
        self.workDirectory = None
        self.RtcClient = server['pathToClientSoftware']

    def __del__(self):
        self.destroy_work_directory()
        self.session.close_conn() 


    @staticmethod
  
    def createServer(server, dirname): 
        return ConfigRTCServer(server, dirname)
       
    def get_file_contents(self, file_name):
        response = self.session.read_file("%s/%s" % (self.getWorkDirectory(), file_name))
        return response
    
	 
    def execute_lscm_command(self, command, run_in_workdirectory=False):
        print command
        command = self.sub_placeholders(command)
        print command
        lscm_command="%s %s" % (self.RtcClient, command)

        if run_in_workdirectory is False:
          response = self.execute_command(lscm_command)
        else:
          response = self.execute_command_in_workDirectory(lscm_command)
        return response


    def execute_command(self, command):
        print "executing command: %s " % (command)
        response = self.session.execute(command, check_success=False, suppress_streaming_output=False)
        if response.rc != 0:
          print response.stderr
          print "unable to execute command %s" % (command)
          raise Exception('unable to execute command ')
        else:
          print "Response", str(response.stdout)
          return response
        
    def getWorkDirectory(self):
        if self.workDirectory is None:
          self.execute_command("/bin/mkdir -p %s/%s/%s" % (self.WorkDirBase,self.WorkDirTimeStamp,self.WorkDirName))
          self.workDirectory =  "%s/%s/%s" % (self.WorkDirBase,self.WorkDirTimeStamp,self.WorkDirName)
        return self.workDirectory

    def destroy_work_directory(self):
        if self.workDirectory is not None:
          self.execute_command("/bin/rm -rf %s/%s" % (self.WorkDirBase, self.WorkDirName))
    
    def sub_placeholders(self, input):
        print self.workDirectory
        print self.getWorkDirectory()
	output = input.replace('<work_dir>',  self.getWorkDirectory())
        return output

         
