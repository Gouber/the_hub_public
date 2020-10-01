import React from "react"
import {CTX} from "../Store/Store";
import {Badge, Button} from "react-bootstrap";


export default function Dashboard(props){

    //passing a value via the context returns that value here.
    //The way we've passed down the value, we passed down an array
    //The following only captures the first element of said array
    const {allChats, sendChatAction, user} = React.useContext(CTX)
    const chatIds = Object.keys(allChats)
    //Will need to figure out which one has the most recent messages to display as first.
    const [activeTopic, changeActiveTopic] = React.useState(chatIds[0])
    const [inputValue, changeInputValue] = React.useState('')
    const messages = allChats[activeTopic]

    return (
        <div style={{width: "900px"}}>
            <h1>Active Chat: {activeTopic}</h1>
            <hr/>
            <h2>Available Chats:</h2>
            {chatIds.map(it => <h3 onClick={e => changeActiveTopic(it)}>{it}</h3>)}
            <hr/>
            <h3>Messages</h3>
            {messages.map(it =>
                <div>
                       <p><Badge variant="secondary">{it.from}</Badge> {it.msg}</p>
                </div>
            )}
            <hr/>
            <input value={inputValue} onChange={e => changeInputValue(e.target.value)}/>
            <Button onClick={e => {
                changeInputValue('')
                sendChatAction({
                    from: user,
                    chat_id: activeTopic,
                    msg: inputValue,
                    token: localStorage.getItem("token")
                })}
            }>Send</Button>
        </div>
    )

}