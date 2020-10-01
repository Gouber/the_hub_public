import React from "react";
import {Form, Button, Alert} from "react-bootstrap";
import {RouteComponentProps} from "react-router-dom"
import {FormikProps, withFormik} from "formik";
import {FormErrors} from "./CommonInterfaces";
import * as Yup from "yup";



interface RegisterFormProps extends RouteComponentProps{
    initialEmail?: string,
    initialUsername?: string,
    initialPassword?: string,
    initialPasswordConfirm?: string
}

interface RegisterFormValues{
    email: string,
    username: string,
    password: string,
    password_confirm: string
}

const FormikRegisterForm = (props: FormikProps< FormErrors & RegisterFormValues > ) => {
        const {
            values,
            errors,
            touched,
            handleBlur,
            handleChange,
            handleSubmit,
            isSubmitting,
        } = props

        return (<>
            <Form onSubmit={handleSubmit}>
                  <Form.Group controlId="formBasicEmail">
                    <Form.Label>Email address</Form.Label>
                    <Form.Control type="email"
                                  placeholder="Enter email"
                                  name="email"
                                  onBlur={handleBlur}
                                  onChange={handleChange}
                                  value={values.email}/>
                    <Form.Text className="text-muted">
                      We'll never share your email with anyone else.
                    </Form.Text>
                  {(touched.email && errors.email) && <Alert variant={"danger"} >{errors.email}</Alert>}
                  </Form.Group>

                  <Form.Group controlId="formUsername">
                    <Form.Label>Username</Form.Label>
                    <Form.Control type="text"
                                  placeholder="Enter Username"
                                  name="username"
                                  onBlur={handleBlur}
                                  onChange={handleChange}
                                  value={values.username} />
                    <Form.Text className="text-muted">
                      Leave blank for your username to be your email
                    </Form.Text>
                      {(touched.username && errors.username) && <Alert variant={"danger"} >{errors.username}</Alert>}
                  </Form.Group>

                  <Form.Group controlId="formBasicPassword">
                    <Form.Label>Password</Form.Label>
                    <Form.Control type="password"
                                  placeholder="Password"
                                  name="password"
                                  onBlur={handleBlur}
                                  onChange={handleChange}
                                  value={values.password}/>
                    {(touched.password && errors.password) && <Alert variant={"danger"} >{errors.password}</Alert>}
                  </Form.Group>

                  <Form.Group controlId="formBasicPasswordConfirmation">
                    <Form.Label>Confirm Password</Form.Label>
                    <Form.Control type="password"
                                  placeholder="Confirm Password"
                                  name="password_confirm"
                                  onBlur={handleBlur}
                                  onChange={handleChange}
                                  value={values.password_confirm} />
                    {(touched.password_confirm && errors.password_confirm) && <Alert variant={"danger"} >{errors.password_confirm}</Alert>}
                  </Form.Group>
                  <Button variant="primary" type="submit" disabled={
                        isSubmitting ||
                        !!(errors.email && touched.email) ||
                        !!(errors.password && touched.password) ||
                        !!(errors.password_confirm && touched.password_confirm) ||
                        !!(errors.username && touched.username)
                    }>
                    Register
                  </Button>
                  {errors.authentication && <Alert variant={"danger"} style={{marginTop: "5px"}}>{errors.authentication}</Alert>}
                </Form>
        </>)
}

function equalTo(ref: any, msg: any) {
  return Yup.mixed().test({
    name: 'equalTo',
    exclusive: false,
    message: msg || '${path} must be the same as ${reference}',
    params: {
      reference: ref.path,
    },
    test: function(value: any) {
      return value === this.resolve(ref);
    },
  });
}
Yup.addMethod(Yup.string, 'equalTo', equalTo);


const RegisterForm = withFormik<RegisterFormProps,RegisterFormValues>({
        mapPropsToValues: props => ({
            email: props.initialEmail || "",
            password: props.initialPassword || "",
            password_confirm: props.initialPasswordConfirm || "",
            username: props.initialUsername || ""
        }),
        validationSchema: Yup.object().shape({
            email: Yup.string()
                .email("Email not valid")
                .required("Email is required"),
            password: Yup.string()
                .required("Password is required"),
            username: Yup.string(),
            //@ts-ignore
            password_confirm: Yup.string().equalTo(Yup.ref('password'),"Passwords must match").required("This field is mandatory")
        }),
        handleSubmit(
        {email, password, username, password_confirm}: RegisterFormValues,
        {props, setSubmitting, setFieldError}
        ){
             fetch("http://localhost:8000/login/api/register-student/",{
                method: "POST",
                body: JSON.stringify({
                    username: username,
                    password: password,
                    email: email
                }),
                headers: {
                  'Content-Type': 'application/json'
                },
             })
                .then(response => response.json())
                 .then(data => {
                     console.log("Student registered", data)
                     if(data.access){
                         //successful we can store the token effectively logging in the guy
                         localStorage.setItem("token", data.access)
                         localStorage.setItem("refresh", data.refresh)
                         props.history.push("/house")
                     }else{
                         setFieldError("authentication","Something went wrong with the registering service.")
                     }
                 })
        }
})(FormikRegisterForm)

export default RegisterForm
