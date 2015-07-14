
import threading
import unittest
import mock

import ptxrpc as rpc

# TODO: Use Mock instead of the test stubs below

class ObjTest1(object):
    def test1(self):
        return 1

class ObjTest2(object):
    def test2(self):
        return 2

    def test_exception(self):
        raise RuntimeError

class RPC_Client_Connection_Tests(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        # Create a test object
        test = mock.MagicMock(return_value=True)

        # Start the RPC server
        self.srv = rpc.PtxRpcServer(host='localhost', port=6780)
        self.srv.register_path('', test)

        # Start the server in a new thread
        srv_thread = threading.Thread(target=self.srv.serve_forever)
        srv_thread.start()

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
        self.assertTrue(client.testConnection())

    def test_connect_error_no_server_running(self):
        """
        Expected Failure: RpcServerNotFound
        """
        self.assertRaises(rpc.RpcServerNotFound, rpc.PtxRpcClient, address='localhost', port=6781)

    @unittest.skip("Currently broken")
    def test_connect_error_server_restarted(self):
        """
        Stop and start the server while a connection is active and verify
        that it recovers
        """
        client = rpc.RpcClient(address='localhost', port=6780)

        self.srv.rpc_stop()
        time.sleep(1.0)

        self.srv = rpc.RpcServer(port=6780)
        t1 = ObjTest1()
        self.srv.registerObject(t1)

        self.assertEqual(client.test1(), 1)
        #self.assertRaises(rpc.RpcServerNotFound, rpc.RpcClient, address='localhost', port=6780)

class RPC_Client_Method_Tests(unittest.TestCase):

    def setUp(self):
        # Create a test object
        test = mock.MagicMock(return_value=True)

        self.srv = rpc.PtxRpcServer(port=6780)
        self.srv.register_path('', test)
        # t1 = ObjTest1()
        # t2 = ObjTest2()
        # self.srv.registerObject(t1)
        # self.srv.registerObject(t2)

        # Start the server in a new thread
        srv_thread = threading.Thread(target=self.srv.serve_forever)
        srv_thread.start()

        self.client = rpc.RpcClient(address='localhost', port=6780)

    def tearDown(self):
        # Stop the server
        self.srv.shutdown()
        self.srv.server_close()
        self.srv_thread.join()

    def test_get_methods(self):
        methods = self.client.rpc_getMethods()

        self.assertTrue('test1' in methods)

    def test_method_call(self):
        self.assertEqual(self.client.test1(), 1)
        self.assertEqual(self.client.test2(), 2)

    def test_method_call_error_protected(self):
        with self.assertRaises(rpc.RpcMethodNotFound):
            self.client._rpcCall('_test3')

    def test_method_call_error_not_found(self):
        with self.assertRaises(rpc.RpcMethodNotFound):
            self.client._rpcCall('test3')

    def test_method_call_error_exception(self):
        with self.assertRaises(rpc.RpcServerException):
            self.client.test_exception()

    def test_notification(self):
        import threading
        testVar = threading.Event()
        testVar.clear()

        self.client._enableNotifications()
        self.client._registerCallback('NOTIFICATION_TEST', lambda: testVar.set())

        self.srv.notifyClients('NOTIFICATION_TEST')

        self.client._checkNotifications()

        self.assertTrue(testVar.is_set())
