import axios from 'axios';

// Automatically use the current hostname effectively allowing local network access
const hostname = window.location.hostname;
const protocol = window.location.protocol;
const API_URL = import.meta.env.VITE_API_URL || `${protocol}//${hostname}:8000`;

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const analyzeComment = async (text) => {
    try {
        const response = await api.post('/analyze', { text });
        return response.data;
    } catch (error) {
        console.error("API Error:", error);
        throw error;
    }
};

export default api;
