import axios from 'axios';
import { notification } from 'antd';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000, // 30 seconds timeout for file uploads
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - can add auth tokens here if needed
api.interceptors.request.use(
  (config) => {
    // If you implement API key authentication later, add it here:
    // config.headers['X-API-Key'] = 'your-api-key';
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors globally
api.interceptors.response.use(
  (response) => {
    // Success response - return data directly
    return response;
  },
  (error) => {
    // Log full error for debugging
    console.error('🚨 API Error intercepted:', error);
    console.error('Error response data:', error.response?.data);
    console.error('Error response status:', error.response?.status);
    
    // Handle different error scenarios
    let errorMessage = 'An unexpected error occurred';
    let errorDescription = '';

    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const data = error.response.data;

      switch (status) {
        case 400:
          errorMessage = 'Bad Request';
          errorDescription = data.detail || 'Invalid request parameters';
          // Log details array if present
          if (data.details) {
            console.error('Validation details:', JSON.stringify(data.details, null, 2));
            errorDescription += '\n' + data.details.map(d => `${d.field}: ${d.message}`).join('\n');
          }
          break;
        case 404:
          errorMessage = 'Not Found';
          errorDescription = data.detail || 'Resource not found';
          break;
        case 422:
          errorMessage = 'Validation Error';
          // Handle Pydantic validation errors
          if (data.detail && Array.isArray(data.detail)) {
            console.error('Pydantic validation errors:', JSON.stringify(data.detail, null, 2));
            errorDescription = data.detail.map(err => 
              `${err.loc.join('.')}: ${err.msg}`
            ).join(', ');
          } else if (data.details && Array.isArray(data.details)) {
            console.error('Custom validation details:', JSON.stringify(data.details, null, 2));
            errorDescription = data.details.map(d => `${d.field}: ${d.message}`).join(', ');
          } else {
            errorDescription = data.detail || data.message || 'Invalid input data';
          }
          break;
        case 500:
          errorMessage = 'Server Error';
          errorDescription = data.detail || 'Internal server error occurred';
          break;
        case 502:
          errorMessage = 'OpenAI Service Error';
          errorDescription = data.detail || 'AI service temporarily unavailable';
          break;
        case 503:
          errorMessage = 'Database Error';
          errorDescription = data.detail || 'Database service unavailable';
          break;
        default:
          errorMessage = `Error ${status}`;
          errorDescription = data.detail || 'Something went wrong';
      }
    } else if (error.request) {
      // Request made but no response received
      errorMessage = 'Network Error';
      errorDescription = 'Cannot connect to server. Please check if the backend is running.';
    } else {
      // Something else happened
      errorMessage = 'Request Error';
      errorDescription = error.message;
    }

    // Show error notification
    notification.error({
      message: errorMessage,
      description: errorDescription,
      duration: 5,
      placement: 'topRight',
    });

    return Promise.reject(error);
  }
);

// API Functions

/**
 * Upload a resume file (PDF or TXT)
 * @param {FormData} formData - FormData containing the resume file
 * @returns {Promise} Response with resume_id and parsed data
 */
export const uploadResume = async (formData) => {
  try {
    console.log('📤 uploadResume called');
    console.log('FormData entries:');
    for (let pair of formData.entries()) {
      console.log(`  ${pair[0]}:`, pair[1]);
    }
    
    const response = await api.post('/upload_resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    console.log('✅ Resume upload response:', response.data);
    
    notification.success({
      message: 'Resume Uploaded',
      description: 'Resume has been successfully parsed and stored.',
      duration: 3,
      placement: 'topRight',
    });
    
    return response.data;
  } catch (error) {
    console.error('❌ uploadResume error:', error);
    console.error('Error response:', error.response?.data);
    throw error;
  }
};

/**
 * Upload a job description as text
 * @param {string} text - Job description text (50-50,000 characters)
 * @returns {Promise} Response with jd_id and parsed requirements
 */
export const uploadJD = async (text) => {
  try {
    console.log('🚀 uploadJD called with text length:', text.length);
    console.log('📝 Text preview:', text.substring(0, 100));
    
    // Backend expects FormData with jd_text field, not JSON
    const formData = new FormData();
    formData.append('jd_text', text);
    
    console.log('📦 FormData created, sending to /upload_jd...');
    
    const response = await api.post('/upload_jd', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    console.log('✅ Response received:', response.data);
    
    notification.success({
      message: 'Job Description Uploaded',
      description: 'JD has been successfully parsed and stored.',
      duration: 3,
      placement: 'topRight',
    });
    
    return response.data;
  } catch (error) {
    console.error('❌ uploadJD error:', error);
    console.error('Error response:', error.response?.data);
    throw error;
  }
};

/**
 * Match resumes against a job description
 * @param {string} jdId - Job description ID
 * @param {Array<string>} resumeIds - Array of resume IDs to match (1-50 resumes)
 * @returns {Promise} Response with match results
 */
export const matchResumes = async (jdId, resumeIds) => {
  try {
    console.log('🎯 matchResumes called');
    console.log('JD ID:', jdId);
    console.log('Resume IDs:', resumeIds);
    console.log('Number of resumes:', resumeIds.length);
    
    // Backend expects 'candidate_ids' not 'resume_ids'
    const response = await api.post(`/match/${jdId}`, { candidate_ids: resumeIds });
    
    console.log('✅ Match response:', response.data);
    
    notification.success({
      message: 'Matching Complete',
      description: `Successfully matched ${resumeIds.length} resume(s) against the job description.`,
      duration: 3,
      placement: 'topRight',
    });
    
    return response.data;
  } catch (error) {
    console.error('❌ matchResumes error:', error);
    console.error('Error response:', error.response?.data);
    throw error;
  }
};

/**
 * Get shortlisted candidates with pagination and filters
 * @param {string} jdId - Job description ID
 * @param {number} threshold - Minimum overall score (0-10)
 * @param {number} page - Page number (default: 1)
 * @param {number} pageSize - Items per page (default: 10, max: 100)
 * @param {string} sortBy - Sort field (default: 'overall_score')
 * @param {string} sortOrder - Sort order 'asc' or 'desc' (default: 'desc')
 * @returns {Promise} Response with shortlisted candidates and pagination info
 */
export const getShortlist = async (
  jdId, 
  threshold = 0, 
  page = 1, 
  pageSize = 10, 
  sortBy = 'overall_score', 
  sortOrder = 'desc'
) => {
  try {
    const response = await api.get(`/shortlist/${jdId}`, {
      params: {
        threshold,
        page,
        page_size: pageSize,
        sort_by: sortBy,
        sort_order: sortOrder,
      },
    });
    
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Export shortlisted candidates to CSV
 * @param {string} jdId - Job description ID
 * @param {number} threshold - Minimum overall score (optional, default: 0)
 * @returns {Promise} Blob containing CSV file
 */
export const exportCSV = async (jdId, threshold = 0) => {
  try {
    const response = await api.get(`/export/${jdId}/csv`, {
      params: { threshold },
      responseType: 'blob', // Important for file download
    });
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `shortlist_${jdId}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
    notification.success({
      message: 'Export Successful',
      description: 'CSV file has been downloaded.',
      duration: 3,
      placement: 'topRight',
    });
    
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Check candidate for bias in scoring
 * @param {string} candidateId - Candidate/Resume ID
 * @returns {Promise} Response with bias analysis report
 */
export const biasCheck = async (candidateId) => {
  try {
    const response = await api.post(`/bias_check/${candidateId}`);
    
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Get all uploaded job descriptions
 * @returns {Promise} Response with list of JDs
 */
export const getAllJDs = async () => {
  try {
    const response = await api.get('/jds');
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Get all uploaded resumes
 * @returns {Promise} Response with list of resumes
 */
export const getAllResumes = async () => {
  try {
    const response = await api.get('/resumes');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export default api;
