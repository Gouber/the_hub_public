import {withRouter, Redirect, RouteComponentProps} from "react-router-dom";
import React from "react"
import {CommonNav} from "../../Components/common/index"
import {ControlledCarousel, ApplicationModal} from "../../Components/houses_hub"
import {Button, Spinner} from "react-bootstrap";
import "./style.css"

export interface DetailHouseFetch{
    id: number,
    number_of_rooms: number,
    number_of_bathrooms: number,
    address: string,
    lat: null | number,
    lgn: null | number,
    price: number,
    agency: number
}

interface DetailState {
    showModal: boolean,
    shouldRedirect: boolean,
    data: DetailHouseFetch | null
}
interface DetailProps extends RouteComponentProps<{id: string}>{}

class Detail extends React.Component<DetailProps,DetailState>{

    constructor(props: DetailProps) {
        super(props);
        this.state={
            showModal: false,
            shouldRedirect: false,
            data: null,
        }
    }

    componentDidMount() {

        fetch("http://localhost:8000/houses/" + this.props.match.params.id)
            .then(response => {
                if(response.status === 404){
                    this.setState({
                        shouldRedirect: true
                    })
                    return;
                } else return response.json()
            })
            .then(data => this.setState({
                data: data
            }))
    }

    showModal = () => {
        this.setState({
            showModal: true
        })
    }

    closeModal =() => {
        this.setState({
            showModal: false
        })
    }


    render(){

        if(this.state.shouldRedirect) return <Redirect to ="/404"/>

        if(!this.state.data)
            return <Spinner animation="border" role="status">
                     <span className="sr-only">Loading...</span>
                   </Spinner>

        let ApplyButton = <div style={{marginTop: "10px" ,display: "flex", justifyContent: "flex-end"}}>
                             <Button variant={"success"} onClick={this.showModal}>Apply</Button>
                          </div>

        return (
            <>
                <CommonNav activeMenuItem={null}/>
                {/*{localStorage.getItem("token") !== null && applyButton}*/}
                {ApplyButton}

                <div style={{marginTop: "30px"}}>
                    <ControlledCarousel/>
                </div>
                <div id ="detailHouseInfo" style={{marginTop: "10px"}}>
                    <h4>Id: {this.state.data.id}</h4>
                    <h4># rooms: {this.state.data.number_of_rooms}</h4>
                    <h4># bathrooms: {this.state.data.number_of_bathrooms}</h4>
                    <h4>Address: {this.state.data.address}</h4>
                    <h4>Price: {this.state.data.price}</h4>
                </div>

                <ApplicationModal
                    id = {this.state.data.id}
                    show={this.state.showModal}
                    close={this.closeModal}
                />
            </>
        )
    }
}

export default withRouter(Detail)