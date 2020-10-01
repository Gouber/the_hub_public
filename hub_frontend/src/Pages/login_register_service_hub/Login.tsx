import React from "react";
import CommonNav from "../../Components/common/CommonNav";
import {LoginForm} from "../../Components/login_register_service_hub/forms";
import {Alert} from "react-bootstrap";
import {RouteComponentProps} from "react-router";


interface LoginState {
    showExternalAlert: boolean;
}

export default class Login extends React.Component<{} & RouteComponentProps, LoginState>{

    constructor(props: {} & RouteComponentProps) {
        super(props);
        this.state = {
            showExternalAlert: this.props.location.state !== undefined
        }
    }

    render(){

        let externalMessage;
        if(this.props.location.state)

            {
                externalMessage = <div style={{marginTop: 10}}>
                                    <Alert variant="success" onClose={() => this.setState({showExternalAlert: false})} dismissible>
                                        {/*@ts-ignore*/}
                                        <p>{this.props.location.state.message}</p>
                                    </Alert>
                                  </div>
            }


        return <>
            <CommonNav activeMenuItem = "login"/>
            <h1>Login Here</h1>
            {/*Needs this to access history inside LoginForm*/}
            <LoginForm {...this.props}/>
            {this.state.showExternalAlert && externalMessage}
        </>
    }
}