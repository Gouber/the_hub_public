import React from "react"
import {Modal} from "react-bootstrap";
import {DynamicApplyForm} from "../login_register_service_hub/forms";

interface ApplicationModalProps {
    id: number,
    show: boolean,
    close: () => void
}


export default class ApplicationModal extends React.Component<ApplicationModalProps, {}> {

    locallyHideModal = () => {
        this.props.close()
        this.setState({
            students: []
        })
    }

    render() {
        return (
            <Modal
                show={this.props.show}
                onHide={this.locallyHideModal}>
                <Modal.Header closeButton>
                    <Modal.Title id="contained-modal-title-vcenter">Apply Here</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <DynamicApplyForm houseId={this.props.id}/>
                </Modal.Body>
            </Modal>
        )
    }
}