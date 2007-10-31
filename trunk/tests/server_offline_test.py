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
import unittest
import scorpion_server.server


class UserDataTest(unittest.TestCase):

  def setUp(self):
    self.user_data = scorpion_server.server.UserData()
    self.user_data.LoadUserCredentials(os.path.join('test_config', 
                                                    'good_users'))
    self.user_data.LoadPermissionsMap(os.path.join('test_config', 
                                                   'good_permissions'))

  def testAuthenticateUser(self):
    self.assertEquals(self.user_data.AuthenticateUser('jeff', 'test'), 
                      'jeff')
    self.assertEquals(self.user_data.AuthenticateUser('jeff', 'test2'), None)
    self.assertEquals(self.user_data.AuthenticateUser(None, None), '')
    
  def testUserCanWriteResource(self):
    self.assertEquals(self.user_data.UserCanWriteResource('jeff', '/jeff'), 
                      True)
    self.assertEquals(self.user_data.UserCanWriteResource('jeff', 
        '/jeff/something else'), True)
    self.assertEquals(self.user_data.UserCanWriteResource('jeff', 
        '/jeffrey'), True)
    self.assertEquals(self.user_data.UserCanWriteResource('jeff', 
        '/jef/more'), False)
    self.assertEquals(self.user_data.UserCanWriteResource('', '/jeff'),
                      False)
    self.assertEquals(self.user_data.UserCanWriteResource('', '/jeff/more'),
                      False)
    
  def testUserCanReadResource(self):
    self.assertEquals(self.user_data.UserCanReadResource('jeff', '/jeff'), 
                      True)
    self.assertEquals(self.user_data.UserCanReadResource('jeff', 
        '/jeff/something else'), True)
    self.assertEquals(self.user_data.UserCanReadResource('jeff', '/jeffrey'),
                      True)
    self.assertEquals(self.user_data.UserCanReadResource('jeff', '/jef/more'),
                      False)
    self.assertEquals(self.user_data.UserCanReadResource('', '/jeff'), False)
    self.assertEquals(self.user_data.UserCanReadResource('', '/jeff/more'), 
                      False)
    self.assertEquals(self.user_data.UserCanReadResource('jeff', '/shared'), 
                      True)
    self.assertEquals(self.user_data.UserCanReadResource('jeff', 
        '/shared_stuff'), True)
    self.assertEquals(self.user_data.UserCanReadResource('jeff', 
        '/shared/stuff'), True)
    self.assertEquals(self.user_data.UserCanReadResource('', '/index'), True)
    self.assertEquals(self.user_data.UserCanReadResource('', '/ind'), False)
    self.assertEquals(self.user_data.UserCanReadResource('', '/index_data'), 
                      True)
    self.assertEquals(self.user_data.UserCanReadResource('', '/index/data'), 
                      True)
    self.assertEquals(self.user_data.UserCanReadResource('jeff', 
        '/index/data'), True)
    self.assertEquals(self.user_data.UserCanReadResource('jeff', '/ind'),
                      False)
    self.assertEquals(self.user_data.UserCanReadResource('jeff', '/index'),
                      True)
    
  def testLoadNormalUserCredentials(self):
    self.user_data.LoadUserCredentials(os.path.join('test_config', 'good_users'))
    self.assertEquals(self.user_data.user_credentials.has_key('jeff'), True)
    self.assertEquals(self.user_data.user_credentials['jeff'], 'test')
    self.assertEquals(self.user_data.user_credentials.has_key('doug'), True)
    self.assertEquals(self.user_data.user_credentials['doug'], 'password')
    self.assertEquals(self.user_data.user_credentials.has_key('dave'), True)
    self.assertEquals(self.user_data.user_credentials['dave'], '12345')
    self.assertEquals(self.user_data.user_credentials.has_key('jim'), True)
    self.assertEquals(self.user_data.user_credentials['jim'], 'p4s5\\/\\/0rd')
    
  def testLoadNormalPermissions(self):
    self.user_data.LoadPermissionsMap(os.path.join('test_config', 
                                                   'good_permissions'))
    self.assertEquals(self.user_data.permissions.has_key('w'), True)
    self.assertEquals(self.user_data.permissions['w'], {'jeff': ['/jeff']})
    self.assertEquals(self.user_data.permissions.has_key('r'), True)
    self.assertEquals(self.user_data.permissions['r'], {'jeff': ['/shared'], 
                                                        '': ['/index']})
    
  def testFindUserFromAuthHeader(self):
    self.assertEquals(self.user_data.FindUserFromAuthHeader(
        'Basic amVmZjp0ZXN0'), 'jeff')
    self.assertEquals(self.user_data.FindUserFromAuthHeader(None), '')
    self.assert_(self.user_data.FindUserFromAuthHeader(
        'Basic amVmZjp0ZXM=') is None)
    self.assert_(self.user_data.FindUserFromAuthHeader(
        'Basic amVmOnRlc3Q=') is None)
    
    
    
    
class DataStoreTest(unittest.TestCase):

  def setUp(self):
    self.data = scorpion_server.server.DataStore('test_hosted', 'index')
    
  def testConvertingResourceToFileName(self):
    self.assertEquals(self.data._ConvertResourceToFileName('/'), 
                      'test_hosted/index')
    self.assertEquals(self.data._ConvertResourceToFileName('/happy'), 
                      'test_hosted/happy')
    self.assertEquals(self.data._ConvertResourceToFileName('/test'), 
                      'test_hosted/test/index')
    self.assertEquals(self.data._ConvertResourceToFileName('/test/index'),
                      'test_hosted/test/index')
    self.assertEquals(self.data._ConvertResourceToFileName('/test/happy'),
                      'test_hosted/test/happy')
    
  def testResourceExists(self):
    self.assertEquals(self.data.ResourceExists('testfile'), True)
    self.assertEquals(self.data.ResourceExists('doesNotExist'), False)
    self.assertEquals(self.data.ResourceExists('also non-existant'), False)
    
  def testWriteToFileThenRead(self):
    self.assertEquals(self.data.WriteResource('testfile', 'This is a test'), 
                      'This is a test')
    self.assertEquals(self.data.ReadResource('testfile'), 'This is a test')
    
    
if __name__ == '__main__':
  unittest.main()