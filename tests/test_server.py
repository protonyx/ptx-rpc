import unittest
import mock

import threading
import requests

import ptxrpc as rpc
    
class RPC_Server_Functional_Tests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.srv = rpc.PtxRpcServer('localhost', 6780)

        # Start the server in a new thread
        cls.srv_thread = threading.Thread(target=cls.srv.serve_forever)
        cls.srv_thread.start()

    @classmethod
    def tearDownClass(cls):
        # Stop the thread
        cls.srv.shutdown()
        cls.srv.server_close()
        cls.srv_thread.join()

    def test_server_port(self):
        self.assertEqual(self.srv.getPort(), 6780)

    @unittest.skip("Not working")
    def test_server_error_already_running(self):
        with self.assertRaises(rpc.RpcServerPortInUse):
            srv2 = rpc.PtxRpcServer('', 6780)

    def test_invalid_path(self):
        resp = requests.post('http://localhost:6780/invalid', data='')
        self.assertEqual(resp.status_code, 404)

    def test_unregister_path(self):
        stub = mock.Mock()

        self.srv.register_path('/test', stub)

        resp = requests.post('http://localhost:6780/test', data='')
        self.assertEqual(resp.status_code, 200)

        self.srv.unregister_path('/test')

        resp = requests.post('http://localhost:6780/invalid', data='')
        self.assertEqual(resp.status_code, 404)

    def test_get(self):
        resp = requests.get('http://localhost:6780/', data='')
        self.assertEqual(resp.status_code, 200)

    def test_uptime(self):
        self.srv.getUptime()


if __name__ == '__main__':
    unittest.main()