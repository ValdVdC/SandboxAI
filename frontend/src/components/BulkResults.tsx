import React, { useEffect, useState } from 'react';
import apiClient from '../services/api';
import { TestResult } from '../types';
import Loading from './Loading';

interface BulkResultsProps {
  promptId: string;
  versionNumber: number;
  testIds: string[];
  onBack: () => void;
}

const BulkResults: React.FC<BulkResultsProps> = ({ promptId, versionNumber, testIds, onBack }) => {
  const [results, setResults] = useState<TestResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [polling, setPolling] = useState(true);
  const [exporting, setExporting] = useState(false);

  const handleExport = async () => {
    if (results.length === 0) return;
    try {
      setExporting(true);
      // We use the batch_id of the first result since they all belong to the same batch
      const batchId = results[0].batch_id;
      await apiClient.exportTests(promptId, versionNumber, batchId);
    } catch (err) {
      console.error('Export failed', err);
      alert('Falha ao exportar CSV. Tente novamente.');
    } finally {
      setExporting(false);
    }
  };

  useEffect(() => {
    let isMounted = true;

    const fetchResults = async () => {
      try {
        const promises = testIds.map(async (id) => {
          const existing = results.find(r => r.id === id);
          if (existing && (existing.status === 'completed' || existing.status === 'failed')) {
            return existing;
          }
          return apiClient.getTestResult(id);
        });

        const data = await Promise.all(promises);
        if (!isMounted) return;
        setResults(data);
        
        const allFinished = data.every(r => r.status === 'completed' || r.status === 'failed');
        if (allFinished) {
          setPolling(false);
        }
      } catch (err) {
        console.error('Failed to fetch bulk results:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchResults();
    
    let interval: number | undefined;
    if (polling) {
      interval = window.setInterval(fetchResults, 3000);
    }
    
    return () => {
      isMounted = false;
      if (interval) clearInterval(interval);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [testIds, polling]); 

  const completedCount = results.filter(r => r.status === 'completed').length;
  const failedCount = results.filter(r => r.status === 'failed').length;
  const pendingCount = results.length - completedCount - failedCount;

  if (loading && results.length === 0) return <Loading message="Iniciando processamento em lote..." />;

  return (
    <div className="bulk-results">
      <div className="bulk-header">
        <div style={{ display: 'flex', gap: 'var(--spacing-md)', alignItems: 'center' }}>
          <button className="btn btn-secondary" onClick={onBack}>← Voltar</button>
          <h2 style={{ margin: 0 }}>Resultados do Lote</h2>
        </div>
        <button 
          className="btn btn-primary" 
          onClick={handleExport}
          disabled={exporting || polling}
          title={polling ? "Aguarde os testes terminarem para exportar" : "Baixar resultados em CSV"}
        >
          {exporting ? 'Exportando...' : 'Exportar CSV'}
        </button>
      </div>

      <div className="bulk-stats-summary">
        <div className="stat-card">
          <span className="stat-label">Total</span>
          <span className="stat-value">{results.length}</span>
        </div>
        <div className="stat-card success">
          <span className="stat-label">Concluídos</span>
          <span className="stat-value">{completedCount}</span>
        </div>
        <div className="stat-card failed">
          <span className="stat-label">Falhas</span>
          <span className="stat-value">{failedCount}</span>
        </div>
        <div className="stat-card pending">
          <span className="stat-label">Processando</span>
          <span className="stat-value">{pendingCount}</span>
        </div>
      </div>

      <div className="results-table-container">
        <table className="results-table">
          <thead>
            <tr>
              <th>Entrada</th>
              <th>Saída</th>
              <th>Métricas</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {results.map(result => (
              <tr key={result.id} className={`status-${result.status}`}>
                <td className="col-input">{result.input}</td>
                <td className="col-output">
                  {result.status === 'completed' ? (
                    <div className="output-text">{result.output}</div>
                  ) : result.status === 'failed' ? (
                    <div className="error-text">{result.error_message}</div>
                  ) : (
                    <div className="loading-dots">Processando...</div>
                  )}
                </td>
                <td className="col-metrics">
                  {result.status === 'completed' && (
                    <div className="metrics-summary">
                      <div>⏱️ {result.latency_ms}ms</div>
                      <div>🪙 {result.tokens_used} tokens</div>
                      <div>💰 ${Number(result.cost_usd || 0).toFixed(4)}</div>
                    </div>
                  )}
                </td>
                <td className="col-status">
                  <span className={`status-badge ${result.status}`}>{result.status}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default BulkResults;
