import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import ServiceRequestSummary from '../components/ServiceRequestSummary';
import CreateServiceRequest from '../components/CreateServiceRequest';
import CreateServiceOffer from '../components/CreateServiceOffer';
import '../styles/Services.css';

const Services = () => {
  //Title and user
  useEffect(() => {
    document.title = "PetBnB - Services";
    fetchServiceRequests();
  }, []);
  const { user } = useAuth();
  //Requests and sorting/filtering
  const [serviceRequests, setServiceRequests] = useState([]);
  const [filteredRequests, setFilteredRequests] = useState([]);
  const [filterCriteria, setFilterCriteria] = useState({
    petType: '',
    location: '',
    startDate: '',
    endDate: '',
  });
  const petTypes = ['', 'Cat', 'Dog', 'Bird', 'Fish', 'Turtle', 'Hamster'];
  const [sortCriteria, setSortCriteria] = useState('startDate');

  //State of sub components
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isOfferModalOpen, setIsOfferModalOpen] = useState(false);

  //Selected objects
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [userOffers, setUserOffers] = useState(null);

  //SERVICE REQUEST QUERIES:
  //1. Fetching all requests:
  const fetchServiceRequests = async () => {
    try {
      const response = await fetch('http://localhost:8000/services/service-requests/', {
        headers: {
          'Authorization': `JWT ${localStorage.getItem('accessToken')}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setServiceRequests(data);
        setFilteredRequests(data);
      } else {
        console.error('Failed to fetch service requests');
      }
    } catch (error) {
      console.error('Error fetching service requests:', error);
    }
  };

  //2. Sorting and Filtering requests
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilterCriteria({ ...filterCriteria, [name]: value });
  };

  const handleSortChange = (e) => {
    setSortCriteria(e.target.value);
  };

  useEffect(() => { //Filtering and sorting fetched requests
    let filtered = [...serviceRequests];
    if (filterCriteria.petType) {
      filtered = filtered.filter(request => request.pet_type === filterCriteria.petType);
    }
    if (filterCriteria.location) {
      filtered = filtered.filter(request => request.location.toLowerCase().includes(filterCriteria.location.toLowerCase()));
    }
    if (filterCriteria.startDate) {
      filtered = filtered.filter(request => new Date(request.start_date) >= new Date(filterCriteria.startDate));
    }
    if (filterCriteria.endDate) {
      filtered = filtered.filter(request => new Date(request.end_date) <= new Date(filterCriteria.endDate));
    }

    filtered.sort((a, b) => {
      if (sortCriteria === 'startDate') {
        return new Date(a.start_date) - new Date(b.start_date);
      } else if (sortCriteria === 'endDate') {
        return new Date(a.end_date) - new Date(b.end_date);
      }
      return 0;
    });

    setFilteredRequests(filtered);
  }, [serviceRequests, filterCriteria, sortCriteria]);

  // REQUEST AND OFFER CRUD

  //1. Creating a request
  const handleCreateRequest = async (values) => {
    try {
      const response = await fetch('http://localhost:8000/services/service-requests/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `JWT ${localStorage.getItem('accessToken')}`,
        },
        body: JSON.stringify(values),
      });

      if (response.ok) {
        fetchServiceRequests();
      } else {
        console.error('Failed to create service request');
      }
    } catch (error) {
      console.error('Error creating service request:', error);
    }
  };

  //2. Deleting a request
  const handleDeleteRequest = async (requestId) => {
    try {
      if (!window.confirm('Are you sure you want to delete this service request?')) return;

      const response = await fetch(`http://localhost:8000/services/service-requests/${requestId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `JWT ${localStorage.getItem('accessToken')}`,
        },
      });
      if (response.ok) {
        setServiceRequests(prevRequests => prevRequests.filter(request => request.id !== requestId));
        setFilteredRequests(prevRequests => prevRequests.filter(request => request.id !== requestId));
      } else {
        console.error('Failed to delete service request');
      }
    } catch (error) {
      console.error('Error deleting service request:', error);
    }
  };

  //3. Creating or updating an offer
  const handleCreateOrUpdateOfferClicked = (request) =>
  {
    setIsOfferModalOpen(true);
    setSelectedRequest(request);
    fetchAllOffers();

  }

  const handleSubmitOffer = async (values, request, existingOffer, setExistingOffer) => {
    try {
      const url = existingOffer
        ? `http://localhost:8000/services/service-offers/${existingOffer.id}/`
        : 'http://localhost:8000/services/service-offers/';
      const method = existingOffer ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `JWT ${localStorage.getItem('accessToken')}`,
        },
        body: JSON.stringify({
          ...values,
          caregiver: user.id,
          service_request: request.id
        }),
      });

      if (response.ok) {
        console.log(existingOffer ? 'Offer updated successfully' : 'Offer created successfully');
        fetchServiceRequests();
        setIsOfferModalOpen(false);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit offer');
      }
    } catch (error) {
      console.error('Error submitting offer:', error);
      throw error;
    }
  };


  //4. Deleting an offer
  const handleDeleteOffer = async (offerId) => {
    try {
      if (!window.confirm('Are you sure you want to delete this service offer?')) return;

      const response = await fetch(`http://localhost:8000/services/service-offers/${offerId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `JWT ${localStorage.getItem('accessToken')}`,
        },
      });

      if (response.ok) {
        console.log('Offer deleted successfully');
        fetchServiceRequests(); // Refresh the service requests to reflect the changes
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete service offer');
      }
    } catch (error) {
      console.error('Error deleting offer:', error);
      throw error;
    }
  };

  const handleViewOffers = (request) => {
    // TODO
    console.log('Viewing offers for request:', request.id);
  };

  //5. Fetching existing offers
  const fetchUserOffer = async (request) => {
    if (user && user.user_type === 'caregiver') {
      try {
        const response = await fetch(`http://localhost:8000/services/service-offers/?service_request=${request.id}&caregiver=${user.id}`, {
          headers: {
            'Authorization': `JWT ${localStorage.getItem('accessToken')}`,
          },
        });
        if (response.ok) {
          const offers = await response.json();
          if (offers.length > 0) {
            return(offers[0]);
          }
          else {
            return null;
          }
        }
        else{
          return null;
        }
      } catch (error) {
        console.error('Error fetching user offer:', error);
        return null;
      }
    }
  };

  const fetchAllOffers = async () => {
    const offers = {};
    for (const request of filteredRequests) {
      let offer = await fetchUserOffer(request);
      offers[request.id] = offer;
    }
    setUserOffers(offers);
  };

  useEffect(() => {
    
    fetchAllOffers();
  }, [filteredRequests]);


  return (
    <div className="services-page">
      <h1>Service Requests</h1>
      {user && user.user_type === 'petowner' && (
        <button onClick={() => setIsCreateModalOpen(true)} className="add-request-button">
          Add New Request
        </button>
      )}
      <div className="filter-sort-container">
        <select
          name="petType"
          value={filterCriteria.petType}
          onChange={handleFilterChange}
        >
          <option value="">All Pet Types</option>
          {petTypes.slice(1).map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
        <input
          type="text"
          name="location"
          placeholder="Filter by location"
          value={filterCriteria.location}
          onChange={handleFilterChange}
        />
        <input
          type="date"
          name="startDate"
          value={filterCriteria.startDate}
          onChange={handleFilterChange}
        />
        <input
          type="date"
          name="endDate"
          value={filterCriteria.endDate}
          onChange={handleFilterChange}
        />
        <select value={sortCriteria} onChange={handleSortChange}>
          <option value="startDate">Sort by Start Date</option>
          <option value="endDate">Sort by End Date</option>
        </select>
      </div>
      <div className="service-requests-list">
        {filteredRequests.map(request => (
          <ServiceRequestSummary
            key={request.id}
            request={request}
            existingOffer={userOffers[request.id]}
            onDeleteRequest={handleDeleteRequest}
            onCreateOrUpdateOffer={handleCreateOrUpdateOfferClicked}
            onDeleteOffer={handleDeleteOffer}
            onViewOffers = {handleViewOffers}
          />
        ))}
      </div>
      <CreateServiceRequest
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateRequest}
      />
      <CreateServiceOffer
        isOpen={isOfferModalOpen}
        onClose={() => setIsOfferModalOpen(false)}
        onSubmit={handleSubmitOffer}
        serviceRequest={selectedRequest}
        existingOffer={selectedRequest? userOffers[selectedRequest.id]: null}
      />
    </div>
  );
};

export default Services;