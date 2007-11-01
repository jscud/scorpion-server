#!/usr/bin/python
#
# Copyright (C) 2007 Jeffrey Scudder
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import os.path
import socket
import cgi
import base64
from SocketServer import BaseServer
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from OpenSSL import SSL


CONFIGURATION_DIRECTORY = 'config'
USER_DATA_FILENAME = 'users'
PERMISSIONS_DATA_FILENAME = 'permissions'
SSL_PEM_FILENAME = 'server.pem'
RESOURCE_DIRECTORY = 'hosted'
DEFAULT_RESOURCE_FILENAME = 'index'
SERVER_PORT = 443
SERVER_AUTH_REALM = 'scorpion server'


class BadCredentialsError(Exception):
  pass

  
class ScorpionResourceServer(HTTPServer):

  def __init__(self, server_address, HandlerClass):
    BaseServer.__init__(self, server_address, HandlerClass)
    ctx = SSL.Context(SSL.SSLv23_METHOD)
    # Server.pem's location (containing the server private key and
    # the server certificate).
    fpem = os.path.join(CONFIGURATION_DIRECTORY, SSL_PEM_FILENAME)
    ctx.use_privatekey_file(fpem)
    ctx.use_certificate_file(fpem)
    self.socket = SSL.Connection(ctx, socket.socket(self.address_family,
                                                    self.socket_type))
    self.server_bind()
    self.server_activate()


class UserData(object):
  
  def __init__(self, credentials_file=None, permissions_file=None):
    self.user_credentials = {}
    self.permissions = {}
    if credentials_file:
      self.LoadUserCredentials(credentials_file)
    if permissions_file:
      self.LoadPermissionsMap(permissions_file)
    
  def LoadUserCredentials(self, file_name):
    if file_name and os.path.exists(file_name):
      self.user_credentials = {}
      user_file = open(file_name, 'r')
      for line in user_file.readlines():
        line_parts = line.strip().split('\t')
        self.user_credentials[line_parts[0]] = line_parts[1]
    
  def LoadPermissionsMap(self, file_name):
    if file_name and os.path.exists(file_name):
      self.permissions = {}
      permissions_file = open(file_name, 'r')
      for line in permissions_file.readlines():
        line_parts = line.strip().split('\t')
        mode = line_parts[0]
        username = line_parts[1]
        resource = line_parts[2]
        if not self.permissions.has_key(mode):
          self.permissions[mode] = {}
        if not self.permissions[mode].has_key(username):
          self.permissions[mode][username] = []
        self.permissions[mode][username].append(resource)
    
  def AuthenticateUser(self, username, password):
    if username is None:
      return ''
    if (self.user_credentials.has_key(username) and 
        self.user_credentials[username] == password):
      return username
    else:
      return None
      
  def UserCanReadResource(self, username, resource):
    if self.UserCanWriteResource(username, resource):
      return True
    if self.permissions['r'].has_key(username):
      for allowed_resource in self.permissions['r'][username]:
        if resource.startswith(allowed_resource):
          return True
    if username != '':
      return self.UserCanReadResource('', resource)
    else:
      return False
      
  def UserCanWriteResource(self, username, resource):
    if self.permissions['w'].has_key(username):
      for allowed_resource in self.permissions['w'][username]:
        if resource.startswith(allowed_resource):
          return True
    if username != '':
      return self.UserCanWriteResource('', resource)
    else:
      return False
    
  def FindUserFromAuthHeader(self, auth_header):
    if auth_header:
      auth_string = base64.decodestring(auth_header.split(' ')[-1])
      user_pass_list = auth_string.split(':')
      username = user_pass_list[0]
      password = user_pass_list[-1]
      return self.AuthenticateUser(username, password)
    else:
      # If there was no auth header, this is the empty anonymous user.
      return ''
    
 
class DataStore(object):
  
  def __init__(self, resource_directory, default_file):
    # The directory in which all of the resources live.
    self.resource_directory = resource_directory
    # The file name to rea from or write to if the resource points
    # to a directory. Example: 'index' or 'index.html'
    self.default_file = default_file
  
  def _ConvertResourceToFileName(self, resource):
    file_parts = resource.split('/')
    full_path = self.resource_directory
    for part in file_parts:
      full_path = os.path.join(full_path, part)
    if os.path.exists(full_path):
      if os.path.isdir(full_path):
        full_path = os.path.join(full_path, self.default_file)
    return full_path
    
  def ReadResource(self, resource):
    file_name = self._ConvertResourceToFileName(resource)
    # Check to see if the user can read the resource.
    
    resource_file = open(file_name, 'rb')
    result = resource_file.read()
    resource_file.close()
    return result
    
  def ResourceExists(self, resource):
    file_name = self._ConvertResourceToFileName(resource)
    return os.path.exists(file_name)
  
  def WriteResource(self, resource, data):
    file_name = self._ConvertResourceToFileName(resource)
    resource_file = open(file_name, 'wb')
    resource_file.write(data)
    resource_file.close()
    return data
    
    
