import React from "react";
import {Redirect} from "react-router-dom"


export default class FourOFour extends React.Component<{}, {}>{

    constructor(props: {}) {
        super(props);
        localStorage.clear()
    }

    render(){
        return <Redirect to={{
            pathname: "/login",
            state: {
                message: "You've succesfully logged out"
            }

        }} />
    }
}