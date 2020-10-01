import React from 'react'
import io from 'socket.io-client'

// TODO: What happens if someone logs out in another tab, logs back in as another user. Does the socket allow sending? CHECK!

export const CTX = React.createContext()


let initialState = {
    1: [{from: "Gouber", msg: "Hi there"},{from: "Gouber", msg: "Oy respond"}],
    2: [{from: "Sean", msg: "Where is the water"},{from: "Gouber", msg: "There is no water here"}],
    3: [{from: "Dani", msg: "Where is the fridge"}]
}

function reducer(state,action){
    switch(action.type){
        case "RECEIVE_MESSAGE":
            const {from, msg, chat_id} = action.payload
            return {
                ...state,
                [chat_id]: [
                    ...state[chat_id],
                    {from, msg}
                ]
            }
        case "INIT":
            var newState = {}
            console.log(action.payload)
            action.payload.forEach(elem => {
                newState = {
                    ...newState,
                    [elem.id] : elem.chat_set.map(chatSet => {
                        return {from: chatSet.student.email, msg: chatSet.message}
                    })
                }
            })
            return newState
        default:
            return state

    }
}


//declare outside of function as we don't want it to re-render every time the store reloads
let socket;


function sendChatAction(value){
    console.log("Sent")
    socket.emit('chat message', value)
}



//A high order component that surrounds its children with the required context to access the chats
export default function Store(props){


    const [allChats, dispatch] = React.useReducer(reducer, initialState)
    if(!socket){
        socket = io(':3001', {
            query: {
                token: localStorage.getItem("token")
            }
        })
        socket.on('chat message', function(msg){
            console.log("Received" + JSON.stringify(msg))
            dispatch({type: "RECEIVE_MESSAGE", payload: msg })
        })
        socket.on('INIT', function(msg){
            dispatch({type: "INIT", payload: msg})
        })
        socket.on('error', (error) => {
          //this will come in handy when we throw this error after sending a chat
          if(error === "token_not_valid"){
            socket.disconnect()
            //want to try to refresh
            fetch("http://localhost:8000/login/api/refresh-token/",{
                method: "POST",
                body: JSON.stringify({refresh: localStorage.getItem("refresh")}),
                headers: {
                    'Content-Type': 'application/json'
                }
            })
                .then(response => response.json())
                .then(data => {
                    console.log(data)
                    if(data.code === "token_not_valid"){
                        console.log("Needs logging back in")
                    }
                    else {
                        localStorage.setItem("token", data.access)
                        localStorage.setItem("refresh", data.refresh)
                        socket.io.opts.query = {
                            token: localStorage.getItem("token")
                        }
                        socket.connect()
                    }
                })
          }else{
              //Connection refused for another reason - possibly server went down. Must handle this
          }
        })
    }

    const user = 'vlad' + Math.random().toFixed(2)

    return (<CTX.Provider value={{allChats, sendChatAction, user}}>
        {props.children}
    </CTX.Provider>)
}