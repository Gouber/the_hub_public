import {Field, FieldArray, FieldProps, Formik, getIn} from "formik";
import React, {Component} from "react";
import {Col, Row, Form, Button} from "react-bootstrap";
import {IconContext} from "react-icons/lib";
import {IoIosCloseCircle, IoIosAddCircle} from "react-icons/all";
import {generate} from "shortid"
import * as Yup from "yup";


interface AdditionalStudent {
    id: string,
    email: string,
    fullname: string
}

interface DestructuringValuesForm {
    additionalStudents: Array<AdditionalStudent>
}

interface DynamicApplyFormProps {
    houseId: number
}

const Input = ({field, form: {errors, touched}}: FieldProps) => {
    const errorMessage = getIn(errors, field.name);
    const touchedBool = getIn(touched, field.name)
    const fieldName = field.name[22].startsWith("e") ? "Email" : "Fullname"
    const errorMessagePretty = errorMessage ? (errorMessage[22].startsWith("e") ? "Email is a required field" : "Fullname is a required field") : undefined

    return (
        <>
            <input placeholder={fieldName} {...field} className={"form-control"}/>
            {(errorMessage && touchedBool) && <div style={{color: "red"}}>{errorMessagePretty}</div>}
        </>
    );
};

const validationSchema = Yup.object().shape({
    additionalStudents: Yup.array().of(
        Yup.object().shape({
            email: Yup.string().email().required(),
            fullname: Yup.string().required()
        })
    )
});

class DynamicApplyForm extends Component<DynamicApplyFormProps, {}> {

    render() {
        return (
            <Formik
                validationSchema={validationSchema}
                initialValues={{
                    additionalStudents: []
                }}
                onSubmit={({additionalStudents}: DestructuringValuesForm) => {

                    const emails: Array<string> = additionalStudents.map(elem => elem.email)

                    fetch("http://localhost:8000/houses/apply/" + this.props.houseId + "/", {
                        method: "POST",
                        body: JSON.stringify({
                            students: JSON.stringify(emails)
                        }),
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': ' Bearer ' + localStorage.getItem("token")
                        }
                    }).then(response => {
                        if (response.status === 401) {
                            console.log(response.json())
                        } else {
                            alert("Success")
                            //TODO: add redirect or close the modal.
                        }
                    })
                }}

            >
                {
                    ({values, handleSubmit}) => (
                        <>
                            <Form onSubmit={handleSubmit}>
                                <FieldArray name={"additionalStudents"}>
                                    {
                                        ({push, remove}) => (
                                            <div>
                                                {values.additionalStudents.map((student: AdditionalStudent, index) => {
                                                    return <div key={student.id}>
                                                        <Row>
                                                            <Col>
                                                                <Field
                                                                    name={`additionalStudents[${index}].email`}
                                                                    component={Input}
                                                                />
                                                            </Col>
                                                            <Col>
                                                                <Field
                                                                    name={`additionalStudents[${index}].fullname`}
                                                                    component={Input}
                                                                />
                                                            </Col>
                                                        </Row>
                                                        <IconContext.Provider value={{color: "red", size: "2em"}}>
                                                            <IoIosCloseCircle style={{marginTop: "5px"}}
                                                                              onClick={() => remove(index)}/>
                                                        </IconContext.Provider>
                                                        <hr/>
                                                    </div>
                                                })}
                                                <IconContext.Provider value={{color: "green", size: "2em"}}>
                                                    <IoIosAddCircle onClick={() => push({
                                                        id: generate(),
                                                        fullname: "",
                                                        email: ""
                                                    })}/>
                                                </IconContext.Provider>
                                                <hr/>
                                            </div>
                                        )
                                    }
                                </FieldArray>
                                <div>
                                    <Button variant={"primary"} type={"submit"}
                                            style={{marginTop: "20px"}}>Submit</Button>
                                </div>
                            </Form>
                        </>
                    )
                }
            </Formik>
        )
    }
}

export default DynamicApplyForm
