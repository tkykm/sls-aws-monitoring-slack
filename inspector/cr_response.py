'''
The MIT License (MIT)

Copyright (c) 2015 base2Services

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import logging
from urllib.request import urlopen, Request, HTTPError, URLError
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class CustomResourceResponse:
    def __init__(self, request_payload, context):
        self.payload = request_payload
        self.response = {
            "StackId": request_payload["StackId"],
            "RequestId": request_payload["RequestId"],
            "LogicalResourceId": request_payload["LogicalResourceId"],
            "Status": 'SUCCESS',
        }
        self.context = context
        
    def respond_error(self, message):
        self.response['Status'] = 'FAILED'
        self.response['Reason'] = message
        self.respond()
    
    def respond(self):
        event = self.payload
        response = self.response
        ####
        #### copied from https://github.com/ryansb/cfn-wrapper-python/blob/master/cfn_resource.py
        ####
        
        if event.get("PhysicalResourceId", False):
            response["PhysicalResourceId"] = event["LogicalResourceId"]
        response['PhysicalResourceId'] = self.context.log_stream_name     


        logger.debug("Received %s request with event: %s" % (event['RequestType'], json.dumps(event)))
        
        serialized = json.dumps(response)
        logger.info(f"Responding to {event['RequestType']} request with: {serialized}")
        
        req_data = serialized.encode('utf-8')
        
        req = Request(
            event['ResponseURL'],
            data=req_data,
            headers={'Content-Length': len(req_data),'Content-Type': ''}
        )
        req.get_method = lambda: 'PUT'
        
        try:
            urlopen(req)
            logger.debug("Request to CFN API succeeded, nothing to do here")
        except HTTPError as e:
            logger.error("Callback to CFN API failed with status %d" % e.code)
            logger.error("Response: %s" % e.reason)
        except URLError as e:
            logger.error("Failed to reach the server - %s" % e.reason)
