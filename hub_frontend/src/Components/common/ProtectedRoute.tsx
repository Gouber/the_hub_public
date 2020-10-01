import React from "react";
import {Route, Redirect, RouteProps} from 'react-router-dom';

function ProtectedRoute ({ component: Component, ...rest }: RouteProps) {
  if (!Component) return null;
  return (<Route {...rest} render={(props) => (
      localStorage.getItem("token") !== null
          ? <Component {...props} />
          : <Redirect to='/404'/>
  )}/>);
}

export default ProtectedRoute