import React, {useState} from "react"
import {Carousel, Col, Container, Row} from "react-bootstrap";

export default function ControlledCarousel(_: {}){
    const transitionTime: number = 5000
    const [index, setIndex] = useState(0)
    //Null stops the carousel from cycling
    const [shouldCycle, setCycle] = useState<null | number>(transitionTime)

    const handleSelect = (selectedIndex: number, e: Object | null) => {
        setIndex(selectedIndex)
    }


    const mouseIn = (index: number) => (_: React.MouseEvent<HTMLImageElement>) => {
        setIndex(index)
        setCycle(null)
    }

    const mouseOut = (_: React.MouseEvent<HTMLImageElement>) => {
        setCycle(transitionTime)
    }

    return (
        <>

            <Carousel activeIndex={index} onSelect={handleSelect} interval={shouldCycle}>
                <Carousel.Item>
                    <img
                        className="d-block w-100"
                        src={require("./resources/first_slide.svg")}
                    />
                </Carousel.Item>

                <Carousel.Item>
                    <img
                        className="d-block w-100"
                        src={require("./resources/second_slide.svg")}
                    />
                </Carousel.Item>

                <Carousel.Item>
                    <img
                        className="d-block w-100"
                        src={require("./resources/third_slide.svg")}
                    />
                </Carousel.Item>

            </Carousel>

            <div style={{marginTop: "20px"}}>
                <Container>
                    <Row>
                        <Col className={"d-flex justify-content-center"}>
                            <img
                                src={require("../../Components/houses_hub/resources/small_image.svg")}
                                className={"thumbnailImage"}
                                onMouseEnter={mouseIn(0)}
                                onMouseOut={mouseOut}
                            />
                        </Col>
                        <Col className={"d-flex justify-content-center"}>
                            <img
                                src={require("../../Components/houses_hub/resources/small_image.svg")}
                                className={"thumbnailImage"}
                                onMouseEnter={mouseIn(1)}
                                onMouseOut={mouseOut}
                            />
                        </Col>
                        <Col className={"d-flex justify-content-center"}>
                            <img
                                src={require("../../Components/houses_hub/resources/small_image.svg")}
                                className={"thumbnailImage"}
                                onMouseEnter={mouseIn(2)}
                                onMouseOut={mouseOut}
                            />
                        </Col>
                    </Row>
                </Container>
            </div>
        </>
    );




}