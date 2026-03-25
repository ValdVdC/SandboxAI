import React, { useEffect, useState } from 'react';
import apiClient from '../services/api';
import { TestResult } from '../types';
import Loading from './Loading';
import '../styles/TestHistory.css';

interface TestHistoryProps {
  promptId: string;
  versionNumber: number;
}

const TestHistory: React.FC<TestHistoryProps> = ({ promptId, versionNumber }) => {
  const [tests, setTests] = useState<TestResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTest, setSelectedTest] = useState<TestResult | null>(null);

  useEffect(() => {
    const fetchTests = async () => {
      try {
        setLoading(true);
        console.log('Fetching tests for:', { promptId, versionNumber });
        const tests = await apiClient.getPromptTests(promptId, versionNumber);
        console.log('Tests fetched:', tests);
        const sorted = tests.sort((a, b) => 
          new Date(b.created_at || '').getTime() - new Date(a.created_at || '').getTime()
        );
        setTests(sorted);
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Failed to fetch tests';
        console.error('Error fetching tests:', err);
        setError(errorMsg);
      } finally {
        setLoading(false);
      }
    };

    if (promptId && versionNumber) {
      fetchTests();
    }
  }, [promptId, versionNumber]);

  if (loading) return <Loading message="Carregando histórico de testes..." />;

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (tests.length === 0) {
    return (
      <div className="test-history">
        <h3>Histórico de Testes</h3>
        <p className="no-tests">Nenhum teste executado ainda nesta versão</p>
      </div>
    );
  }

  return (
    <div className="test-history">
      <h3>Histórico de Testes ({tests.length})</h3>

      {selectedTest ? (
        <div className="test-detail-view">
          <button
            className="btn btn-secondary back-btn"
            onClick={() => setSelectedTest(null)}
          >
            ← Voltar
          </button>

          <div className="test-detail">
            <div className="detail-section">
              <h4>Entrada</h4>
              <pre className="code-block">{selectedTest.input || 'Sem entrada'}</pre>
            </div>

            {selectedTest.expected && (
              <div className="detail-section">
                <h4>Esperado</h4>
                <pre className="code-block">{selectedTest.expected}</pre>
              </div>
            )}

            {selectedTest.status === 'completed' && (
              <div className="detail-section">
                <h4>Saída Obtida</h4>
                <pre className="code-block">{selectedTest.output || 'Sem saída'}</pre>
              </div>
            )}

            {selectedTest.status === 'failed' && (
              <div className="detail-section error">
                <h4>Erro</h4>
                <pre className="code-block">{selectedTest.error_message || 'Erro desconhecido'}</pre>
              </div>
            )}

            <div className="metrics-grid">
              <div className="metric">
                <label>Status</label>
                <span className={`value status-${selectedTest.status}`}>{selectedTest.status}</span>
              </div>
              {selectedTest.latency_ms !== undefined && (
                <div className="metric">
                  <label>Latência</label>
                  <span className="value">{selectedTest.latency_ms}ms</span>
                </div>
              )}
              {selectedTest.tokens_used !== undefined && (
                <div className="metric">
                  <label>Tokens</label>
                  <span className="value">{selectedTest.tokens_used}</span>
                </div>
              )}
              {selectedTest.cost_usd !== undefined && (
                <div className="metric">
                  <label>Custo USD</label>
                  <span className="value">${(typeof selectedTest.cost_usd === 'string' ? parseFloat(selectedTest.cost_usd) : selectedTest.cost_usd).toFixed(6)}</span>
                </div>
              )}
            </div>

            <div className="detail-footer">
              <span className="date">
                {selectedTest.created_at && new Date(selectedTest.created_at).toLocaleString('pt-BR')}
              </span>
            </div>
          </div>
        </div>
      ) : (
        <div className="test-list">
          {tests.map((test, idx) => (
            <div
              key={test.id}
              className={`test-item status-${test.status}`}
              onClick={() => setSelectedTest(test)}
            >
              <div className="test-header">
                <span className="test-number">#{tests.length - idx}</span>
                <span className={`status-badge status-${test.status}`}>{test.status}</span>
                <span className="test-date">
                  {test.created_at && new Date(test.created_at).toLocaleString('pt-BR')}
                </span>
              </div>
              <div className="test-preview">
                <p className="input-preview">
                  <strong>Entrada:</strong> {test.input?.substring(0, 100) || 'Sem entrada'}
                  {test.input && test.input.length > 100 ? '...' : ''}
                </p>
              </div>
              {test.status === 'completed' && test.latency_ms !== undefined && (
                <div className="test-metrics">
                  <span className="metric-small">{test.latency_ms}ms</span>
                  {test.tokens_used !== undefined && (
                    <span className="metric-small">{test.tokens_used} tokens</span>
                  )}
                  {test.cost_usd !== undefined && (
                    <span className="metric-small">${(typeof test.cost_usd === 'string' ? parseFloat(test.cost_usd) : test.cost_usd).toFixed(6)}</span>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TestHistory;
