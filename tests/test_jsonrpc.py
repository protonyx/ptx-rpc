import unittest
import mock

import threading
import requests

import ptxrpc.engines.jsonrpc as jsonrpc
import ptxrpc as rpc
    
class RPC_Server_JsonRpc_Tests(unittest.TestCase):
    """
    Test the functionality of the server using the jsonrpc engine

    Bypasses the client class to send commands directly to the server.

    Uses the requests library to simplify unittest code
    """

    @classmethod
    def setUpClass(self):
        # Create a test object
        test = mock.MagicMock()
        del test._rpc
        test.subtract = lambda subtrahend, minuend: int(subtrahend) - int(minuend)
        test.foobar = mock.MagicMock(return_value=None)
        test.raise_exception = mock.MagicMock(side_effect=RuntimeError)

        # Start the RPC server
        self.srv = rpc.PtxRpcServer(host='localhost', port=6780, engine='jsonrpc')
        self.srv.register_path('/', test)

        # Start the server in a new thread
        self.srv_thread = threading.Thread(target=self.srv.serve_forever)
        self.srv_thread.start()

    @classmethod
    def tearDownClass(self):
        # Stop the server
        self.srv.shutdown()
        self.srv.server_close()
        self.srv_thread.join()
    
    def test_request_call_multi_pos_param(self):
        req = '{"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}'

        resp = requests.post('http://localhost:6780/', data=req)
        self.assertEqual(resp.status_code, 200)

        rpc_req, rpc_resp, rpc_err = jsonrpc.decode(resp.content)

        self.assertEqual(len(rpc_req), 0)
        self.assertEqual(len(rpc_resp), 1)
        self.assertEqual(len(rpc_err), 0)

        rpc_resp = rpc_resp[0]
        self.assertEqual(rpc_resp.result, 19)
        self.assertEqual(rpc_resp.id, 1)

    def test_request_call_multi_named_param(self):
        req = '{"jsonrpc": "2.0", "method": "subtract", "params": {"subtrahend": 42, "minuend": 23}, "id": 3}'

        resp = requests.post('http://localhost:6780/', data=req)
        self.assertEqual(resp.status_code, 200)

        rpc_req, rpc_resp, rpc_err = jsonrpc.decode(resp.content)

        self.assertEqual(len(rpc_req), 0)
        self.assertEqual(len(rpc_resp), 1)
        self.assertEqual(len(rpc_err), 0)

        rpc_resp = rpc_resp[0]
        self.assertEqual(rpc_resp.result, 19)
        self.assertEqual(rpc_resp.id, 3)

    def test_request_call_no_params(self):
        req = '{"jsonrpc": "2.0", "method": "foobar", "id": 2}'

        resp = requests.post('http://localhost:6780/', data=req)
        self.assertEqual(resp.status_code, 200)

        rpc_req, rpc_resp, rpc_err = jsonrpc.decode(resp.content)

        self.assertEqual(len(rpc_req), 0)
        self.assertEqual(len(rpc_resp), 1)
        self.assertEqual(len(rpc_err), 0)

        rpc_resp = rpc_resp[0]
        self.assertEqual(rpc_resp.result, None)
        self.assertEqual(rpc_resp.id, 2)

    def test_request_call_multi_combo_param(self):
        req = '{"jsonrpc": "2.0", "method": "subtract", "params": [42], "kwargs": {"minuend": 23}, "id": 3}'

        resp = requests.post('http://localhost:6780/', data=req)
        self.assertEqual(resp.status_code, 200)

        rpc_req, rpc_resp, rpc_err = jsonrpc.decode(resp.content)

        self.assertEqual(len(rpc_req), 0)
        self.assertEqual(len(rpc_resp), 1)
        self.assertEqual(len(rpc_err), 0)

        rpc_resp = rpc_resp[0]
        self.assertEqual(rpc_resp.result, 19)
        self.assertEqual(rpc_resp.id, 3)

    def test_request_call_exception(self):
        req = '{"jsonrpc": "2.0", "method": "raise_exception", "id": 4}'

        resp = requests.post('http://localhost:6780/', data=req)
        self.assertEqual(resp.status_code, 200)

        rpc_req, rpc_resp, rpc_err = jsonrpc.decode(resp.content)

        self.assertEqual(len(rpc_req), 0)
        self.assertEqual(len(rpc_resp), 0)
        self.assertEqual(len(rpc_err), 1)

        rpc_err = rpc_err[0]
        self.assertEqual(type(rpc_err), jsonrpc.JsonRpc_ServerException)

    def test_request_error_invalid_json(self):
        req = '{"jsonrpc": "2.0", "method": "foobar, "params": "bar", "baz]'
        
        resp = requests.post('http://localhost:6780/', data=req)
        self.assertEqual(resp.status_code, 200)

        rpc_req, rpc_resp, rpc_err = jsonrpc.decode(resp.content)

        self.assertEqual(len(rpc_req), 0)
        self.assertEqual(len(rpc_resp), 0)
        self.assertEqual(len(rpc_err), 1)

        rpc_err = rpc_err[0]
        self.assertEqual(type(rpc_err), jsonrpc.JsonRpc_ParseError)

    def test_request_error_invalid_request(self):
        req = '{"jsonrpc": "2.0", "method": 1, "params": "bar"}'
        
        resp = requests.post('http://localhost:6780/', data=req)
        self.assertEqual(resp.status_code, 200)

        rpc_req, rpc_resp, rpc_err = jsonrpc.decode(resp.content)

        self.assertEqual(len(rpc_req), 0)
        self.assertEqual(len(rpc_resp), 0)
        self.assertEqual(len(rpc_err), 1)

        rpc_err = rpc_err[0]
        self.assertEqual(type(rpc_err), jsonrpc.JsonRpc_InvalidRequest)

    def test_request_error_parse_empty_request(self):
        req = '{}'
        
        resp = requests.post('http://localhost:6780/', data=req)
        self.assertEqual(resp.status_code, 200)

        rpc_req, rpc_resp, rpc_err = jsonrpc.decode(resp.content)

        self.assertEqual(len(rpc_req), 0)
        self.assertEqual(len(rpc_resp), 0)
        self.assertEqual(len(rpc_err), 1)

        rpc_err = rpc_err[0]
        self.assertEqual(type(rpc_err), jsonrpc.JsonRpc_InvalidRequest)

    def test_request_error_batch_invalid_json(self):
        req = '[\
                        {"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"},\
                        {"jsonrpc": "2.0", "method"\
                    ]'
        
        resp = requests.post('http://localhost:6780/', data=req)
        self.assertEqual(resp.status_code, 200)

        rpc_req, rpc_resp, rpc_err = jsonrpc.decode(resp.content)

        self.assertEqual(len(rpc_req), 0)
        self.assertEqual(len(rpc_resp), 0)
        self.assertEqual(len(rpc_err), 1)

        rpc_err = rpc_err[0]
        self.assertEqual(type(rpc_err), jsonrpc.JsonRpc_ParseError)

    def test_request_error_batch_empty(self):
        req = '[]'
        
        resp = requests.post('http://localhost:6780/', data=req)
        self.assertEqual(resp.status_code, 200)

        rpc_req, rpc_resp, rpc_err = jsonrpc.decode(resp.content)

        self.assertEqual(len(rpc_req), 0)
        self.assertEqual(len(rpc_resp), 0)
        self.assertEqual(len(rpc_err), 1)

        rpc_err = rpc_err[0]
        self.assertEqual(type(rpc_err), jsonrpc.JsonRpc_InvalidRequest)

    def test_request_error_batch_invalid_nonempty(self):
        req = '[1]'
        
        resp = requests.post('http://localhost:6780/', data=req)
        self.assertEqual(resp.status_code, 200)

        rpc_req, rpc_resp, rpc_err = jsonrpc.decode(resp.content)

        self.assertEqual(len(rpc_req), 0)
        self.assertEqual(len(rpc_resp), 0)
        self.assertEqual(len(rpc_err), 1)

        rpc_err = rpc_err[0]
        self.assertEqual(type(rpc_err), jsonrpc.JsonRpc_InvalidRequest)

    def test_request_error_parse_invalid_batch(self):
        req = '[1,2,3]'
        
        resp = requests.post('http://localhost:6780/', data=req)
        self.assertEqual(resp.status_code, 200)

        rpc_req, rpc_resp, rpc_err = jsonrpc.decode(resp.content)

        self.assertEqual(len(rpc_req), 0)
        self.assertEqual(len(rpc_resp), 0)
        self.assertEqual(len(rpc_err), 3)

        self.assertEqual(type(rpc_err[0]), jsonrpc.JsonRpc_InvalidRequest)
        self.assertEqual(type(rpc_err[1]), jsonrpc.JsonRpc_InvalidRequest)
        self.assertEqual(type(rpc_err[2]), jsonrpc.JsonRpc_InvalidRequest)

    def test_request_batch(self):
        req = '[{"jsonrpc": "2.0", "method": "subtract", "params": [100, 10], "id": 1}, \
                {"jsonrpc": "2.0", "method": "subtract", "params": [99, 11], "id": 2}]'

        resp = requests.post('http://localhost:6780/', data=req)
        self.assertEqual(resp.status_code, 200)

        rpc_req, rpc_resp, rpc_err = jsonrpc.decode(resp.content)

        self.assertEqual(len(rpc_req), 0)
        self.assertEqual(len(rpc_resp), 2)
        self.assertEqual(len(rpc_err), 0)

        self.assertEqual(rpc_resp[0].result, 90)
        self.assertEqual(rpc_resp[0].id, 1)
        self.assertEqual(rpc_resp[1].result, 88)
        self.assertEqual(rpc_resp[1].id, 2)

        