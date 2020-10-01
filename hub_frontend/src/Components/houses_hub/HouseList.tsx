import React from "react"
import {Card, Table, Spinner, Button} from "react-bootstrap"
import {Link} from "react-router-dom";


interface HouseListProps{
    apiLink: string
}

interface HouseListState{
    houseList: Array<any>
}


export default class HouseList extends React.Component<HouseListProps, HouseListState>{
    constructor(props: HouseListProps) {
        super(props)
        this.state = {
            houseList: []
        }
    }


    componentDidMount() {
    fetch(this.props.apiLink)
              .then(response => response.json() )
              .then(data => this.setState({
                  houseList: data
              }))
    }


    render() {
        const houseList = this.state.houseList

        if(!houseList) return (
            <Spinner animation="border" role="status">
              <span className="sr-only">Loading...</span>
            </Spinner>
        )

        return (
            <>
                <h2>List of Houses</h2>
                <hr/>
                <div id={"houseListHolder"} style={{display: 'flex', flexDirection: 'column'}}>
                    {houseList.map( (house,i) => {
                        return <Card key={house.id} style={{flex: "1", marginBottom: "20px"}}  >
                            <Card.Body>
                                <Card.Img variant="top" src={require("./resources/card_image.svg")} />
                                <Card.Title style={{paddingTop: "10px"}}>{house.address}</Card.Title>
                                <Card.Text>
                                    <Table striped bordered hover variant="dark">
                                        <tbody>
                                            <tr>
                                                <td>Agency</td>
                                                <td>{house.agency}</td>
                                            </tr>
                                            <tr>
                                                <td>Number of rooms</td>
                                                <td>{house.number_of_rooms}</td>
                                            </tr>
                                            <tr>
                                                <td>Number of bathrooms</td>
                                                <td>{house.number_of_bathrooms}</td>
                                            </tr>
                                            <tr>
                                                <td>Price</td>
                                                <td>{house.price}</td>
                                            </tr>
                                        </tbody>
                                    </Table>
                                </Card.Text>
                                <div className={"d-flex flex-row-reverse btn-toolbar"}>
                                    <div className={"mr-2"}>
                                        <Button as={Link} to={"/detail/"+house.id} variant={"dark"}>Detail</Button>
                                    </div>
                                    <div className={"mr-2"}>
                                        <Button variant={"dark"}>Quick View</Button>
                                    </div>
                                </div>
                            </Card.Body>
                        </Card>
                    })}
                </div>
            </>
        );
    }


}

