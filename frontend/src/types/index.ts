// User types
export interface User {
  id: number;
  email: string;
  full_name?: string;
  subscription_tier: 'free' | 'premium' | 'enterprise';
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name?: string;
}

// Project types
export type ProjectStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface Project {
  id: number;
  name: string;
  description?: string;
  keywords?: string[];
  status: ProjectStatus;
  created_at: string;
  updated_at?: string;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  keywords?: string[];
}

// Analysis types
export interface Analysis {
  id: number;
  project_id: number;
  overall_score?: number;
  verdict?: string;
  key_insights?: string[];
  recommendations?: string[];
  reddit_data?: any;
  twitter_data?: any;
  linkedin_data?: any;
  completed_at?: string;
  created_at: string;
}

export interface ProjectWithAnalysis extends Project {
  analysis?: Analysis;
}

// Subscription types
export type SubscriptionPlan = 'starter' | 'pro' | 'enterprise';
export type SubscriptionStatus = 'active' | 'past_due' | 'cancelled' | 'none';

export interface Subscription {
  id: number;
  user_id: number;
  plan: SubscriptionPlan;
  status: SubscriptionStatus;
  current_period_end?: number;
  validations_used: number;
  validations_limit?: number;
  created_at: string;
}

export interface CheckoutSession {
  checkout_url: string;
}

// API response types
export interface ApiError {
  detail: string;
}

export interface ValidationTask {
  status: string;
  task_id: string;
  project_id: number;
}
