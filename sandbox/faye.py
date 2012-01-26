import zmq
import sys
from zmq.utils import jsonapi

def main(*args):
    context = zmq.Context(1)
    
    subscriber = context.socket(zmq.SUB)
    subscriber.connect('ipc://neo-events')
    msg_type = args[0] if args else ''
    subscriber.setsockopt(zmq.SUBSCRIBE, msg_type)
    
    while True:
        address = '?'
        #contents = subscriber.recv()
        [address, contents] = subscriber.recv_multipart()
        json_contents = jsonapi.loads(contents)
        print 'Subscribed message:', address, json_contents['msg'] 

if __name__ == "__main__":
    main(*sys.argv[1:])