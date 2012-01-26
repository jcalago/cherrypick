import zmq
import sys
from zmq.utils import jsonapi

uri = 'ipc://neo-core'
context = zmq.Context()

socket = context.socket(zmq.REQ)
socket.connect(uri)

msg = jsonapi.dumps({'msg': input})
socket.send(msg)
socket.recv()

socket.setsockopt(zmq.LINGER, 0)
socket.close()
context.term()
