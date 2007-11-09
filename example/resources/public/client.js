/*
 * Copyright (C) 2007 Jeffrey Scudder
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
 
var scorpion_server = {}

/**
 * Constructor for an scorpion server client object.
 *
 * The client is configured to get and set resources on the server.
 *
 * @param username {String}
 * @param password {String}
 * @param requestCallback {Function} The function to be executed after the
 *     client receives a response from the server. The callbackFunction must
 *     take two parameters, the server's status code and the body of the
 *     server's response.
 */
scorpion_server.Client = function(username, password, requestCallback) {
  if (window.XMLHttpRequest) {
    this.http = new XMLHttpRequest();
  } else if (window.ActiveXObject) {
    this.http = new ActiveXObject("Microsoft.XMLHTTP");
  }
  this.setRequestCallback(requestCallback);
  this.setCredentials(username, password);
};

/**
 * Allows changes in how the client handles a response from the server.
 *
 * The requestCallback function is called when the client receives a response
 * to a (GET or POST) request. 
 *
 * @param requestCallback {Function} The function to be executed after the
 *     client receives a response from the server. The callbackFunction must
 *     take two parameters, the server's status code and the body of the
 *     server's response.
 */
scorpion_server.Client.prototype.setRequestCallback = function(
    requestCallback) {
  this.callbackFunction = requestCallback;
  callbackThis = this;
  this.http.onreadystatechange = function() {
    if (callbackThis.http.readyState == 4) {
      requestCallback(callbackThis.http.status, 
                      callbackThis.http.responseText);
    }
  }
}

/**
 * Sets the credentials to be used on all requests.
 *
 * If credentials are provided, they will be used to create a Basic Auth 
 * header which is sent with each request.
 *
 * @param username {String} The username for Basic Auth
 * @param password {String} The password to be used in the Basic Auth header.
 */
scorpion_server.Client.prototype.setCredentials = function(username, 
    password) {
  if (username != null && password != null) {
    this.encodedCredentials = scorpion_server.encode64(
        username + ':' + password);
  } else {
    this.encodedCredentials = null;
  }
}

/**
 * The get method performs an HTTP GET request on the url.
 *
 * The request includes an Basic Authorization header if the username and
 * password of the object are set. When the client receives the server's 
 * response, it calls the callbackFunction with the status and body from
 * the server.
 *
 * @param url {String} The URL which the client will request.
 *
 */
scorpion_server.Client.prototype.get = function(url) {
  // Append a unique URL parameter to the URL to prevent IE from using a 
  // cached value instead of asking the server. The server will ignore
  // all URL parameters.
  var currentTime = new Date();
  url = [url, '?timestamp=', currentTime.toGMTString()].join('');
  this.http.open("GET", url, true);
  if (this.encodedCredentials) {
    this.http.setRequestHeader('Authorization', 
                               'Basic ' + this.encodedCredentials);
  }
  this.setRequestCallback(this.callbackFunction);
  this.http.send(null);
  // After the request is made, the onreadystatechange function is called.
  // Once the client receives the full response, the client object's 
  // this.requestCallback with the status message and body as parameters.
};

/**
 * The post method sends data to the url.
 *
 * The request includes an Basic Authorization header if the username and
 * password of the object are set. When the client receives the server's 
 * response, it calls the callbackFunction with the status and body from
 * the server.
 *
 * @param data {String} The data to be stored at this resource.
 * @param url {String} The URL which the client will request.
 *
 */
scorpion_server.Client.prototype.post = function(data, url) {
  this.http.open("POST", url, true);
  this.setRequestCallback(this.callbackFunction);
  if (this.encodedCredentials) {
    this.http.setRequestHeader('Authorization', 
                               'Basic ' + this.encodedCredentials);
  }
  this.http.send(data);
  // After the request is made, the onreadystatechange function is called.
  // Once the client receives the full response, the client object's 
  // this.requestCallback with the status message and body as parameters.
};


// This code was written by Tyler Akins and has been placed in the
// public domain.  It would be nice if you left this header intact.
// Base64 code from Tyler Akins -- http://rumkin.com

scorpion_server.keyStr = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';

scorpion_server.encode64 = function(input) {
  var output = "";
  var chr1, chr2, chr3;
  var enc1, enc2, enc3, enc4;
  var i = 0;

  do {
    chr1 = input.charCodeAt(i++);
    chr2 = input.charCodeAt(i++);
    chr3 = input.charCodeAt(i++);

    enc1 = chr1 >> 2;
    enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
    enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
    enc4 = chr3 & 63;

    if (isNaN(chr2)) {
      enc3 = enc4 = 64;
    } else if (isNaN(chr3)) {
      enc4 = 64;
    }

    output = [output, scorpion_server.keyStr.charAt(enc1), 
              scorpion_server.keyStr.charAt(enc2), 
              scorpion_server.keyStr.charAt(enc3), 
              scorpion_server.keyStr.charAt(enc4)].join('');
  } while (i < input.length);
   
  return output;
}

scorpion_server.decode64 = function(input) {
  var output = "";
  var chr1, chr2, chr3;
  var enc1, enc2, enc3, enc4;
  var i = 0;

  // remove all characters that are not A-Z, a-z, 0-9, +, /, or =
  input = input.replace(/[^A-Za-z0-9\+\/\=]/g, "");

  do {
    enc1 = scorpion_server.keyStr.indexOf(input.charAt(i++));
    enc2 = scorpion_server.keyStr.indexOf(input.charAt(i++));
    enc3 = scorpion_server.keyStr.indexOf(input.charAt(i++));
    enc4 = scorpion_server.keyStr.indexOf(input.charAt(i++));

    chr1 = (enc1 << 2) | (enc2 >> 4);
    chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);
    chr3 = ((enc3 & 3) << 6) | enc4;

    output = output + String.fromCharCode(chr1);

    if (enc3 != 64) {
      output = output + String.fromCharCode(chr2);
    }
    if (enc4 != 64) {
      output = output + String.fromCharCode(chr3);
    }
  } while (i < input.length);

  return output;
}