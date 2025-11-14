import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
  validateStatus: function (status) {
    // Accept 2xx status codes and also 202 (Accepted/Processing)
    return status >= 200 && status < 300;
  }
});

// Issues
export const searchIssues = async (days, label = 'documentation') => {
  const response = await api.get('/issues/search', {
    params: { days, label }
  });
  return response.data;
};

export const analyzeIssue = async (issueNumber) => {
  const response = await api.post('/analyze-issue', {
    issue_number: issueNumber
  });
  return response.data;
};

export const getAnalysis = async (analysisId) => {
  const response = await api.get(`/analysis/${analysisId}`);
  return response.data;
};

export const listAnalyses = async (limit = 50, offset = 0) => {
  const response = await api.get('/issues', {
    params: { limit, offset }
  });
  return response.data;
};

// Review Queue
export const getReviewQueue = async (status = 'needs_review', sortBy = 'date') => {
  const response = await api.get('/review-queue', {
    params: { status, sort_by: sortBy }
  });
  return response.data;
};

// Health check
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;

