

var http = require('http');
var httpServer = http.createServer(function(req, res) {
        res.writeHead(404, {'Content-Type':'text/html'});
}).listen(8888);

var faye = require('faye');
var adapter = new faye.NodeAdapter({
    mount: '/faye',
    timeout: 60	
});

adapter.attach(httpServer);

faye.Logging.logLevel = 'error';

zeromq = require('zmq');
zmqSocket = zeromq.createSocket('subscriber');
zmqSocket.subscribe('');  // Subscribe to everything.
zmqSocket.connect("tcp://192.168.3.15:9999");
zmqSocket.on('message', function(envelope, data) {
    console.log('got messsage');
    data = JSON.parse(data.toString('utf8'));
    adapter.getClient().publish(envelope.toString(), data);
});

console.log('Server started');