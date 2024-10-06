import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/Services.css';

const ServiceRequestSummary = ({ request, existingOffer, onDeleteRequest, onCreateOrUpdateOffer, onDeleteOffer, onViewOffers }) => {
  const [expanded, setExpanded] = useState(false);

  const { user } = useAuth();

  const toggleExpand = () => {
    setExpanded(!expanded);
  };


  const isOwner = user.id === request.owner;
  const isCaregiver = user.user_type === 'caregiver';
  const ownerIdentifier = request.owner_display_name || request.owner_email || 'Unknown Owner';


  return (
    <div className="service-request-summary">
      <div className="service-request-header">
        <h3>{request.pet_type} {request.pet_breed ? "- " + request.pet_breed:''}</h3>
        <span className="owner-identifier">{ownerIdentifier}</span>
      </div>
      <div className="service-request-content" onClick={toggleExpand}>
        <p>Location: {request.location}</p>
        <p>Dates: {request.start_date} to {request.end_date}</p>
        {expanded && (
          <div className="service-request-details">
            <p>{request.description}</p>
            {isOwner && (
              <div className="service-functions right-align">
                {request.total_offers_count >0 ? <button onClick={(e) => { e.stopPropagation(); onViewOffers(request); }} className="view-offers"> 
                  View Offers ({request.pending_offers_count})
                </button>:<p></p>}
                <button onClick={(e) => { e.stopPropagation(); onDeleteRequest(request.id); }} className="delete-button">
                  Delete Request
                </button>
              </div>
            )}
            {isCaregiver && !isOwner && (
              existingOffer ? (
                <div className="service-functions right-align">
                  <span>Offer submitted on {new Date(existingOffer.created_at).toLocaleDateString()}</span>
                  <button onClick={(e) => { e.stopPropagation(); onCreateOrUpdateOffer(request, existingOffer); }} className="make-offer-button right-align">
                    Update Offer
                  </button>
                  <button onClick={(e) => { e.stopPropagation(); onDeleteOffer(existingOffer.id); }} className="delete-button">
                    Delete Offer
                  </button>
                </div>
              ) : (
                <button onClick={(e) => { e.stopPropagation(); onCreateOrUpdateOffer(request); }} className="make-offer-button right-align">
                  Make an Offer
                </button>
              )
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ServiceRequestSummary;