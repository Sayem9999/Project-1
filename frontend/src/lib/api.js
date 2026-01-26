import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const api = {
  // Auth
  register: (data) => axios.post(`${API}/auth/register`, data),
  login: (data) => axios.post(`${API}/auth/login`, data),
  getMe: () => axios.get(`${API}/auth/me`, { headers: getAuthHeader() }),

  // Listings
  createListing: (data) => axios.post(`${API}/listings`, data, { headers: getAuthHeader() }),
  getListings: (params) => axios.get(`${API}/listings`, { params }),
  getListing: (id) => axios.get(`${API}/listings/${id}`),
  getMyListings: () => axios.get(`${API}/users/me/listings`, { headers: getAuthHeader() }),

  // Bids
  placeBid: (data) => axios.post(`${API}/bids`, data, { headers: getAuthHeader() }),
  getListingBids: (listingId) => axios.get(`${API}/bids/${listingId}`),
  getUserBids: (userId) => axios.get(`${API}/users/${userId}/bids`),

  // Watchlist
  addToWatchlist: (listingId) => axios.post(`${API}/watchlist`, { listing_id: listingId }, { headers: getAuthHeader() }),
  removeFromWatchlist: (listingId) => axios.delete(`${API}/watchlist/${listingId}`, { headers: getAuthHeader() }),
  getWatchlist: () => axios.get(`${API}/watchlist`, { headers: getAuthHeader() }),

  // Payments
  createCheckout: (data) => axios.post(`${API}/payments/checkout`, data, { headers: getAuthHeader() }),
  getPaymentStatus: (sessionId) => axios.get(`${API}/payments/status/${sessionId}`, { headers: getAuthHeader() }),
};

export default api;