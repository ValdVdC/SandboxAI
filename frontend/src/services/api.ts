/// <reference types="vite/client" />
import axios, { AxiosInstance } from 'axios';
import {
  AuthResponse,
  CreatePromptRequest,
  LoginRequest,
  Metrics,
  Prompt,
  PromptMetrics,
  PromptVersion,
  VersionListResponse,
  RegisterRequest,
  TestExecution,
  TestResult,
  UpdatePromptRequest,
  User,
  PaginatedResponse,
} from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add token to requests
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/auth/login', data);
    return response.data;
  }

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/auth/register', data);
    return response.data;
  }

  async getProfile(): Promise<User> {
    const response = await this.client.get<User>('/auth/profile');
    return response.data;
  }

  // Prompts
  async createPrompt(data: CreatePromptRequest): Promise<Prompt> {
    const response = await this.client.post<Prompt>('/prompts', data);
    return response.data;
  }

  async listPrompts(search?: string, skip: number = 0, limit: number = 20): Promise<PaginatedResponse<Prompt>> {
    const response = await this.client.get<PaginatedResponse<Prompt>>('/prompts', {
      params: { search, skip, limit },
    });
    return response.data;
  }

  async getPrompt(id: string): Promise<Prompt> {
    const response = await this.client.get<Prompt>(`/prompts/${id}`);
    return response.data;
  }

  async updatePrompt(id: string, data: UpdatePromptRequest): Promise<Prompt> {
    const response = await this.client.put<Prompt>(`/prompts/${id}`, data);
    return response.data;
  }

  async deletePrompt(id: string): Promise<void> {
    await this.client.delete(`/prompts/${id}`);
  }

  async duplicatePrompt(id: string, name: string): Promise<Prompt> {
    const response = await this.client.post<Prompt>(`/prompts/${id}/duplicate`, { name });
    return response.data;
  }

  // Versions
  async getPromptVersions(promptId: string): Promise<VersionListResponse> {
    const response = await this.client.get<VersionListResponse>(`/prompts/${promptId}/versions`);
    return response.data;
  }

  async createVersion(
    promptId: string,
    data: { content: string; provider: string; model: string }
  ): Promise<PromptVersion> {
    const response = await this.client.post<PromptVersion>(
      `/prompts/${promptId}/versions`,
      data
    );
    return response.data;
  }

  async getVersion(promptId: string, versionId: string): Promise<PromptVersion> {
    const response = await this.client.get<PromptVersion>(
      `/prompts/${promptId}/versions/${versionId}`
    );
    return response.data;
  }

  async restoreVersion(promptId: string, versionId: string): Promise<Prompt> {
    const response = await this.client.post<Prompt>(
      `/prompts/${promptId}/versions/${versionId}/restore`
    );
    return response.data;
  }

  // Tests
  async executeTest(
    promptId: string,
    versionNum: number,
    data: { input: string; expected?: string }
  ): Promise<TestExecution> {
    const response = await this.client.post<TestExecution>(
      `/prompts/${promptId}/versions/${versionNum}/tests`,
      data
    );
    return response.data;
  }

  async getTestExecution(id: string): Promise<TestExecution> {
    const response = await this.client.get<TestExecution>(`/prompts/tests/${id}`);
    return response.data;
  }

  async getPromptTests(promptId: string, versionNumber: number): Promise<TestResult[]> {
    const response = await this.client.get<any>(
      `/prompts/${promptId}/versions/${versionNumber}/tests`
    );
    // Response is TestListResponse with items array
    return response.data.items || [];
  }

  async getTestResult(testId: string): Promise<TestResult> {
    const response = await this.client.get<TestResult>(`/tests/${testId}/result`);
    return response.data;
  }

  // Metrics
  async getMetrics(): Promise<Metrics> {
    const response = await this.client.get<Metrics>('/metrics');
    return response.data;
  }

  async getPromptMetrics(promptId: string): Promise<PromptMetrics> {
    const response = await this.client.get<PromptMetrics>(`/prompts/${promptId}/metrics`);
    return response.data;
  }

  // Health
  async health(): Promise<{ status: string }> {
    const response = await this.client.get<{ status: string }>('/health');
    return response.data;
  }
}

export default new ApiClient();
