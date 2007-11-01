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

import scorpion_server.server

scorpion_server.server.CONFIGURATION_DIRECTORY = 'config'
scorpion_server.server.USER_DATA_FILENAME = 'users'
scorpion_server.server.PERMISSIONS_DATA_FILENAME = 'permissions'
scorpion_server.server.SSL_PEM_FILENAME = 'server.pem'
scorpion_server.server.RESOURCE_DIRECTORY = 'resources'
scorpion_server.server.DEFAULT_RESOURCE_FILENAME = '_index'

scorpion_server.server.StartServer()