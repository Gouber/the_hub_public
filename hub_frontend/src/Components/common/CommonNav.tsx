import React from "react";
import {Nav} from "react-bootstrap";
import {Link} from "react-router-dom";

interface CommonNavProps {
    activeMenuItem: string | null;
}

interface CommonNavState {
    loggedIn: boolean;
}


export default class CommonNav extends React.Component<CommonNavProps, CommonNavState> {

    constructor(props: CommonNavProps) {
        super(props);
        this.state = {
            loggedIn: !!localStorage.getItem("token"),
        }
    }

    render() {


        let nav;
        if (this.state.loggedIn) {
            nav = <Nav variant="tabs">
                <Nav>
                    <Nav.Item>
                        <Nav.Link eventKey="house" as={Link} to="/house">House</Nav.Link>
                    </Nav.Item>
                </Nav>
                <Nav className="ml-auto" defaultActiveKey={this.props.activeMenuItem}>
                    <Nav.Item>
                        <Nav.Link eventKey="logout" as={Link} to="/logout">Logout</Nav.Link>
                    </Nav.Item>
                </Nav>
            </Nav>
        } else {



            nav = <Nav variant="tabs" defaultActiveKey={this.props.activeMenuItem}>
                <Nav.Item>
                    <Nav.Link eventKey="login" as={Link} to="/login">Login</Nav.Link>
                </Nav.Item>
                <Nav.Item>
                    <Nav.Link eventKey="register" as={Link} to="/register">Register</Nav.Link>
                </Nav.Item>
                <Nav.Item>
                    <Nav.Link eventKey="house" as={Link} to="/house">House</Nav.Link>
                </Nav.Item>
            </Nav>
        }
        return (
            <>
                {nav}
            </>
        )
    }
}