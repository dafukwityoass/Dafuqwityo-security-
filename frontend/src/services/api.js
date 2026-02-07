import axios from 'axios';

// Get backend URL from environment
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: async (userData) => {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  },
  
  login: async (credentials) => {
    const response = await api.post('/api/auth/login', credentials);
    return response.data;
  },
  
  logout: async () => {
    const response = await api.post('/api/auth/logout');
    return response.data;
  },
  
  getMe: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  }
};

// Bills API
export const billsAPI = {
  getBills: async () => {
    const response = await api.get('/api/bills');
    return response.data;
  },
  
  createBill: async (billData) => {
    const response = await api.post('/api/bills', billData);
    return response.data;
  },
  
  updateBill: async (billId, updateData) => {
    const response = await api.put(`/api/bills/${billId}`, updateData);
    return response.data;
  },
  
  deleteBill: async (billId) => {
    const response = await api.delete(`/api/bills/${billId}`);
    return response.data;
  }
};

// Payment Methods API
export const paymentMethodsAPI = {
  getPaymentMethods: async () => {
    const response = await api.get('/api/payment-methods');
    return response.data;
  },
  
  createPaymentMethod: async (methodData) => {
    const response = await api.post('/api/payment-methods', methodData);
    return response.data;
  },
  
  deletePaymentMethod: async (methodId) => {
    const response = await api.delete(`/api/payment-methods/${methodId}`);
    return response.data;
  }
};

// Payments API
export const paymentsAPI = {
  processPayment: async (paymentData) => {
    const response = await api.post('/api/payments/process', paymentData);
    return response.data;
  },
  
  getPaymentHistory: async () => {
    const response = await api.get('/api/payments/history');
    return response.data;
  }
};

// Lightning API
export const lightningAPI = {
  createInvoice: async (amount_usd, memo) => {
    const response = await api.post('/api/lightning/invoice', { amount_usd, memo });
    return response.data;
  },
  
  verifyPayment: async (payment_hash) => {
    const response = await api.post('/api/lightning/verify', { payment_hash });
    return response.data;
  }
};

// Dashboard API
export const dashboardAPI = {
  getMetrics: async () => {
    const response = await api.get('/api/dashboard/metrics');
    return response.data;
  }
};

export default api;