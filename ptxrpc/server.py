import threading
import Queue
import socket
import select
import logging
import inspect
import errno
from datetime import datetime


import SocketServer
import BaseHTTPServer

# Local Imports
import engines
from errors import *
from engines import RpcRequest, RpcResponse


class PtxRpcServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    """
    Flexible RPC server that attaches to a TCP socket. Used to generate a REST API
    with a flexible architecture for RPC.

    :param requestHandler: object to handle requests
    :type requestHandler: HTTPRequestHandler object
    :param logger: Logger instance if you wish to override the internal instance
    :type logger: Logging.logger
    :param port: Port to attach srv_socket to
    :type port: int
    
    .. note::

        Method calls to functions that begin with an underscore are considered 
        protected and will not be invoked
    """

    DEBUG_RPC_SERVER = False

    allow_reuse_address = True
    
    def __init__(self, host, port, **kwargs):
        try:
            SocketServer.TCPServer.__init__(self, (host, port), self.RpcDispatcher)
        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                raise RpcServerPortInUse()

        self.logger = kwargs.get('logger', logging)
        self.port = kwargs.get('port', 0)
        self.name = 'RpcServer'

        # Encode/Decode Engine, jsonrpc is the default
        engine_name = kwargs.get('engine', 'jsonrpc')
        import importlib
        self.engine = importlib.import_module('ptxrpc.engines.%s' % engine_name)
        #self.engine = getattr(engines, engine)
            
        # RPC Path Handlers
        self.rpc_paths = {}
        self.rpc_locks = {}

        self.rpc_startTime = datetime.now()

        if self.DEBUG_RPC_SERVER:
            self.logger.debug('[%s] RPC Server started on port %i', self.name, self.port)

        # Update port if randomly assigned
        self.address, self.port = self.socket.getsockname()

    #===========================================================================
    # RPC Request Dispatcher
    #===========================================================================

    class RpcDispatcher(BaseHTTPServer.BaseHTTPRequestHandler):

        def rpc_path_valid(self):
            return self.path in self.server.rpc_paths

        def rpc_getMethods(self, target):
            """
            Get a list of valid methods in the registered objects. Protected methods
            that begin with an underscore ('_') are not included.

            :returns: list of strings
            """
            # Catalog methods
            validMethods = []

            target_members = inspect.getmembers(target)

            for attr, val in target_members:
                if inspect.ismethod(val) and not attr.startswith('_'):
                    validMethods.append(attr)

            return validMethods

        def do_POST(self):
            """
            Handle all POST requests as RPC requests
            """
            if not self.rpc_path_valid():
                self.error_404()
                return

            try:
                # Get data
                data_size = int(self.headers["content-length"])
                max_chunk_size = 4*1024 # 4K
                data = ''
                while data_size > 0:
                    chunk_size = min(data_size, max_chunk_size)
                    chunk = self.rfile.read(chunk_size)
                    if not chunk:
                        break
                    data += chunk
                    data_size -= len(chunk)

                # Process request, catch all errors
                response = self.rpc_process(data)

            except Exception as e:
                # Unhandled server exception
                self.send_response(500)
                self.send_header("Content-length", "0")
                self.end_headers()

            else:
                try:
                    content_type = self.server.engine.get_content_type()
                except:
                    content_type = 'text'

                self.send_response(200)
                self.send_header("Content-type", content_type)
                self.send_header("Content-length", str(len(response)))
                self.end_headers()
                self.wfile.write(response)

        def do_GET(self):
            """
            Handle GET requests

            Data to send to requester:
            version
            uptime
            connection info?
            hostname?

            if on root (server) path:
                list of registered objects and paths
            """
            response = 'GET test'
            self.send_response(200)
            self.send_header("Content-length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

        def rpc_process(self, data):
            engine = self.server.engine
            target = self.server.rpc_paths.get(self.path)
            lock   = self.server.rpc_locks.get(self.path)

            # Decode the incoming data
            requests, responses, errors = engine.decode(data)

            # Process responses
            for resp in responses:
                # TODO: Figure out what to do with responses
                # For now, ignore all responses
                responses.remove(resp)

            # Process errors
            for err in errors:
                # TODO: Log all errors received from a client
                errors.remove(err)

            # Process requests
            for req in requests:
                method_name = req.method
                req_id = req.id

                try:
                    with lock:
                        # RPC hook for target objects, allows the object to dispatch the request
                        if hasattr(target, '_rpc'):
                            result = target._rpc(method_name)

                        elif not method_name.startswith('_') and hasattr(target, method_name):
                            method = getattr(target, method_name)
                            result = req.call(method)

                        else:
                            responses.append(RpcMethodNotFound(id=req_id))
                            break

                    # Check if the request was a notification
                    if req_id is not None:
                        responses.append(RpcResponse(id=req_id, result=result))

                # Catch exceptions during method execution
                # DO NOT ALLOW ANY EXCEPTIONS TO PASS THIS LEVEL
                except Exception as e:
                    # Catch-all for everything else
                    excp = RpcServerException(id=req_id)
                    excp.message = e.__class__.__name__
                    responses.append(excp)

                    self.logger.exception("RPC Server Exception")

                # Remove the request from the queue
                requests.remove(req)

            # Encode the outgoing data
            out_data = engine.encode(requests, responses, errors)
            # TODO: Catch exceptions during engine encode

            return out_data


        def error_404(self):
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-length", "0")
            self.end_headers()

    #===========================================================================
    # Server Management
    #===========================================================================

    def register_path(self, path, object):
        self.rpc_paths[path] = object
        # Create a new lock for this object
        self.rpc_locks[path] = threading.Lock()

    def unregister_path(self, path):
        self.rpc_paths.pop(path)
        self.rpc_locks.pop(path)

    def getPort(self):
        """
        Get the port the socket is bound to

        :return:
        """
        return self.port

    def getUptime(self):
        """
        Get the uptime (in seconds) that the RpcServer has been running
        
        :returns: float
        """
        delta = datetime.now() - self.rpc_startTime
        return delta.total_seconds()
