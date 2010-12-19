from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

class RequestHandler(SimpleXMLRPCRequestHandler):
	rpc_paths = ("/RPC")

def source_path():
	return "http://localhost:8001/instance/source.zip"

server = SimpleXMLRPCServer(("", 8000), requestHandler=RequestHandler)

server.register_function(source_path, "source")
server.serve_forever()
