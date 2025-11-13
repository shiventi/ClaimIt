import axios from 'axios';
import { API_URL } from '../config';

const API_BASE_URL = API_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatbotAPI = {
  // Create a new conversation
  createConversation: () => api.post('/chatbot/conversations/'),
  
  // Get a conversation
  getConversation: (id) => api.get(`/chatbot/conversations/${id}/`),
  
  // Send a message
  sendMessage: (conversationId, message) =>
    api.post(`/chatbot/conversations/${conversationId}/send_message/`, { message }),
  
  // Get form data
  getFormData: (conversationId) =>
    api.get(`/chatbot/conversations/${conversationId}/form_data/`),
};

export const formsAPI = {
  // List available forms
  listForms: () => api.get('/forms/list/'),
  
  // Get a specific form
  getForm: (formName) => api.get(`/forms/${formName}/`, { responseType: 'blob' }),
};

export default api;
