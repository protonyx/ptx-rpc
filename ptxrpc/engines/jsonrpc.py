"""
JSON RPC Python class for PTX-RPC

Conforms to the JSON RPC 2.0 Spec (http://www.jsonrpc.org/specification) with
a small addition to allow for both positional and keyword arguments

This class can either be instantiated with a JSON encoded string or used as 
a utility helper class
"""
import json

from .. import errors
from . import RpcRequest, RpcResponse, RpcError

def get_content_type():
    return 'application/json'

#===============================================================================
# Error Type
#===============================================================================
                 
class JsonRpc_Error(errors.RpcError):
    code = None
    message = None
    data = None

    def __init__(self, **rpc_dict):
        RuntimeError.__init__(self)
        
        self.id = rpc_dict.get('id', None)
        
        if 'error' in rpc_dict:
            error = rpc_dict.get('error', {})
            self.code = error.get('code', None)
            self.message = error.get('message', None)
        
    def __str__(self):
        return repr(str(self.message))
        
    def export(self):
        return {'id': self.id,
                'error': {'code': self.code, 'message': self.message}}

class JsonRpc_ParseError(errors.RpcInvalidPacket):
    code = -32700
    message = 'Invalid JSON was received by the server.'

class JsonRpc_InvalidRequest(errors.RpcInvalidPacket):
    code = -32600
    message = 'The JSON sent is not a valid Request object.'

class JsonRpc_MethodNotFound(errors.RpcMethodNotFound):
    code = -32601
    message = 'The method does not exist / is not available.'

class JsonRpc_InvalidParams(errors.RpcServerException):
    code = -32602
    message = 'Invalid method parameter(s).'

class JsonRpc_InternalError(errors.RpcServerException):
    code = -32603
    message = 'Internal JSON-RPC error.'

class JsonRpc_ServerException(errors.RpcServerException):
    code = -32000
    message = 'An unhandled server exception occurred'

JsonRpcErrors = {  -32700: JsonRpc_ParseError,
                   -32600: JsonRpc_InvalidRequest,
                   -32601: JsonRpc_MethodNotFound,
                   -32602: JsonRpc_InvalidParams,
                   -32603: JsonRpc_InternalError,
                   -32000: JsonRpc_ServerException  } 
                 # -32000 to -32099 are reserved server-errors

JsonRpc_error_map = {
                    errors.RpcInvalidPacket: JsonRpc_InvalidRequest,
                    errors.RpcMethodNotFound: JsonRpc_MethodNotFound,
                    errors.RpcServerException: JsonRpc_ServerException
                    }

#===============================================================================
# Request Type
#===============================================================================
               
class JsonRpc_Request(RpcRequest):
    def __init__(self, **rpc_dict):
        self.id = rpc_dict.get('id', None)
        self.method = rpc_dict.get('method', '')

        # decode arguments
        args = rpc_dict.get('params', [])
        kwargs = rpc_dict.get('kwargs', {})

        if type(args) == dict:
            self.kwargs = args
            self.args = []

        else:
            self.kwargs = kwargs
            self.args = args
        
    def getID(self):
        return self.id
    
    def getMethod(self):
        return self.method
        
    def export(self):
        # Slight modification of the JSON RPC 2.0 specification to allow 
        # both positional and named parameters
        # Adds kwargs variable to object only when both are present
        out = {'jsonrpc': '2.0',
               'id': self.id,
               'method': self.method }

        if len(self.args) > 0:
            out['params'] = self.args
            if len(self.kwargs) > 0:
                out['kwargs'] = self.kwargs
            
        elif len(self.args) == 0:
            out['params'] = self.kwargs
            
        return out
        
#===============================================================================
# Response Type
#===============================================================================

class JsonRpc_Response(RpcResponse):
    def __init__(self, **rpc_dict):

        self.id = rpc_dict.get('id', None)
        self.result = rpc_dict.get('result', None)
        
    def getID(self):
        return self.id
        
    def getResult(self):
        return self.result
        
    def export(self):
        ret = {'jsonrpc': '2.0',
               'id': self.id,
               'result': self.result}
            
        return ret
     
#===============================================================================
# JSON RPC Handlers
#===============================================================================

def _parseJsonRpcObject(self, rpc_dict):
    """
    Takes a dictionary and determines if it is an RPC request or response
    """
    if rpc_dict.get('jsonrpc') == '2.0':
        if 'method' in rpc_dict.keys() and type(rpc_dict.get('method')) is unicode:
            # Request object
            self.requests.append(JsonRpc_Request(**rpc_dict))

        elif 'id' in rpc_dict.keys() and 'result' in rpc_dict.keys():
            # Result response object
            self.responses.append(JsonRpc_Response(**rpc_dict))

        elif 'id' in rpc_dict.keys() and 'error' in rpc_dict.keys():
            # Error response object
            error_code = rpc_dict['error'].get('code', -32700)
            err_obj = JsonRpcErrors.get(error_code, JsonRpc_ParseError)

            self.errors.append(err_obj(**rpc_dict))

        else:
            self.errors.append(JsonRpc_InvalidRequest(**rpc_dict))

    else:
        return JsonRpc_InvalidRequest()

def decode(data):
    """

    :param data:
    :return: (requests, responses, errors)
    """
    requests = []
    responses = []
    errors = []

    try:
        req = json.loads(data)

        if type(req) == list:
            # Batch request
            for sub_req in req:
                try:
                    res = _parseJsonRpcObject(sub_req)
                    if isinstance(res, RpcRequest):
                        requests.append(res)
                    elif isinstance(res, RpcResponse):
                        responses.append(res)
                    elif isinstance(res, RpcError):
                        errors.append(res)

                except:
                    errors.append(JsonRpc_InvalidRequest())

            if len(req) == 0:
                errors.append(JsonRpc_InvalidRequest())

        elif type(req) == dict:
            # Single request
            res = _parseJsonRpcObject(req)
            if isinstance(res, RpcRequest):
                requests.append(res)
            elif isinstance(res, RpcResponse):
                responses.append(res)
            elif isinstance(res, RpcError):
                errors.append(res)

        else:
            errors.append(JsonRpc_ParseError())

    except:
        # No JSON object could be decoded
        errors.append(JsonRpc_ParseError())

    return (requests, responses, errors)

def encode(requests, responses, errors):
    """

    :param requests:
    :param responses:
    :param errors:
    :return: str
    """
    ret = []

    for rpc_obj in requests + responses + errors:
        rpc_dict = rpc_obj.export()

        ret.append(rpc_dict)

    if len(ret) == 1:
        return str(json.dumps(ret[0]))
    elif len(ret) > 1:
        return str(json.dumps(ret))
    else:
        return ''
