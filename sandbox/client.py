import pickle
import logging
class TestObject(object):
    def __init__(self, value):
        self.value = value
        
    def get_value(self):
        return self.value
    
    def test(self):
        return self.value.upper()

import zmq
import sys
from zmq.utils import jsonapi

class DoItClient(object):
    def __init__(self, endpoint, timeout=3000, retries=3, keepalive=False):
        self.endpoint = endpoint
        self.timeout = timeout
        self.retries = retries
        self.retries_left = 0
        self.keepalive = keepalive
        self.context = None
        self.client = None
        self.poll = None

    def __connect(self):
        if not self.context:
            logging.debug('Initializing Context')
            self.context = zmq.Context()
            
        if not self.client:
            logging.debug('Connecting')
            self.client = self.context.socket(zmq.REQ)
            self.client.connect(self.endpoint)
        
        if not self.poll:
            logging.debug('Initializing Poller')
            self.poll = zmq.Poller()
        self.poll.register(self.client, zmq.POLLIN)
        
    def __disconnect(self):
        logging.debug('Disconnecting')
        self.client.setsockopt(zmq.LINGER, 0)
        self.client.close()
        self.poll.unregister(self.client)
        self.client = None
        
    def __close(self):
        if self.client:
            self.__disconnect()
            self.poll = None
        if self.context:
            self.context.term()

    def __reconnect(self):
        logging.debug('Reconnecting')
        self.__disconnect()

        self.retries_left -= 1
        if self.retries_left == 0:
            raise Exception("Server seems to be offline, abandoning")
        else:
            logging.warn('Server timeout, retrying ... attempt %s/%s' % (self.retries-self.retries_left+1, self.retries))
        
        self.__connect()
        self.__send()

    def __send(self):
        logging.debug('Sending')
        while self.retries_left:
            self.client.send(self.msg)
            
            socks = dict(self.poll.poll(self.timeout))
            if socks.get(self.client) == zmq.POLLIN:
                reply = self.client.recv()
                if not reply:
                    raise Exception('what?')
                if reply:
                    logging.debug('Server replied')
                    self.reply = jsonapi.loads(reply)
                    break;
                else:
                    raise Exception('why?')
    
            else:
                self.__reconnect()

    def send(self, cmd, *args, **kwargs):
        msg = {'cmd': cmd}
        if args:
            msg['args'] = args
        if kwargs:
            msg['kwargs'] = kwargs
        self.msg = jsonapi.dumps(msg)
        self.reply = None
        self.retries_left = self.retries

        self.__connect()
        self.__send()
        if not self.keepalive:
            self.__disconnect()
        
        return self.reply

    def close(self):
        # TODO: Maybe stop send
        self.__close()


def main(*args):
    logging.getLogger().setLevel(logging.DEBUG)
    #client = DoItClient('ipc://neo-core', timeout=1000, keepalive=True)
    client = DoItClient('tcp://127.0.0.1:8888', timeout=1000, keepalive=True)
    
    msg = 'Write:'
    input = 'X'
    while msg and input:
        print 'Write:',
        input = raw_input()
        
        if input:
            try:
                reply = client.send(input)
            except:
                print 'Server down'
            else:
                print 'Reply:', reply
            
    client.close()

    """
    uri = 'ipc://neo-core'
    context = zmq.Context(1)
    
    socket = context.socket(zmq.REQ)
    socket.connect(uri)
    
    msg = 'Write:'
    while msg:
        print 'Write:',
        input = raw_input()
        msg = jsonapi.dumps({'msg': input})
        socket.send(msg)
        #socket.send(pickle.dumps(TestObject('jorpan')))
        json_response = socket.recv()
        response = jsonapi.loads(json_response)
        print 'Reply:', response['msg'] 
    """



if __name__ == "__main__":
    main(*sys.argv[1:])
