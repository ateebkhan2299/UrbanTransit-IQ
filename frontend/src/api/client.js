import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Section 7 Full Contract Endpoints
export const getSyncStatus = () => apiClient.get('/dashboard/sync-status');
export const getNotifications = (unreadOnly = false) => apiClient.get(`/notifications?unread_only=${unreadOnly}`);
export const getRoutesList = () => apiClient.get('/routes/list');
export const getDashboardSummary = (routeId = null) => apiClient.get(`/dashboard/summary${routeId ? `?route_id=${routeId}` : ''}`);
export const getTopRoutes = (limit = 5) => apiClient.get(`/dashboard/top-routes?limit=${limit}`);
export const getDelaysByCause = (routeId = null) => apiClient.get(`/delays/by-cause${routeId ? `?route_id=${routeId}` : ''}`);
export const getRoutesGeo = () => apiClient.get('/map/routes-geo');
export const getDelayHotspots = () => apiClient.get('/map/delay-hotspots');
export const getRouteById = (id) => apiClient.get(`/routes/${id}`);
export const simulateWhatIf = (payload) => apiClient.post('/whatif/simulate', payload);

// Additional Core Endpoints
export const getRoutes = () => apiClient.get('/routes');
export const getDelaysSummary = () => apiClient.get('/delays/summary');
export const getDelayedRoutes = () => apiClient.get('/delays/routes');
export const getOccupancyHourly = (routeId = null) => apiClient.get(`/occupancy/hourly${routeId ? `?route_id=${routeId}` : ''}`);
export const getOvercrowdedRoutes = (routeId = null) => apiClient.get(`/occupancy/overcrowded${routeId ? `?route_id=${routeId}` : ''}`);
export const getForecastDemand = (routeId = null) => apiClient.get(`/forecast/demand${routeId ? `?route_id=${routeId}` : ''}`);
export const getRecommendations = (routeId = null) => apiClient.get(`/recommendations${routeId ? `?route_id=${routeId}` : ''}`);
export const getModelComparison = () => apiClient.get('/models/comparison');

// New Dashboard Endpoints
export const getPassengerFlow = () => apiClient.get('/dashboard/passenger-flow');
export const getRoutePerformance = () => apiClient.get('/dashboard/route-performance');
export const getDelays = () => apiClient.get('/dashboard/delays');
export const getOccupancy = () => apiClient.get('/dashboard/occupancy');
export const getForecast = () => apiClient.get('/dashboard/forecast');
export const getDashboardRouteGeo = () => apiClient.get('/dashboard/route-geo');
export const exportReport = (type, format) => apiClient.get(`/reports/export?type=${type}&format=${format}`, { responseType: 'blob' });

export default apiClient;
