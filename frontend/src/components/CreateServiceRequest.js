import React, { useState } from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import '../styles/ServiceComponents.css';

const CreateServiceRequest = ({ isOpen, onClose, onSubmit }) => {

  const petTypes = ['Cat', 'Dog', 'Bird', 'Fish', 'Turtle', 'Hamster'];
  const [error, setError] = useState(null);
  if (!isOpen) return null;

  const initialValues = {
    pet_type: '',
    pet_breed: '',
    start_date: '',
    end_date: '',
    location: '',
    description: ''
  };

  const validationSchema = Yup.object().shape({
    pet_type: Yup.string().required('Required'),
    pet_breed: Yup.string().test('is-breed-required', 'Required for dogs', function (value) {
      return this.parent.pet_type !== 'Dog' || (this.parent.pet_type === 'Dog' && value);
    }),
    start_date: Yup.date().required('Required'),
    end_date: Yup.date().min(
      Yup.ref('start_date'),
      "End date can't be before start date"
    ).required('Required'),
    location: Yup.string().required('Required'),
    description: Yup.string().required('Required')
  });

  const handleSubmit = async (values, { setSubmitting }) => {

    try {
      await onSubmit(values);
      onClose();
    } catch (error) {
      console.error('Error submitting offer:', error);
      setError(error.message || 'An error occurred while submitting the offer. Please try again.');
    } finally {
      setSubmitting(false);
    }

  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Create New Service Request</h2>
        {error && <div className="error-message">{error}</div>}
        <Formik
          initialValues={initialValues}
          validationSchema={validationSchema}
          onSubmit={handleSubmit}
        >
          {({ values, setFieldValue, isSubmitting }) => (
            <Form>
              <div className="form-group">
                <label htmlFor="pet_type">Pet Type</label>
                <Field as="select" name="pet_type" onChange={(e) => {
                  setFieldValue('pet_type', e.target.value);
                  setFieldValue('pet_breed', '');
                }}>
                  <option value="">Select a pet type</option>
                  {petTypes.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </Field>
                <ErrorMessage name="pet_type" component="div" className="error" />
              </div>

              <div className="form-group">
                <label htmlFor="pet_breed">Pet Breed</label>
                <Field type="text" name="pet_breed" />
                <ErrorMessage name="pet_breed" component="div" className="error" />
                {values.pet_type === 'Dog' && (
                  <small className="helper-text">Required for dogs</small>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="start_date">Start Date</label>
                <Field type="date" name="start_date" />
                <ErrorMessage name="start_date" component="div" className="error" />
              </div>

              <div className="form-group">
                <label htmlFor="end_date">End Date</label>
                <Field type="date" name="end_date" />
                <ErrorMessage name="end_date" component="div" className="error" />
              </div>

              <div className="form-group">
                <label htmlFor="location">Location</label>
                <Field type="text" name="location" />
                <ErrorMessage name="location" component="div" className="error" />
              </div>

              <div className="form-group">
                <label htmlFor="description">Description</label>
                <Field as="textarea" name="description" />
                <ErrorMessage name="description" component="div" className="error" />
              </div>

              <div className="button-group">
                <button type="submit" disabled={isSubmitting}>
                  Submit
                </button>
                <button type="button" onClick={onClose}>
                  Cancel
                </button>
              </div>
            </Form>
          )}
        </Formik>
      </div>
    </div>
  );
};

export default CreateServiceRequest;