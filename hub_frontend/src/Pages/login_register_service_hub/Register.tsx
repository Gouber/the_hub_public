import React from "react";
import CommonNav from "../../Components/common/CommonNav";
import {RegisterForm} from "../../Components/login_register_service_hub/forms";
import {RouteComponentProps} from "react-router";
import {DynamicApplyForm} from "../../Components/login_register_service_hub/forms"


export default class Register extends React.Component<{} & RouteComponentProps, {}>{

    render(){
        return <>
            <CommonNav activeMenuItem = "register"/>
            <h1>Register Here</h1>
            <RegisterForm {...this.props}/>
        </>
    }

}