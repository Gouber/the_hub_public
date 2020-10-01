import React from "react";

import {Route, Redirect, RouteProps} from 'react-router-dom';

function AnonymousUserRoute ({ component: Component, ...rest }: RouteProps) {
  if (!Component) return null;
  console.log("This gets called")
  console.log(localStorage.getItem("token"))
  return (<Route {...rest} render={(props) => (
      localStorage.getItem("token") === null
          ? <Component {...props} />
          : <Redirect to='/404'/>
  )}/>);
}

export default AnonymousUserRoute