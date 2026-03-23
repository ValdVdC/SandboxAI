import React, { useEffect, useState } from 'react';
import apiClient from '../services/api';
import { TestResult } from '../types';
import Loading from './Loading';
import '../styles/TestResults.css';

interface TestResultsProps {
  testId: string;
  autoRefresh?: boolean;
  onBack?: () => void;
}

const TestResults: React.FC<TestResultsProps> = ({ testId, autoRefresh = true, onBack }) => {
  const [result, setResult] = useState<TestResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const resultData = await apiClient.getTestExecution(testId);
        setResult(resultData as TestResult);
        console.log('Test result fetched:', resultData);
      } catch (err) {
        console.error('Error fetching test result:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch test result');
      } finally {
        setLoading(false);
      }
    };

    fetchResult();

    // Poll while test is queued or running
    if (autoRefresh && result && (result.status === 'queued' || result.status === 'pending' || result.status === 'running')) {
      const interval = setInterval(fetchResult, 1000);
      return () => clearInterval(interval);
    }
  }, [testId, result?.status, autoRefresh]);

  if (loading) return <Loading message="Carregando resultados do teste..." />;

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (!result) {
    return <div className="error-message">Teste não encontrado</div>;
  }

  return (
    <div className="test-results">
      <div className="test-results-header">
        {onBack && (
          <button className="btn btn-secondary back-btn" onClick={onBack}>
            ← Voltar
          </button>
        )}
        <h2>Resultados do Teste</h2>
      </div>

      <div className="test-status">
        <span className={`status-badge status-${result.status}`}>{result.status}</span>
        {result.created_at && (
          <span className="test-date">{new Date(result.created_at).toLocaleString('pt-BR')}</span>
        )}
      </div>

      {result.status === 'queued' && (
        <div className="running-indicator">
          <span className="spinner"></span>
          Teste em execução...
        </div>
      )}

      <div className="test-input-output">
        <div className="section">
          <h3>Entrada</h3>
          <pre className="code-block">{result.input || 'Sem entrada'}</pre>
        </div>

        {result.expected && (
          <div className="section">
            <h3>Saída Esperada</h3>
            <pre className="code-block">{result.expected}</pre>
          </div>
        )}

        {result.status === 'completed' && (
          <div className="section">
            <h3>Saída Real</h3>
            <pre className="code-block">{result.output || 'Sem saída'}</pre>
          </div>
        )}

        {result.status === 'failed' && (
          <div className="section error">
            <h3>Erro</h3>
            <pre className="code-block">{result.error_message || 'Erro desconhecido'}</pre>
          </div>
        )}
      </div>

      {result.status === 'completed' && (
        <div className="metrics-grid">
          <div className="metric">
            <label>Latência</label>
            <span className="value">{result.latency_ms || 0}ms</span>
          </div>
          <div className="metric">
            <label>Tokens</label>
            <span className="value">{result.tokens_used || 0}</span>
          </div>
          <div className="metric">
            <label>Custo USD</label>
            <span className="value">
              ${typeof result.cost_usd === 'number' ? result.cost_usd.toFixed(6) : '0.000000'}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default TestResults;
