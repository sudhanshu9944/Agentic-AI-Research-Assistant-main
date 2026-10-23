let apiBase = import.meta.env.VITE_API_BASE_URL || '';
if (apiBase && !apiBase.startsWith('http://') && !apiBase.startsWith('https://')) {
  apiBase = apiBase.startsWith('/') ? apiBase : 'https://' + apiBase;
}
const API_BASE_URL = (apiBase || '/api').replace(/\/+$/, '');

async function requestAPI(url, options = {}, timeout = 300000) {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), timeout);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error(
        'The server took too long to respond. Try again or check the server connection.',
      );
    }
    throw error;
  } finally {
    window.clearTimeout(timer);
  }
}

/**
 * Handle fetch response and parse as JSON, throwing standard errors for status codes.
 */
async function handleResponse(response) {
  if (!response.ok) {
    let errorMessage = `Request failed with status ${response.status}`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch (_) {
      // Ignore JSON parse errors for non-JSON error pages
    }
    throw new Error(errorMessage);
  }
  return response.json();
}

export const api = {
  /**
   * Check if backend is alive
   */
  async healthCheck() {
    try {
      const response = await requestAPI(`${API_BASE_URL}/health`, {}, 45000);
      return await handleResponse(response);
    } catch (error) {
      console.error('Backend health check failed:', error);
      return { status: 'offline', error: error.message };
    }
  },

  /**
   * Run the AI research pipeline on a topic
   */
  async recommendTopics(query, model, temperature = 0.3) {
    const response = await requestAPI(`${API_BASE_URL}/recommendations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, model, temperature }),
    });
    return handleResponse(response);
  },

  async runResearch(query, model = null, temperature = 0.3, selectedTopics, excludedTopics = []) {
    const payload = {
      query,
      temperature,
      selected_topics: selectedTopics,
      excluded_topics: excludedTopics,
    };
    if (model) {
      payload.model = model;
    }

    const response = await requestAPI(`${API_BASE_URL}/research`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    return await handleResponse(response);
  },

  /**
   * Get past research sessions
   */
  async getHistory() {
    const response = await requestAPI(`${API_BASE_URL}/history`, {}, 45000);
    return await handleResponse(response);
  },

  /**
   * Get a specific report
   */
  async getReport(sessionId) {
    const response = await requestAPI(
      `${API_BASE_URL}/report/${encodeURIComponent(sessionId)}`,
      {},
      45000,
    );
    return await handleResponse(response);
  },

  /**
   * Export the report as PDF (returns a Blob)
   */
  async exportPDF(sessionId) {
    const response = await requestAPI(`${API_BASE_URL}/export/pdf`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ session_id: sessionId }),
    });

    if (!response.ok) {
      let errorMessage = 'Failed to generate PDF';
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorMessage;
      } catch (_) {
        /* Keep the default message for non-JSON server errors. */
      }
      throw new Error(errorMessage);
    }

    return await response.blob();
  },

  /**
   * Export the report as Markdown (returns text)
   */
  async exportMarkdown(sessionId) {
    const response = await requestAPI(`${API_BASE_URL}/export/markdown`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ session_id: sessionId }),
    });

    if (!response.ok) {
      let errorMessage = 'Failed to generate Markdown';
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorMessage;
      } catch (_) {
        /* Keep the default message for non-JSON server errors. */
      }
      throw new Error(errorMessage);
    }

    return await response.text();
  },
};
