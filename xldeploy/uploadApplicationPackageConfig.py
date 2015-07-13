#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
import re
import urllib
import sys, time, ast
from xml.etree import ElementTree as ET
from java.lang import String
from org.apache.commons.codec.binary import Base64
from org.apache.http import HttpHost
from org.apache.http.client.config import RequestConfig
from org.apache.http.client.methods import HttpGet, HttpPost, HttpPut, HttpDelete
from org.apache.http.util import EntityUtils
from org.apache.http.entity import StringEntity
from org.apache.http.impl.client import HttpClients
from com.xebialabs.xlrelease.domain.configuration import HttpConnection

class XLDeployClient(object):
    def __init__(self, httpConnection, username=None, password=None):
        self.httpRequest = HttpRequest(httpConnection, username, password)

    @staticmethod
    def createClient(httpConnection, username=None, password=None):
        return XLDeployClient(httpConnection, username, password)


    def extract_state(self, task_state_xml):
        state_pos = task_state_xml.find('state="')
        state_offset = len('state="')
        state_end_pos = task_state_xml.find('"', state_pos + state_offset + 1)
        state = task_state_xml[state_pos + state_offset:state_end_pos]
        return state


    def getParameterTypeName(self,root):
        params = root.find("parameters")
        if params:
            for child in params:
                return child.tag


    def getParameterNames(self, parameterTypeId):
        metadata_url = "/deployit/metadata/type/%s" % (parameterTypeId)
        metadata_response = self.httpRequest.get(metadata_url, contentType='application/xml')
        root = ET.fromstring(metadata_response.getResponse())
        params = root.find("property-descriptors")
        if params:
            parameterNames = []
            for child in params:
                parameterNames.append(child.get("name"))
        return parameterNames


    def addParameter(self, root, parameterTypeId, parameterName, parameters):
        params = root.find("parameters")
        propertyDict = dict(ast.literal_eval(parameters))
        if params:
            for child in params:
                if child.tag == parameterTypeId:
                    param = ET.SubElement(child, parameterName)
                    param.text = propertyDict[parameterName]


    def prepare_control_task(self, control_task_name, target_ci_id, parameters = None):
        # print 'DEBUG: prepare the control task'
        prepare_control_task_url = "/deployit/control/prepare/%s/%s" % (control_task_name, target_ci_id)
        prepare_response = self.httpRequest.get(prepare_control_task_url, contentType='application/xml')
        control_obj = prepare_response.getResponse()
        root = ET.fromstring(control_obj)
        # print 'DEBUG: Control obj from /prepare', control_obj, '\n'
        parameterTypeId = self.getParameterTypeName(root)
        # print 'DEBUG: got parameterTypeId: %s' % parameterTypeId
        if parameterTypeId:
            parameterNames = self.getParameterNames(parameterTypeId)
            # print 'Found parameter names: %s' % parameterNames
            for parameterName in parameterNames:
                self.addParameter(root, parameterTypeId, parameterName, parameters)
        # print 'DEBUG: Control obj after udating parameters ', ET.tostring(root), '\n'
        invoke_response = self.httpRequest.post('/deployit/control', ET.tostring(root), contentType='application/xml')
        task_id = invoke_response.getResponse()
        # print 'DEBUG: Control task ID', task_id, '\n'
        return task_id


    def invoke_task_and_wait_for_result(self, task_id, polling_interval = 10, number_of_trials = None, continue_if_step_fails = False, number_of_continue_retrials = 0):
        start_task_url = "/deployit/task/%s/start" % (task_id)
        print 'DEBUG: About to invoke task by post %s - continue enabled: %s - trial: %s \n' % (task_id, continue_if_step_fails, number_of_continue_retrials)
        self.httpRequest.post(start_task_url, '', contentType='application/xml')
        trial = 0
        while not number_of_trials or trial < number_of_trials:
            # print 'DEBUG: About to get task status', task_id, '\n'
            trial += 1
            get_task_status_url = "/deployit/task/%s" % (task_id)
            task_state_response = self.httpRequest.get(get_task_status_url, contentType='application/xml')
            task_state_xml = task_state_response.getResponse()
            status = self.extract_state(task_state_xml)
            print 'DEBUG: Task', task_id, 'now in state', status, '\n'
            if status in ('FAILED', 'STOPPED') and continue_if_step_fails and number_of_continue_retrials > 0:
                status = self.invoke_task_and_wait_for_result(task_id,polling_interval,number_of_trials, continue_if_step_fails, number_of_continue_retrials-1)
            if status in ('FAILED', 'STOPPED', 'CANCELLED', 'DONE', 'EXECUTED'):
                break
            time.sleep(polling_interval)
        return status
    
    def deploymentExists(self, deploymentPackage, environment):
        deploymentExistsUrl = "/deployit/deployment/exists?application=%s&environment=%s" % (deploymentPackage.rsplit('/',1)[0],environment)
        # print 'DEBUG: checking deployment exists with url %s \n' % deploymentExistsUrl
        deploymentExists_response = self.httpRequest.get(deploymentExistsUrl, contentType='application/xml')
        response = deploymentExists_response.getResponse()
        return 'true' in response
    
    def deploymentPrepareUpdate(self, deploymentPackage, environment):
        deploymentPrepareUpdateUrl = "/deployit/deployment/prepare/update?version=%s&deployedApplication=%s" % (deploymentPackage, "%s/%s" % (environment, deploymentPackage.rsplit('/',2)[1]))
        deploymentPrepareUpdate_response = self.httpRequest.get(deploymentPrepareUpdateUrl, contentType='application/xml')
        return deploymentPrepareUpdate_response.getResponse()

    def deploymentPrepareInitial(self, deploymentPackage, environment):
        deploymentPrepareInitialUrl = "/deployit/deployment/prepare/initial?version=%s&environment=%s" % (deploymentPackage, environment)
        deploymentPrepareInitial_response = self.httpRequest.get(deploymentPrepareInitialUrl, contentType='application/xml')
        return deploymentPrepareInitial_response.getResponse()

    def add_orchestrators(self, root, orchestrators):
        if orchestrators:
            params = root.find(".//orchestrator")
            params.clear()
            orchs = orchestrators.split(",")
            for orch in orchs:
                orchestrator = ET.SubElement(params, 'value')
                orchestrator.text = orch.strip()
    
    def set_deployed_application_properties(self, root, deployed_application_properties):
        if deployed_application_properties:
            deployeds_application_properties_dict = dict(ast.literal_eval(deployed_application_properties))
            for key in deployeds_application_properties_dict:
                pkey_xml = root.find(key)
                if not pkey_xml:
                    pkey_xml = ET.SubElement(root.find("udm.DeployedApplication"), key)
                pkey_xml.text = deployeds_application_properties_dict[key]
                
    
    def set_deployed_properties(self, root, deployed_properties):
        if deployed_properties:
            deployeds_properties_dict = dict(ast.literal_eval(deployed_properties))
            for key in deployeds_properties_dict:
                for xlr_tag_deployed in root.findall(".//deployeds/*"):
                    print 'DEBUG: deployed is %s \n' % ET.tostring(xlr_tag_deployed)
                    print 'DEBUG: xlrTag exists? %s' % xlr_tag_deployed.findtext('xlrTag')
                    print 'DEBUG: xlrTag key? %s' % key
                    if key == xlr_tag_deployed.findtext('xlrTag'):
                        deployed_properties_dict = dict(ast.literal_eval(deployeds_properties_dict[key]))
                        print 'DEBUG: deployed properties dict is %s \n' % deployed_properties_dict
                        for pkey in deployed_properties_dict:
                            pkey_xml = xlr_tag_deployed.find(pkey)
                            if not pkey_xml:
                                pkey_xml = ET.SubElement(xlr_tag_deployed, pkey)
                            pkey_xml.text = deployed_properties_dict[pkey]
                    
    
    def deployment_prepare_deployeds(self, deployment, orchestrators = None, deployed_application_properties = None, deployed_properties = None):
        deployment_prepare_deployeds = "/deployit/deployment/prepare/deployeds"
        # print 'DEBUG: Prepare deployeds for deployment object %s \n' % deployment
        deployment_prepare_deployeds_response = self.httpRequest.post(deployment_prepare_deployeds, deployment, contentType='application/xml')
        # print 'DEBUG: Deployment object including mapping is now %s \n' % deployment
        deployment_xml = deployment_prepare_deployeds_response.getResponse()
        root = ET.fromstring(deployment_xml)
        self.add_orchestrators(root, orchestrators)
        self.set_deployed_application_properties(root, deployed_application_properties)
        print 'DEBUG: Deployment object after updating orchestrators: %s \n' % ET.tostring(root)
        self.set_deployed_properties(root, deployed_properties)
        return ET.tostring(root)
    
    def get_deployment_task_id(self, deployment):
        getDeploymentTaskId = "/deployit/deployment"
        # print 'DEBUG: creating task id for deployment object %s \n' % deployment
        deploymentTaskId_response = self.httpRequest.post(getDeploymentTaskId, deployment, contentType='application/xml')
        # print 'DEBUG: getDeploymentTaskId response is %s \n' % (deploymentTaskId_response.getResponse())
        return deploymentTaskId_response.getResponse()
    
    def deploymentRollback(self, taskId):
        deploymentRollback = "/deployit/deployment/rollback/%s" % taskId
        # print 'DEBUG: calling rollback for taskId %s \n' % taskId
        deploymentRollback_response = self.httpRequest.post(deploymentRollback,'',contentType='application/xml')
        # print 'DEBUG: received rollback taskId %s \n' % deploymentRollback_response.getResponse()
        return deploymentRollback_response.getResponse()
    
    def archiveTask(self, taskId):
        archiveTask = "/deployit/task/%s/archive" % taskId
        self.httpRequest.post(archiveTask,'',contentType='application/xml')

    def cancelTask(self, taskId):
        cancelTask = "/deployit/task/%s" % taskId
        self.httpRequest.delete(cancelTask, contentType='application/xml')

    def stopTask(self, taskId):
        stopTask = "/deployit/task/%s/stop" % taskId
        self.httpRequest.post(stopTask,'',contentType='application/xml')#

    def upload_xml_list(self, applicationId, packageVersion, applicationXml):
        uploadTask = "/deployit/repository/cis" 
        try:
          uploadTask_response = self.httpRequest.post(uploadTask, applicationXml, contentType='application/xml')        
          print uploadTask_response.getResponse()
        except:
          print uploadTask_response.errorDump()
          print "unable to upload xml for application: %s, package version: %s" % (applicationId, applicationVersion)
          raise

