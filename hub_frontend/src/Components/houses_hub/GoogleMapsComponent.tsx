import React from "react"
import {Map, GoogleApiWrapper, Polygon, GoogleAPI} from 'vlad-maps';


interface GoogleMapsProps {
    google: GoogleAPI
}

interface GoogleMapsState {
    triangleCoords: Array<any>
}



export class GoogleMapsComponent extends React.Component<GoogleMapsProps, GoogleMapsState>{

    constructor(props: GoogleMapsProps) {
        super(props);
        this.state={
            triangleCoords:
            [
                { lat: 37.789411, lng: -122.422116 },
                { lat: 37.785757, lng: -122.421333 },
                { lat: 37.789352, lng: -122.415346 }
            ]
        }
    }

    render(){
        return (
            //@ts-ignore
             <Map id="mainGoogleMap"
                 google={this.props.google}
                 >
             <Polygon
          somethingUpdated = {(poly: { getPaths: () => { (): any; new(): any;[x: string]: any[]; }; }) => {
              console.log(poly.getPaths()['i'][0])
          }}
          paths = {[this.state.triangleCoords]}
          strokeColor="#0000FF"
          strokeOpacity={0.8}
          strokeWeight={2}
          fillColor="#0000FF"
          editable={true}
          fillOpacity={0.35} />
             </Map>
             )
    }
}

export default GoogleApiWrapper({
    apiKey: ""
})(GoogleMapsComponent)