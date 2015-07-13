from lm.RTCWorkspace import RTCWorkspace

class RTCWorkspaceUtil(object):

    @staticmethod
    def createRTCWorkspace(config, client_server):
      return RTCWorkspace.createRTCWorkspace(config, client_server)
