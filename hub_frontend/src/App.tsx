import React from 'react';
import './App.css';
import {BrowserRouter as Router, Switch, Route} from "react-router-dom";
import {Login,Register} from "../src/Pages/login_register_service_hub/index"
import {AnonymousUserRoute, ProtectedRoute} from "../src/Components/common"
import {FourOFour, Logout} from "../src/Pages/common/index"
import {HouseIndex, Detail} from "../src/Pages/houses_hub/index"
import StandAloneChat from "./ChatApp/StandAloneChat/StandAloneChat";

class App extends React.Component{


      render() {
          return (
              <>
                  <div id="mainPage">
                      <Router>
                          <Switch>
                              <AnonymousUserRoute path="/login" exact component={Login}/>
                              <AnonymousUserRoute path="/register" exact component={Register}/>
                              <Route path="/house" exact component={HouseIndex}/>
                              <Route path="/404" exact component={FourOFour}/>
                              <Route path="/logout" exact component={Logout}/>
                              <Route path="/detail/:id" exact component={Detail}/>
                              <Route path="/chat/:id" exact component={StandAloneChat}/>
                          </Switch>
                      </Router>
                  </div>
              </>
          );
      }
}

export default App;
