import unittest

import threading
import requests

import ptxrpc as rpc
    
class RPC_Server_Functional_Tests(unittest.TestCase):
    def test_server_init_thread(self):
        srv = rpc.PtxRpcServer('', 6780)

        # Start the server in a new thread
        srv_thread = threading.Thread(target=srv.serve_forever)
        srv_thread.start()

        self.assertEqual(srv.getPort(), 6780)

        # Stop the thread
        srv.shutdown()
        srv.server_close()
        srv_thread.join()

    def test_server_error_already_running(self):
        srv = rpc.PtxRpcServer('', 6780)

        # Start the server in a new thread
        srv_thread = threading.Thread(target=srv.serve_forever)
        srv_thread.start()
        
        with self.assertRaises(rpc.RpcServerPortInUse):
            srv2 = rpc.PtxRpcServer('', 6780)

            # shutdown the server in case the error was not thrown
            srv_thread2 = threading.Thread(target=srv.serve_forever)
            srv_thread2.start()
            srv2.shutdown()
            srv_thread2.join()

            # fail the test if we got to this point
            raise RuntimeError("Test Failed, Port should have been in use but wasn't")
        
        srv.shutdown()
        srv.server_close()
        srv_thread.join()

    def test_invalid_path(self):
        srv = rpc.PtxRpcServer('', 6780)

        # Start the server in a new thread
        srv_thread = threading.Thread(target=srv.serve_forever)
        srv_thread.start()

        resp = requests.post('http://localhost:6780/invalid', data='')
        self.assertEqual(resp.status_code, 404)

        srv.shutdown()
        srv.server_close()
        srv_thread.join()

    def test_get(self):
        srv = rpc.PtxRpcServer('', 6780)

        # Start the server in a new thread
        srv_thread = threading.Thread(target=srv.serve_forever)
        srv_thread.start()

        resp = requests.get('http://localhost:6780/', data='')
        self.assertEqual(resp.status_code, 200)

        srv.shutdown()
        srv.server_close()
        srv_thread.join()

if __name__ == '__main__':
    unittest.main()