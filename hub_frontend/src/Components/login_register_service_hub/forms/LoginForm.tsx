import React from "react";
import {Form, Button, Alert,} from "react-bootstrap";
import {FormikProps, withFormik} from "formik";
import * as Yup from "yup"
import {RouteComponentProps} from "react-router-dom";
import {FormErrors} from "./CommonInterfaces";


interface LoginFormValues{
    email: string,
    password: string,
}
interface LoginFormProps extends RouteComponentProps{
    initialEmail?: string
    initialPassword?: string
}



const FormikLoginForm = (props: FormikProps< FormErrors & LoginFormValues > ) => {
    const {
        values,
        errors,
        touched,
        handleBlur,
        handleChange,
        handleSubmit,
        isSubmitting,
    } = props
    return (
        <>
            <Form onSubmit={handleSubmit}>
              <Form.Group controlId="formBasicEmail">
                <Form.Label>Email address</Form.Label>
                <Form.Control type="email"  onBlur = {handleBlur} placeholder="Enter email" name="email" onChange={handleChange} value={values.email} />
                <Form.Text className="text-muted">
                  We'll never share your email with anyone else. <br/>
                    {(touched.email && errors.email) && <Alert variant={"danger"} >{errors.email}</Alert>}
                </Form.Text>
              </Form.Group>

              <Form.Group controlId="formBasicPassword">
                <Form.Label>Password</Form.Label>
                <Form.Control type="password" onBlur = {handleBlur} placeholder="Password" name="password" onChange={handleChange} value={values.password}/>
                <Form.Text>
                    { (touched.password && errors.password) && <Alert variant={"danger"} >{errors.password}</Alert>}
                </Form.Text>
              </Form.Group>
              <Button variant="primary" type="submit" disabled={
                        isSubmitting ||
                        !!(errors.email && touched.email) ||
                        !!(errors.password && touched.password)
                    }>
                Login
              </Button>
              {errors.authentication && <Alert variant={"danger"} style={{marginTop: "5px"}}>{errors.authentication}</Alert>}
            </Form>
        </>
    )
}

const LoginForm = withFormik<LoginFormProps, LoginFormValues>({

    mapPropsToValues: props => ({
        email: props.initialEmail || "",
        password: props.initialPassword || ""
    }),
    validationSchema: Yup.object().shape({
        email: Yup.string()
            .email("Email not valid")
            .required("Email is required"),
        password: Yup.string().required("Password is required")
    }),
    handleSubmit(
        {email, password}: LoginFormValues,
        {props, setSubmitting, setFieldError}
    ){
        fetch('http://localhost:8000/login/api/login/', {
            method: "POST",
            body: JSON.stringify({username: email, password: password}),
            headers: {
              'Content-Type': 'application/json'
            },

        })
          .then(response => response.json())
          .then(data => {
              if(data.access) {
                  localStorage.setItem("token", data.access)
                  localStorage.setItem("refresh", data.refresh)
                  props.history.push("/house")
              }else{
                  setFieldError("authentication","Authentication failed!")
                  setSubmitting(false);
              }
          } );
    }
})( FormikLoginForm )

export default LoginForm