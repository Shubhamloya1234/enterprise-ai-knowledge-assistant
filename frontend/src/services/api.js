import axios from "axios";

const api = axios.create({
    baseURL:
        import.meta.env.VITE_API_BASE_URL ||
        "http://127.0.0.1:8000",

    headers: {
        "Content-Type": "application/json",
    },
});

// Attach JWT to outgoing requests.
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("token");

        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        // Allow Axios to set the multipart boundary for file uploads.
        if (config.data instanceof FormData) {
            delete config.headers["Content-Type"];
        }

        return config;
    },
    (error) => Promise.reject(error)
);

// Handle expired or invalid sessions centrally.
api.interceptors.response.use(
    (response) => response,

    (error) => {
        if (
            error.response?.status === 401 &&
            !error.config?.url?.includes("/auth/login")
        ) {
            window.dispatchEvent(
                new Event("auth:logout")
            );
        }

        return Promise.reject(error);
    }
);

export default api;