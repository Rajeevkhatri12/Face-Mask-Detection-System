import axios from 'axios';

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || (import.meta.env.PROD ? '/api' : 'http://localhost:8000');

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000
});

export const buildAssetUrl = (path) => {
  if (!path) return '';
  if (path.startsWith('http') || path.startsWith('data:')) return path;
  return `${API_BASE_URL}${path}`;
};

export const predictImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post('/predict-image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return data;
};

export const predictCameraFrame = async (imageBase64, persist = false, signal) => {
  const { data } = await api.post('/predict-camera-frame', {
    image_base64: imageBase64,
    persist
  }, {
    signal,
    timeout: 60000
  });
  return data;
};

export const getStatistics = async () => {
  const { data } = await api.get('/statistics');
  return data;
};

export const getHistory = async (limit = 100) => {
  const { data } = await api.get('/history', { params: { limit } });
  return data;
};

export const downloadFile = (path) => {
  window.open(`${API_BASE_URL}${path}`, '_blank', 'noopener,noreferrer');
};

export default api;
