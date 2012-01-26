import logging
#import zmq
from gevent_zeromq import zmq
from gevent import Timeout
from zmq.utils import jsonapi

class Reply(object):
    status = 0
    data = None
    
    def __init__(self, status, data):
        self.status = status
        self.data = data
            
    def serialize(self):
        return jsonapi.dumps({
            'level': self.status,
            'data': self.data
        })
        
class ServerOfflineException(Exception):
    pass

class CherrypickClient(object):
    def __init__(self, endpoint, timeout=3000, retries=3, keepalive=False):
        self.endpoint = endpoint
        self.timeout = timeout
        self.retries = retries
        self.attempts = 0
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
        self.attempts += 1
        if self.attempts > self.retries:
            raise ServerOfflineException("Server seems to be offline, abandoning")
        else:
            logging.warn('Server timeout, retrying ... attempt %s/%s' % (self.attempts, self.retries))

        logging.debug('Reconnecting')
        self.__disconnect()
        self.__connect()
        self.__send()

    def __send(self):
        """
        logging.debug('Sending')

        while self.attempts <= self.retries:
            self.client.send_json(self.msg)
            socks = dict(self.poll.poll(self.timeout))
            if socks.get(self.client) == zmq.POLLIN:
                reply = self.client.recv_json()
                if not reply:
                    raise Exception('what?')
                if reply:
                    logging.debug('Server replied')
                    self.reply = reply
                    break
                else:
                    raise Exception('why?')
    
            else:
                self.__reconnect()
        """
        while self.attempts <= self.retries:
            with Timeout(self.timeout/1000) as timeout:
                try:
                    logging.debug('Sending')
                    self.client.send_json(self.msg)
                    self.reply = self.client.recv_json()
                    logging.debug('Server replied')
                    timeout.cancel()
                    break
                except Timeout:
                    self.__reconnect()

    """
    def send(self, cmd, *args, **kwargs):
        from gevent import spawn
        return spawn(self.__spawned_send, cmd, *args, **kwargs).get(block=False, timeout=self.timeout)
        
    def __spawned_send(self, cmd, *args, **kwargs):
    """
    def send(self, cmd, *args, **kwargs):
        self.msg = {'cmd': [cmd, args, kwargs]}
        """
        if args:
            self.msg['args'] = args
        if kwargs:
            self.msg['kwargs'] = kwargs
        """

        self.reply = None
        self.attempts = 0

        self.__connect()
        
        try:
            self.__send()
            self.reply = Reply(self.reply['status'], self.reply['data'])
        except ServerOfflineException, e:
            self.reply = Reply(-1, e.message) 
            print self.reply
        except Exception, e:
            print e
        finally:
            if not self.keepalive:
                self.__disconnect()
            return self.reply
    
    def close(self):
        # TODO: Maybe stop send
        self.__close()
