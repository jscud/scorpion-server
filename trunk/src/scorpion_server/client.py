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

import urllib2
import base64


class ScorpionClient(object):

  def __init__(self, username=None, password=None):
    self.__headers = {}
    self.__username = username
    self.__password = password
    
  def SetCredentials(self, username, password):
    self.__username = username
    self.__password = password
    self._GenerateAuthHeader()

  def _GenerateAuthHeader(self):
    to_encode = ':'.join([self.__username, self.__password])
    encoded = base64.encodestring(to_encode).strip()
    self.__headers['Authorization'] = 'Basic %s' % encoded.strip()
    
  def Read(self, url):
    request = urllib2.Request(url, None, self.__headers)
    response = urllib2.urlopen(request)
    return response.read()
    
  def Write(self, url, data):
    request = urllib2.Request(url, data, self.__headers)
    response = urllib2.urlopen(request)
    return response.read()
  