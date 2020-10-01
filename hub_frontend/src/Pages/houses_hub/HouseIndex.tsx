import React from "react";
import {CommonNav} from "../../Components/common";
import {GoogleApiWrapper, HouseList} from "../../Components/houses_hub"


export default class HouseIndex extends React.Component<{}, {}>{

    render() {
        return (
        <>
        <CommonNav activeMenuItem={"house"}/>
        <h1>Home Index</h1>
         <div style={{position: "relative", width: "100%", height: "400px"}}>
         <GoogleApiWrapper />
         </div>
         <div style={{paddingTop: "20px"}}>
         <HouseList apiLink={"http://localhost:8000/houses/index/"}/>
         </div>
        </>
        )
    }
}