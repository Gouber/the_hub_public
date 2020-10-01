import {FormikErrors} from "formik";

export interface Auth{
    authentication: string
}
export interface FormErrors extends FormikErrors<Auth>{}