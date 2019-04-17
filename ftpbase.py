from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
import threading


def Run_Ftp(address, port, path):
    authorizer = DummyAuthorizer()
    authorizer.add_anonymous(path)
    handler = FTPHandler
    handler.authorizer = authorizer
    server = FTPServer((address, port), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server