class XLDeployClientUtil(object):

    @staticmethod
    def createXLDeployClient(container, username, password):
        client = XLDeployClient.createClient(container, username, password)
        return client

class HttpResponse:
    def getStatus(self):
        """
        Gets the status code
        :return: the http status code
        """
        return self.status

    def getResponse(self):
        """
        Gets the response content
        :return: the reponse as text
        """
        return self.response

    def isSuccessful(self):
        """
        Checks if request successful
        :return: true if successful, false otherwise
        """
        return 200 <= self.status < 400

    def getHeaders(self):
        """
        Returns the response headers
        :return: a dictionary of all response headers
        """
        return self.headers

    def errorDump(self):
        """
        Dumps the whole response
        """
        print 'Status: ', self.status, '\n'
        print 'Response: ', self.response, '\n'
        print 'Response headers: ', self.headers, '\n'

    def __init__(self, status, response, headers):
        self.status = status
        self.response = response
        self.headers = {}
        for header in headers:
            self.headers[str(header.getName())] = str(header.getValue())

class HttpRequest:
    def __init__(self, params, username = None, password = None):
        """
        Builds an HttpRequest

        :param params: an HttpConnection
        :param username: the username
            (optional, it will override the credentials defined on the HttpConnection object)
        :param password: an password
            (optional, it will override the credentials defined on the HttpConnection object)
        """
        self.params = HttpConnection(params)
        self.username = username
        self.password = password

    def doRequest(self, **options):
        """
        Performs an HTTP Request

        :param options: A keyword arguments object with the following properties :
            method: the HTTP method : 'GET', 'PUT', 'POST', 'DELETE'
                (optional: GET will be used if empty)
            context: the context url
                (optional: the url on HttpConnection will be used if empty)
            body: the body of the HTTP request for PUT & POST calls
                (optional: an empty body will be used if empty)
            contentType: the content type to use
                (optional, no content type will be used if empty)
            headers: a dictionary of headers key/values
                (optional, no headers will be used if empty)
        :return: an HttpResponse instance
        """
        request = self.buildRequest(
            options.get('method', 'GET'),
            options.get('context', ''),
            options.get('body', ''),
            options.get('contentType', None),
            options.get('headers', None))
        return self.executeRequest(request)


    def get(self, context, **options):
        """
        Performs an Http GET Request

        :param context: the context url
        :param options: the options keyword argument described in doRequest()
        :return: an HttpResponse instance
        """
        options['method'] = 'GET'
        options['context'] = context
        return self.doRequest(**options)


    def put(self, context, body, **options):
        """
        Performs an Http PUT Request

        :param context: the context url
        :param body: the body of the HTTP request
        :param options: the options keyword argument described in doRequest()
        :return: an HttpResponse instance
        """
        options['method'] = 'PUT'
        options['context'] = context
        options['body'] = body
        return self.doRequest(**options)


    def post(self, context, body, **options):
        """
        Performs an Http POST Request

        :param context: the context url
        :param body: the body of the HTTP request
        :param options: the options keyword argument described in doRequest()
        :return: an HttpResponse instance
        """
        options['method'] = 'POST'
        options['context'] = context
        options['body'] = body
        return self.doRequest(**options)


    def delete(self, context, **options):
        """
        Performs an Http DELETE Request

        :param context: the context url
        :param options: the options keyword argument described in doRequest()
        :return: an HttpResponse instance
        """
        options['method'] = 'DELETE'
        options['context'] = context
        return self.doRequest(**options)


    def buildRequest(self, method, context, body, contentType, headers):
        url = self.quote(self.createPath(self.params.getUrl(), context))

        method = method.upper()

        if method == 'GET':
            request = HttpGet(url)
        elif method == 'POST':
            request = HttpPost(url)
            request.setEntity(StringEntity(body))
        elif method == 'PUT':
            request = HttpPut(url)
            request.setEntity(StringEntity(body))
        elif method == 'DELETE':
            request = HttpDelete(url)
        else:
            raise Exception('Unsupported method: ' + method)

        request.addHeader('Content-Type', contentType)
        request.addHeader('Accept', contentType)
        self.setCredentials(request)
        self.setProxy(request)
        self.setHeaders(request, headers)

        return request


    def createPath(self, url, context):
        url = re.sub('/*$', '', url)
        if context is None:
            return url
        elif context.startswith('/'):
            return url + context
        else:
            return url + '/' + context

    def quote(self, url):
        return urllib.quote(url, ':/?&=%')


    def setCredentials(self, request):
        if self.username:
            username = self.username
            password = self.password
        elif self.params.getUsername():
            username = self.params.getUsername()
            password = self.params.getPassword()
        else:
            return

        encoding = Base64.encodeBase64String(String(username + ':' + password).getBytes())
        request.addHeader('Authorization', 'Basic ' + encoding)


    def setProxy(self, request):
        if not self.params.getProxyHost():
            return

        proxy = HttpHost(self.params.getProxyHost(), int(self.params.getProxyPort()))
        config = RequestConfig.custom().setProxy(proxy).build()
        request.setConfig(config)


    def setHeaders(self, request, headers):
        if headers:
            for key in headers:
                request.setHeader(key, headers[key])


    def executeRequest(self, request):
        client = None
        response = None
        try:
            client = HttpClients.createDefault()
            response = client.execute(request)
            status = response.getStatusLine().getStatusCode()
            entity = response.getEntity()
            result = EntityUtils.toString(entity, "UTF-8") if entity else None
            headers = response.getAllHeaders()
            EntityUtils.consume(entity)

            return HttpResponse(status, result, headers)
        finally:
            if response:
                response.close()
            if client:
                client.close()
      
# actual job


xldClient = XLDeployClientUtil.createXLDeployClient(xldeployServer, username, password)


print "uploading package xml to xldeploy"
xmlConfigData = xmlConfigData.replace(applicationIdPlaceholder,applicationId)
xmlConfigData = xmlConfigData.replace(versionPlaceholder,applicationVersion)

xldClient.upload_xml_list("Applications/%s" % (applicationId), applicationVersion, xmlConfigData)

