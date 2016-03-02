var express = require('express');
var app = express();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var r = require('rethinkdb')
var sleep = require('sleep')
// var today = '2016-02-25';

app.use(express.static('public'));
app.use('/socket.io', express.static('node_modules/socket.io-client'));

app.get('/', function (req, res) {
  res.sendFile(__dirname + '/index_new2.html');
});

app.get('/sender', function (req, res) {
  res.sendFile(__dirname + '/public/sender.html');
});

r.connect( {host: 'localhost', port: 28015}, function(err, c) {
  r.db('papelex').table("orders").filter(r.row('DATA').eq((new Date()).toISOString().slice(0, 10))).changes().run(c)
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
      r.db('papelex').table("orders").filter(r.row('DATA').eq((new Date()).toISOString().slice(0, 10))).run(c)
        .then(function(cursor) {
          cursor.each(function(err, item) {
            socket.emit("initial_order", item);
            sleep.usleep(1000); // waits 1ms
          }, function() {
            socket.emit('finished_initial_orders');
          });
        });
    });
  socket.on('disconnect', function(){
    console.log('user disconnected');
  });
});

// http.listen(3000, function () {
http.listen(80, '192.168.24.179', function () {
// http.listen(80, '192.168.1.9', function () {
  console.log('Example app listening on port 3000!');
});
