__author__ = 'kkennedy'

__all__ = ['jsonrpc']

class RpcRequest(object):
    def __init__(self):
        self.method = ''
        self.args = []
        self.kwargs = {}

    def call(self, target):
        # Invoke target method with stored arguments
        # Don't attempt to catch exceptions here, let them bubble up
        return target(*self.params, **self.kwargs)

class RpcResponse(object):
    pass

class RpcError(object):
    pass