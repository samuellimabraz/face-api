import axios from 'axios';
import { APIKeyRequest, APIKeyResponse, OrganizationRequest, RegisterRequest, RecognizeRequest, RecognitionResult } from '../types/api';

const API_URL = '/api';

const axiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for better error handling
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    throw error;
  }
);

export const api = {
  createOrganization: async (data: OrganizationRequest) => {
    const response = await axiosInstance.post('/orgs', data);
    return response.data;
  },

  createApiKey: async (organization: string, data: APIKeyRequest) => {
    const response = await axiosInstance.post<APIKeyResponse>(`/orgs/${organization}/api-key`, data);
    return response.data;
  },

  revokeApiKey: async (organization: string, apiKey: string, data: { api_auth: APIKeyRequest }) => {
    const response = await axiosInstance.delete(`/orgs/${organization}/api-key`, {
      headers: { Authorization: `Bearer ${apiKey}` },
      data,
    });
    return response.data;
  },

  registerPerson: async (organization: string, apiKey: string, data: RegisterRequest) => {
    const response = await axiosInstance.post(`/register/${organization}`, data, {
      headers: { Authorization: `Bearer ${apiKey}` },
    });
    return response.data;
  },

  recognizePerson: async (organization: string, apiKey: string, data: RecognizeRequest) => {
    const response = await axiosInstance.post<RecognitionResult>(`/recognize/${organization}`, data, {
      headers: { Authorization: `Bearer ${apiKey}` },
    });
    return response.data;
  },
};