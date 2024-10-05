import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { useAuth } from '../context/AuthContext';
import '../styles/Form.css';

function Login() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { login } = useAuth();

  useEffect(() => {
    document.title = "PetBnB - Login";
  },[]);

  const initialValues = {
    email: '',
    password: '',
    rememberMe: false
  };

  const validationSchema = Yup.object({
    email: Yup.string().email('Invalid email address').required('Required'),
    password: Yup.string().required('Required')
  });

  const handleSubmit = async (values) => {
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/auth/jwt/create/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: values.email,
          password: values.password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Store the tokens
        localStorage.setItem('accessToken', data.access);
        localStorage.setItem('refreshToken', data.refresh);
        // Update the auth context
        login({ email: values.email });
        // Redirect to home page or dashboard
        navigate('/');
      } else {
        setError(data.detail || 'Login failed. Please check your credentials.');
      }
    } catch (error) {
      setError('An error occurred. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="login-form">
      <h1>Login</h1>
      <Formik
        initialValues={initialValues}
        validationSchema={validationSchema}
        onSubmit={handleSubmit}
      >
        <Form>
          <div>
            <label htmlFor="email">Email:</label>
            <Field type="email" id="email" name="email" />
            <ErrorMessage name="email" component="div" className="error" />
          </div>
          <div>
            <label htmlFor="password">Password:</label>
            <Field type="password" id="password" name="password" />
            <ErrorMessage name="password" component="div" className="error" />
          </div>
          <div className="checkbox-container">
            <label htmlFor="rememberMe">Remember me</label>
            <Field type="checkbox" id="rememberMe" name="rememberMe" />
          </div>
          <div>
            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Logging in...' : 'Login'}
            </button>
          </div>
          {error && <div className="error">{error}</div>}
        </Form>
      </Formik>
      <div className="login-links">
        <Link to="/forgot-password">Forgot Password?</Link>
        <br />
        Don't have an account? <Link to="/register">Register</Link>
      </div>
    </div>
  );
}

export default Login;