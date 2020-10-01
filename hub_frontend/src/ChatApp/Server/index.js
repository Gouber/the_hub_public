var app = require('express')();
var http = require('http').createServer(app);
var io = require('socket.io')(http);
const fetch = require("node-fetch");



app.get('/', (req, res) => {
  res.send('<h1>Hello world</h1>');
});

async function initConversation(socket){
    const response = await fetch('http://localhost:8000/chat/api/conversation_with_chat', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': ' Bearer ' + socket.handshake.query.token
        },
    })
    return await response.json()
}

async function sendChat(socket,msg){
    const response = await fetch('http://localhost:8000/chat/api/create_chat/' + msg.chat_id, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'Authorization': ' Bearer ' + msg.token
        },
        body: JSON.stringify({message: msg.msg})
    })
    return await response
}


io.use(function(socket,next){
   initConversation(socket).then(data => {
       if (data.code === "token_not_valid"){
           console.log("Triggering refresh")
           next(new Error("token_not_valid"))
       }else{
           data.forEach(chat => {
               console.log("Joining " + chat.id)
               socket.join(chat.id)
           })
           socket.emit("INIT", data)
           next()
       }
   })
});

//Gotta initialize it

io.on('connection', function(socket){

    // console.log(socket))
    console.log('a user connected')
    socket.on('chat message', function(msg){
        //We have access to the token here.
        //Send it using the message
        //console.log(socket.handshake.query.token)
         sendChat(socket,msg).then(data => {
             console.log("Status: " + data.status)
         })

        //need to fetch here and see if we created correct message
        io.to(msg.chat_id).emit('chat message', msg)
    });

})

http.listen(3001, () => {
  console.log('listening on *:3000');
});