class ScorpionResourceRequestHandler(SimpleHTTPRequestHandler):

  def setup(self):
    self.connection = self.request
    self.rfile = socket._fileobject(self.request, 'rb', self.rbufsize)
    self.wfile = socket._fileobject(self.request, 'wb', self.wbufsize)
    self.user_data = UserData()
    self.user_data.LoadUserCredentials(os.path.join(CONFIGURATION_DIRECTORY,
                                                    USER_DATA_FILENAME))
    self.user_data.LoadPermissionsMap(os.path.join(CONFIGURATION_DIRECTORY,
                                                   PERMISSIONS_DATA_FILENAME))
    self.data_store = DataStore(RESOURCE_DIRECTORY, DEFAULT_RESOURCE_FILENAME)
    
  def _UserHasReadPermissions(self, resource):
    return self._UserCanPerformAction(self.user_data.UserCanReadResource, resource)
    
  def _UserHasWritePermissions(self, resource):
    return self._UserCanPerformAction(self.user_data.UserCanWriteResource, resource)
  
  def _UserCanPerformAction(self, user_may_do_action, resource):
    """Determines if auth is valid and user can perform a read or write.
    
    Args:
      user_may_do_action: Function The function which checks the 
          permisisons of the user on the resource. This is usually
          either self.user_data.UserCanReadResource or
          self.user_data.UserCanWriteResource.
      resource: str The resource which is to be read or written.
          This is usually self.path.
    """
    # Validate the credentials sent by the user.
    auth_header = self.headers.getheader('Authorization')
    user = self.user_data.FindUserFromAuthHeader(auth_header)
    # If the user's credentials were bad, send a 401 response.
    if user is None:
      self.AskUserToAuthenticate()
      print 'User sent bad credentials.'
      return False
    # Check to see if the user has permissions to read the resource.
    if not user_may_do_action(user, self.path):
      # If the user does not have permission but they are not logged in, send
      # a 401 to ask for credentials.
      if user == '':
        self.AskUserToAuthenticate()
        print 'User could not read because they were not logged in.'
        return False
      else:
        # If the user does not have permission and they are logged in, send 
        # a 403.
        self.send_error(403)
        print 'User does not have permissions to read.'
        return False
    return True
  
  def do_GET(self):
    if self._UserHasReadPermissions(self.path):
      # The user has permissions to read the resource.
      # Check to make sure that the resource is valid.
      if self.data_store.ResourceExists(self.path):
        # If the resource exists, send it!
        resource_data = self.data_store.ReadResource(self.path)
        self.wfile.write(resource_data)
        print 'Sent the resource!'
        return
      else:
        # The resource does not exist, so send a 404.
        print 'Resource not found.' 
        self.send_error(404)
        return
      
  def do_POST(self):
    if self._UserHasWritePermissions(self.path):
      data_length = int(self.headers.getheader('content-length'))
      request_body = self.rfile.read(data_length)
      print 'The request body was:', request_body
      resource_data = self.data_store.WriteResource(self.path, request_body)
      self.wfile.write(resource_data)
      print 'Wrote the resource to disk!'
      
  def AskUserToAuthenticate(self):
    realm = SERVER_AUTH_REALM
    self.wfile.write('HTTP/1.0 401 Authentication Required\n'
                       'Server: %s\n'
                       'Date: %s\n'
                       'WWW-Authenticate: Basic realm="%s"\n\n' % (
                            self.version_string(),
                            self.date_time_string(), realm))


def StartServer(HandlerClass=ScorpionResourceRequestHandler,
                ServerClass=ScorpionResourceServer):
    server_address = ('', SERVER_PORT) # (address, port)
    httpd = ServerClass(server_address, HandlerClass)
    sa = httpd.socket.getsockname()
    print 'Serving HTTPS on', sa[0], 'port', sa[1]
    httpd.serve_forever()


if __name__ == '__main__':
    StartServer()