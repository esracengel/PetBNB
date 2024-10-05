import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import '../styles/Form.css';

function Register() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState(null);
  const navigate = useNavigate();


  useEffect(() => {
    document.title = "PetBnB - Register";
  },[]);
  const initialValues = {
    email: '',
    username: '',
    password: '',
    re_password: '',
    user_type: 'petowner'
  };

  const validationSchema = Yup.object({
    email: Yup.string().email('Invalid email address').required('Required'),
    username: Yup.string().required('Required'),
    password: Yup.string()
      .min(8, 'Password must be at least 8 characters')
      .matches(/[a-zA-Z]/, 'Password must contain at least one letter')
      .matches(/[0-9]/, 'Password must contain at least one number')
      .required('Password is required'),
    re_password: Yup.string()
      .oneOf([Yup.ref('password'), null], 'Passwords must match')
      .required('Required'),
    user_type: Yup.string().required('Required')
  });


  const registerUser = async (values) => {
    setIsSubmitting(true);
    try {
      const response = await fetch('http://localhost:8000/auth/users/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values),
      });
      const data = await response.json();
      if (response.ok) {
        setSubmitResult({ success: true, message: 'Registration successful!' });
      } else {
        const errorMessage = Object.values(data).flat().join(' ');
        setSubmitResult({ success: false, message: errorMessage || 'Registration failed.' });
      }
    } catch (error) {
      setSubmitResult({ success: false, message: 'An error occurred. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };


  if (isSubmitting) {
    return <div>Registering user...</div>;
  }

  if (submitResult) {
    return (
      <div>
        <h2>{submitResult.success ? 'Registration Successful' : 'Registration Failed'}</h2>
        <p>{submitResult.message}</p>
        {submitResult.success ? (
          <button onClick={() => navigate('/login')}>Go to Login</button>
        ) : (
          <button onClick={() => setSubmitResult(null)}>Try Again</button>
        )}
      </div>
    );
  }

  return (
    <div>
      <h1>Registration</h1>
      <Formik
        initialValues={initialValues}
        validationSchema={validationSchema}
        onSubmit={registerUser}
      >
        <Form>
          <div>
            <label htmlFor="email">Email:</label>
            <Field type="email" id="email" name="email" />
            <ErrorMessage name="email" component="div" className="error" />
          </div>
          <div>
            <label htmlFor="username">Username:</label>
            <Field type="text" id="username" name="username" />
            <ErrorMessage name="username" component="div" className="error" />
          </div>
          <div>
            <label htmlFor="password">Password:</label>
            <Field type="password" id="password" name="password" />
            <ErrorMessage name="password" component="div" className="error" />
          </div>
          <div>
            <label htmlFor="re_password">Confirm Password:</label>
            <Field type="password" id="re_password" name="re_password" />
            <ErrorMessage name="re_password" component="div" className="error" />
          </div>
          <div>
            <label htmlFor="user_type">User Type:</label>
            <Field as="select" id="user_type" name="user_type">
              <option value="petowner">Pet Owner</option>
              <option value="caregiver">Caregiver</option>
            </Field>
            <ErrorMessage name="user_type" component="div" className="error" />
          </div>
          <button type="submit">Register</button>
        </Form>
      </Formik>
    </div>
  );
}

export default Register;