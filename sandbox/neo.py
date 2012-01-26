from gevent.monkey import patch_all
patch_all()

from gevent_zeromq import zmq
#import zmq
from zmq.utils import jsonapi
import datetime

context = zmq.Context()

server = context.socket(zmq.REP)
#server.bind('ipc://neo-core')
server.bind('tcp://*:8888')

publisher = context.socket(zmq.PUB)
#publisher.bind('ipc://neo-events')
publisher.bind('tcp://*:9999')

print 'Listeing...'

tasks = [{'id': 1, 'name': 'Jonas'},
         {'id': 2, 'name': 'Hannes'},
         {'id': 3, 'name': 'Patrik'},
         {'id': 4, 'name': 'Stefan'},
         {'id': 5, 'name': 'Jonte'},
         {'id': 6, 'name': 'David'},
         {'id': 7, 'name': 'Joel'},
         {'id': 8, 'name': 'Matthias'},
         {'id': 9, 'name': 'Emilia'},
         {'id': 10, 'name': 'Andrei'}]

while True:
    #request = server.recv()
    #msg = jsonapi.loads(request)
    json_msg = server.recv()
    msg = jsonapi.loads(json_msg)
    print 'RECEIVED:', msg

    cmd = msg['cmd']
    method, args, kwargs = cmd

    if method == 'list_items':
        from time import sleep
        #sleep(5)
        server.send_json({'status': 1, 'data': tasks})
    
    elif method == 'update_item':
        server.send_json({'status': 1, 'data': None})

        task = [task for task in tasks if task['id'] == int(kwargs['pk'])][0]
        task = tasks.pop(tasks.index(task))
        tasks.insert(int(kwargs['index']), task)

        publisher.send_multipart(['/events', json_msg])
        print 'PUBLISHED'

    elif method == 'get_task':
        server.send_json({'status': 1, 'data': {'inbox': 'sportamore',
                                                'folder': 'TODO',
                                                'project': 'Receipt page',
                                                'subject': '#Add share links on receipt page',
                                                'user': 'Jonas Lundberg',
                                                'description': 'Use sharethis and place the share buttons next to the page title.'
                                                }})
        
    else:
        print '????'
    
    #reply_msg = jsonapi.dumps({'msg': 'OK'})
    #server.send(reply_msg)

