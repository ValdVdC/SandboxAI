import { useEffect, useState } from 'react';
import apiClient from '../services/api';
import { Prompt } from '../types';

export const usePrompts = (search?: string) => {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPrompts = async () => {
      try {
        setLoading(true);
        const response = await apiClient.listPrompts(search);
        setPrompts(response.items);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch prompts');
      } finally {
        setLoading(false);
      }
    };

    const timeoutId = setTimeout(fetchPrompts, 300); // Debounce search
    return () => clearTimeout(timeoutId);
  }, [search]);

  return { prompts, loading, error };
};

export const usePromptDetail = (id: string) => {
  const [prompt, setPrompt] = useState<Prompt | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPrompt = async () => {
      try {
        setLoading(true);
        const data = await apiClient.getPrompt(id);
        setPrompt(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch prompt');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchPrompt();
    }
  }, [id]);

  return { prompt, loading, error };
};

export const useTestExecution = (testId: string) => {
  const [test, setTest] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTest = async () => {
      try {
        setLoading(true);
        const data = await apiClient.getTestExecution(testId);
        setTest(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch test');
      } finally {
        setLoading(false);
      }
    };

    if (testId) {
      fetchTest();
    }
  }, [testId]);

  return { test, loading, error, refetch: () => fetchTest() };
};
