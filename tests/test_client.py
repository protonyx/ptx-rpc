import unittest
import mock

import time
import threading
import requests

import ptxrpc as rpc

class RPC_Client_Connection_Tests(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        # Create a test object
        test = mock.MagicMock()
        del test._rpc
        test.test_connection = mock.MagicMock(return_value=True)

        # Start the RPC server
        self.srv = rpc.PtxRpcServer(host='localhost', port=6780)
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

    def test_connect(self):
        # Create a connection to the server
        client = rpc.PtxRpcClient(uri='http://localhost:6780/')

        # Call a dummy method
        self.assertTrue(client.test_connection())

    def test_connect_error_no_server_running(self):
        """
        Expected Failure: RpcServerNotFound
        """
        with self.assertRaises(rpc.RpcServerNotFound):
            client = rpc.PtxRpcClient(uri='http://localhost:6781/')

            client.test_connection()

    def test_connect_error_server_restarted(self):
        """
        Stop and start the server while a connection is active and verify
        that it recovers
        """
        client = rpc.PtxRpcClient(uri='http://localhost:6780/')

        self.tearDownClass()
        time.sleep(1.0)
        self.setUpClass()

        # Call a dummy method
        self.assertTrue(client.test_connection())

class RPC_Client_Method_Tests(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        # Create a test object
        self.test = mock.MagicMock()
        del self.test._rpc
        self.test.test_bool = mock.MagicMock(return_value=True)
        self.test.test_int = mock.MagicMock(return_value=1)
        self.test.test_float = mock.MagicMock(return_value=3.14)
        self.test.test_iter = mock.MagicMock(return_value=[1, '2', 3.00])
        self.test.test_dict = mock.MagicMock(return_value={'1': 'one'})
        self.test.test_except = mock.MagicMock(side_effect=RuntimeError)
        self.test.test_none = mock.MagicMock(return_value=None)
        del self.test.test_no_method

        # Start the RPC server
        self.srv = rpc.PtxRpcServer(host='localhost', port=6780)
        self.srv.register_path('/', self.test)

        # Start the server in a new thread
        self.srv_thread = threading.Thread(target=self.srv.serve_forever)
        self.srv_thread.start()

        time.sleep(1.0)

        self.client = rpc.PtxRpcClient(uri='http://localhost:6780/')

    @classmethod
    def tearDownClass(self):
        # Stop the server
        self.srv.shutdown()
        self.srv.server_close()
        self.srv_thread.join()

    def test_method_call(self):
        self.client.test_none()

    def test_method_call_return_types(self):
        data_types = ['bool', 'int', 'float', 'iter', 'dict', 'none']

        for dt in data_types:
            self.assertEqual(getattr(self.client, 'test_%s' % dt)(), getattr(self.test, 'test_%s' % dt)())

    def test_method_call_error_protected(self):
        with self.assertRaises(AttributeError):
            self.client._rpcCall('_test3')

    def test_method_call_error_not_found(self):
        with self.assertRaises(AttributeError):
            self.client._rpcCall('test_no_method')

    def test_method_call_error_exception(self):
        with self.assertRaises(rpc.RpcServerException):
            self.client.test_except()



if __name__ == '__main__':
    unittest.main()