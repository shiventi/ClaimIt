/**
 * Frontend Configuration
 * Reads from enviroment variables set in root .env file
 */

// API Base URL (without /api suffix)
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Full API URL
export const API_URL = `${API_BASE_URL}/api`;

const config = {
  API_BASE_URL,
  API_URL,
};

export default config;
