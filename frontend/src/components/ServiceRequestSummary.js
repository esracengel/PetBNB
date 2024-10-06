import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/Services.css';

const ServiceRequestSummary = ({ request, onDelete }) => {
  const [expanded, setExpanded] = useState(false);
  const { user } = useAuth();

  const toggleExpand = () => {
    setExpanded(!expanded);
  };

  const isOwner = user.id === request.owner;

  const isCaregiver = user.user_type === 'caregiver';

  const ownerIdentifier = request.owner_display_name || request.owner_email || 'Unknown Owner';

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this service request?')) {
      try {
        const response = await fetch(`http://localhost:8000/services/service-requests/${request.id}/`, {
          method: 'DELETE',
          headers: {
            'Authorization': `JWT ${localStorage.getItem('accessToken')}`,
          },
        });
        if (response.ok) {
          onDelete(request.id);
        } else {
          console.error('Failed to delete service request');
        }
      } catch (error) {
        console.error('Error deleting service request:', error);
      }
    }
  };

  return (
    <div className="service-request-summary">
      <div className="service-request-header">
        <h3>{request.pet_type} - {request.pet_breed}</h3>
        <span className="owner-identifier">{ownerIdentifier}</span>
      </div>
      <div className="service-request-content" onClick={toggleExpand}>
        <p>Location: {request.location}</p>
        <p>Dates: {request.start_date} to {request.end_date}</p>
        {expanded && (
          <div className="service-request-details">
            <p>Description: {request.description}</p>
            {isOwner && (
              <div className = "service-functions right-align">
                <Link to={`/service-request/${request.id}/offers`} className = "view-offers">View Offers</Link>
                <button onClick={(e) => { e.stopPropagation(); handleDelete(); }} className="delete-button">
                  Delete Request
                </button>
              </div>
            )}
            {isCaregiver && !isOwner && (
                <div className='service-functions right-align'>
                    <Link to={`/service-request/${request.id}/make-offer`}>Make Offer</Link>
                </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ServiceRequestSummary;