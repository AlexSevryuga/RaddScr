import axios from 'axios';
import type {
  User,
  AuthTokens,
  LoginCredentials,
  RegisterData,
  Project,
  ProjectCreate,
  ProjectWithAnalysis,
  Subscription,
  CheckoutSession,
  ValidationTask,
} from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  register: async (data: RegisterData): Promise<User> => {
    const response = await api.post<User>('/auth/register', data);
    return response.data;
  },

  login: async (credentials: LoginCredentials): Promise<AuthTokens> => {
    const response = await api.post<AuthTokens>('/auth/login', credentials);
    localStorage.setItem('access_token', response.data.access_token);
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    window.location.href = '/login';
  },

  getMe: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },
};

// Projects API
export const projectsApi = {
  list: async (): Promise<Project[]> => {
    const response = await api.get<Project[]>('/projects');
    return response.data;
  },

  create: async (data: ProjectCreate): Promise<Project> => {
    const response = await api.post<Project>('/projects', data);
    return response.data;
  },

  get: async (id: number): Promise<ProjectWithAnalysis> => {
    const response = await api.get<ProjectWithAnalysis>(`/projects/${id}`);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/projects/${id}`);
  },

  validate: async (id: number): Promise<ValidationTask> => {
    const response = await api.post<ValidationTask>(`/projects/${id}/validate`);
    return response.data;
  },
};

// Stripe API
export const stripeApi = {
  createCheckoutSession: async (plan: string): Promise<CheckoutSession> => {
    const response = await api.post<CheckoutSession>(
      '/stripe/create-checkout-session',
      { plan }
    );
    return response.data;
  },

  getSubscription: async (): Promise<Subscription> => {
    const response = await api.get<Subscription>('/stripe/subscription');
    return response.data;
  },

  cancelSubscription: async (): Promise<{ status: string }> => {
    const response = await api.post<{ status: string }>(
      '/stripe/cancel-subscription'
    );
    return response.data;
  },
};

export default api;
