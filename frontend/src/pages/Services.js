import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import ServiceRequestSummary from '../components/ServiceRequestSummary';
import CreateServiceRequest from '../components/CreateServiceRequest';
import '../styles/Services.css';

const Services = () => {
  const [serviceRequests, setServiceRequests] = useState([]);
  const [filteredRequests, setFilteredRequests] = useState([]);
  const [filterCriteria, setFilterCriteria] = useState({
    petType: '',
    location: '',
    startDate: '',
    endDate: '',
  });
  const [sortCriteria, setSortCriteria] = useState('startDate');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const { user } = useAuth();

  const petTypes = ['', 'Cat', 'Dog', 'Bird', 'Fish', 'Turtle', 'Hamster'];

  useEffect(() => {
    document.title = "PetBnB - Services";
  },[]);
  useEffect(() => {
    fetchServiceRequests();
  }, []);

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

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilterCriteria({ ...filterCriteria, [name]: value });
  };

  const handleSortChange = (e) => {
    setSortCriteria(e.target.value);
  };

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
      console.log(JSON.stringify(values));

      if (response.ok) {
        fetchServiceRequests();  // Refresh the list after creating a new request
      } else {
        console.error('Failed to create service request');
      }
    } catch (error) {
      console.error('Error creating service request:', error);
    }
  };

  useEffect(() => {
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
          <ServiceRequestSummary key={request.id} request={request} />
        ))}
      </div>
      <CreateServiceRequest
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateRequest}
      />
    </div>
  );
};

export default Services;