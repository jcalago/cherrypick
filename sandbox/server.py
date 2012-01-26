import zmq
from zmq.utils import jsonapi
import pickle
import time

uri = 'ipc://test'
#uri = 'tcp://127.0.0.1:8888'
context = zmq.Context(1)

server = context.socket(zmq.REP)
server.bind(uri)

publisher = context.socket(zmq.PUB)
publisher.bind('tcp://127.0.0.1:9999')

print 'Listeing...'
from client import TestObject

tasks = ['Issue #1', 'Issue #2', 'Issue #3']

while True:
    request = server.recv()
    msg = jsonapi.loads(request)
    print 'RECEIVED:', msg

    if msg['cmd'] == 'list':
        server.send_json({'msg': 'OK'})
        

    server.send_json({'msg': 'OK'})

    pub_msg = jsonapi.dumps({'msg': ': %s' % msg['msg']})
    msg_type = 'A' if msg['msg'].isdigit() else 'B'
    #for i in xrange(1000):
    #publisher.send_multipart([msg_type, pub_msg])
    publisher.send_json(pub_msg)
    print '... PUBLISHED'
    #time.sleep(1)
"""

from random import randint
import time

server = context.socket(zmq.REP)
server.bind(uri)

cycles = 0
while True:
    request = server.recv()
    cycles += 1

    # Simulate various problems, after a few cycles
    if cycles > 3 and randint(0, 3) == 0:
        print "I: Simulating a crash"
        break
    elif cycles > 3 and randint(0, 3) == 0:
        print "I: Simulating CPU overload"
        time.sleep(2)

    print "I: Normal request (%s)" % request
    time.sleep(1) # Do some heavy work
    server.send(request)

server.close()
context.term()
"""
