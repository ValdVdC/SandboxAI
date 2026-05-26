import { useCallback, useEffect, useState } from 'react';
import apiClient from '../services/api';
import { Prompt, TestExecution } from '../types';

export function useApiData<T>(fetchFn: () => Promise<T>, dependencies: any[] = []) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await fetchFn();
      setData(result);
      return result;
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to fetch data';
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, dependencies);

  useEffect(() => {
    execute().catch(() => {});
  }, [execute]);

  return { data, loading, error, execute };
}

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
  const [test, setTest] = useState<TestExecution | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTest = useCallback(async () => {
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
  }, [testId]);

  useEffect(() => {
    if (testId) {
      fetchTest();
    }
  }, [testId, fetchTest]);

  return { test, loading, error, refetch: () => fetchTest() };
};
