var express = require('express');
var app = express();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var r = require('rethinkdb')
var sleep = require('sleep')

app.use(express.static('public'));
app.use('/socket.io', express.static('node_modules/socket.io-client'));

// Main routes
app.get('/', function (req, res) {
  res.sendFile(__dirname + '/public/index.html');
});

app.get('/sender', function (req, res) {
  res.sendFile(__dirname + '/public/sender.html');
});

r.connect( {host: 'localhost', port: 28015}, function(err, c) {
  r.db('papelex').table("orders").filter(r.row('DATA').eq((new Date()).toLocaleDateString())).changes().run(c)
    .then(function(cursor) {
      cursor.each(function(err, item) {
        console.log(item['new_val']);
        io.sockets.emit('new_order', item['new_val']);
      }, function() {
        console.log('new_order')
      });
    });
});

io.on('connection', function(socket){
  console.log('a user connected');
    r.connect( {host: 'localhost', port: 28015}, function(err, c) {
      r.db('papelex').table("orders").filter(r.row('DATA').eq((new Date()).toLocaleDateString())).run(c)
        .then(function(cursor) {
          cursor.each(function(err, item) {
            socket.emit("initial_order", item);
            sleep.usleep(1000); // waits 1ms to avoid initial flood
          }, function() {
            socket.emit('finished_initial_orders');
          });
        });
    });
  socket.on('disconnect', function(){
    console.log('user disconnected');
  });
});


if(process.argv[process.argv.length - 1] === 'production'){
  http.listen(80, '192.168.24.45', function () {
    console.log('Papelex BI is live!');
  });  
} else {
  http.listen(3000, function () {
    console.log('Papelex BI happily listening on port 3000!');
  });
}
