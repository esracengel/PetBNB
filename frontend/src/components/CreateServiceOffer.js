import React, { useState } from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { useAuth } from '../context/AuthContext';
import '../styles/ServiceComponents.css';

const CreateServiceOffer = ({ isOpen, onClose, onSubmit, serviceRequest, existingOffer }) => {
    const { user } = useAuth();
    const [error, setError] = useState(null);

    if (!isOpen) return null;

    const validationSchema = Yup.object({
        price: Yup.number()
            .required('Required')
            .positive('Price must be positive')
            .min(0.01, 'Minimum price is $0.01'),
        message: Yup.string()
            .required('Required')
            .min(10, 'Message must be at least 10 characters')
            .max(500, 'Message must not exceed 500 characters'),
    });

    const handleSubmit = async (values, { setSubmitting }) => {
        try {
            await onSubmit(values, serviceRequest, existingOffer);
            onClose();
        } catch (error) {
            console.error('Error submitting offer:', error);
            setError(error.message || 'An error occurred while submitting the offer. Please try again.');
        } finally {
            setSubmitting(false);
        }
    };

    const initialValues = existingOffer
        ? { price: existingOffer.price, message: existingOffer.message }
        : { price: 10.00, message: `Hello, I'm ${user.username}. I'd love to take care of your pet.` };

    const headerText = (existingOffer ? 'Update Offer' : 'New Offer') + " for " +  serviceRequest.owner_display_name + "'s " + serviceRequest.pet_type;

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <h2 className='modal-header'>{headerText}</h2>
                <div className="request-details">
                    <p>Pet: {serviceRequest.pet_type} ({serviceRequest.pet_breed})</p>
                    <p>Dates: {serviceRequest.start_date} to {serviceRequest.end_date}</p>
                    <p>Location: {serviceRequest.location}</p>
                </div>
                {error && <div className="error-message">{error}</div>}
                <Formik
                    initialValues={initialValues}
                    validationSchema={validationSchema}
                    onSubmit={handleSubmit}
                >
                    {({ isSubmitting }) => (
                        <Form>
                            <div className="form-group">
                                <label htmlFor="price">Price per day ($)</label>
                                <Field type="number" id="price" name="price" step="0.01" />
                                <ErrorMessage name="price" component="div" className="error" />
                            </div>
                            <div className="form-group">
                                <label htmlFor="message">Message to pet owner</label>
                                <Field as="textarea" id="message" name="message" className= 'message-input'/>
                                <ErrorMessage name="message" component="div" className="error" />
                            </div>
                            <div className="button-group">
                                <button type="submit" disabled={isSubmitting}>
                                    {isSubmitting ? 'Submitting...' : (existingOffer ? 'Update Offer' : 'Submit Offer')}
                                </button>
                                <button type="button" onClick={onClose}>Cancel</button>
                            </div>
                        </Form>
                    )}
                </Formik>
            </div>
        </div>
    );
};

export default CreateServiceOffer;