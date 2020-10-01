import React from "react"
import Store from "../Store/Store";
import Dashboard from "./Dashboard";


export default function StandAloneChat(props){
    return(
        <Store>
            <Dashboard/>
        </Store>
    )
}