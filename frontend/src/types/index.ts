// User & Auth
export interface User {
  id: string;
  email: string;
  username: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  full_name: string;
  password: string;
}

// Prompts
export interface Prompt {
  id: string;
  user_id: string;
  name: string;
  description: string;
  current_version: number;
  created_at: string;
  updated_at: string;
}

export interface PromptVersion {
  id: string;
  prompt_id: string;
  version: number;
  content: string;
  provider: string;
  model: string;
  change_description?: string;
  created_at: string;
  created_by?: string;
}

export interface VersionListResponse {
  total: number;
  items: PromptVersion[];
}

export interface CreatePromptRequest {
  name: string;
  description?: string;
}

export interface UpdatePromptRequest {
  content: string;
  change_description?: string;
}

// Tests & Execution
export interface TestExecution {
  id: string;
  test_id?: string; // For response from POST /tests with celery_task_id
  celery_task_id?: string; // When queued
  status: 'queued' | 'pending' | 'running' | 'completed' | 'failed';
  message?: string; // For queued response
  created_at?: string;
}

export interface TestResult {
  id: string;
  version_id: string;
  batch_id?: string;
  input: string;
  output?: string;
  expected?: string;
  latency_ms?: number;
  tokens_used?: number;
  cost_usd?: number;
  status: 'queued' | 'pending' | 'running' | 'completed' | 'failed';
  error_message?: string;
  created_at?: string;
}

// Metrics
export interface Metrics {
  total_tests: number;
  total_tokens: number;
  total_cost_usd: number;
  avg_latency_ms: number;
  tests_by_provider: Record<string, number>;
  tests_by_status: Record<string, number>;
}

export interface PromptMetrics {
  prompt_id: string;
  total_executions: number;
  avg_latency_ms: number;
  total_tokens: number;
  total_cost_usd: number;
  success_rate: number;
}

// API Response
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
