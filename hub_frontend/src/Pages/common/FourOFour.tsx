import React from "react";
import {Link} from "react-router-dom";


export default class FourOFour extends React.Component {
    render() {
        return (
            <>
                <h1>404 Page not found</h1>
                <p>This page does not exist or you don't have permission to view it</p>
                <Link to={"/house"}>Back to Houses</Link>
            </>
        )
    }
}