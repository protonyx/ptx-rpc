
#===============================================================================
# Error Base Classes
#===============================================================================

class RpcError(RuntimeError):
    pass

class RpcServerPortInUse(RpcError):
    pass

class RpcServerNotFound(RpcError):
    pass

class RpcServerUnresponsive(RpcError):
    pass

class RpcTimeout(RpcError):
    pass

class RpcServerException(RpcError):
    pass

class RpcInvalidPacket(RpcError):
    pass

class RpcMethodNotFound(RpcError):
    pass


    

