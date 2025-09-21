// C.H.R.I.S.T. Project - Main JavaScript

// API Base URL
const API_BASE = '/api/v1';

// Utility functions
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);

    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// API wrapper
class ChristAPI {
    async ingest(data) {
        return axios.post(`${API_BASE}/consciousness/ingest`, data);
    }

    async getEvents(params = {}) {
        return axios.get(`${API_BASE}/consciousness/events`, { params });
    }

    async search(query, k = 10) {
        return axios.post(`${API_BASE}/retrieval/search`, { query, k });
    }

    async ask(question) {
        return axios.post(`${API_BASE}/retrieval/ask`, question, {
            headers: { 'Content-Type': 'text/plain' }
        });
    }

    async chat(message, persona = null) {
        return axios.post(`${API_BASE}/simulation/chat`, { message, persona });
    }

    async getGoals(status = null) {
        return axios.get(`${API_BASE}/teleology/goals`, {
            params: status ? { status } : {}
        });
    }

    async createGoal(goal) {
        return axios.post(`${API_BASE}/teleology/goals`, goal);
    }

    async generateReflection(params = {}) {
        return axios.post(`${API_BASE}/retrieval/reflect`, params);
    }
}

const api = new ChristAPI();

// Global initialization
document.addEventListener('DOMContentLoaded', () => {
    // Check API health
    checkAPIHealth();

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Set active nav link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});

async function checkAPIHealth() {
    try {
        const response = await axios.get('/health');
        console.log('API Health:', response.data);
    } catch (error) {
        console.error('API Health Check Failed:', error);
        showNotification('API connection error. Some features may not work.', 'warning');
    }
}

// Export functions for use in templates
window.api = api;
window.showNotification = showNotification;
window.formatDate = formatDate;
window.formatBytes = formatBytes;