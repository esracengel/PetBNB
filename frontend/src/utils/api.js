// src/utils/api.js

const API_URL = 'http://localhost:8000';

export const apiCall = async (endpoint, method = 'GET', body = null) => {
  const token = localStorage.getItem('accessToken');

  const headers = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `JWT ${token}`;
  }

  const config = {
    method,
    headers,
  };

  if (body) {
    config.body = JSON.stringify(body);
  }

  const response = await fetch(`${API_URL}${endpoint}`, config);

  if (response.status === 401) {
    // Token has expired, attempt to refresh
    const refreshed = await refreshToken();
    if (refreshed) {
      // Retry the original request
      return apiCall(endpoint, method, body);
    } else {
      // Refresh failed, redirect to login
      window.location.href = '/login';
    }
  }

  return response;
};

const refreshToken = async () => {
  const refreshToken = localStorage.getItem('refreshToken');
  if (!refreshToken) return false;

  try {
    const response = await fetch(`${API_URL}/auth/jwt/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('accessToken', data.access);
      return true;
    } else {
      return false;
    }
  } catch (error) {
    return false;
  }
};