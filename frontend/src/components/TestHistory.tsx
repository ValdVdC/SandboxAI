import React, { useEffect, useState } from 'react';
import apiClient from '../services/api';
import { TestResult } from '../types';
import Loading from './Loading';
import '../styles/TestHistory.css';

interface TestHistoryProps {
  promptId: string;
  versionNumber: number;
  onViewBatch?: (testIds: string[]) => void;
}

interface HistoryItem {
  type: 'single' | 'batch';
  batch_id?: string;
  data: TestResult[];
  created_at: string;
}

const TestHistory: React.FC<TestHistoryProps> = ({ promptId, versionNumber, onViewBatch }) => {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTest, setSelectedTest] = useState<TestResult | null>(null);
  const [exporting, setExporting] = useState(false);

  const handleExport = async () => {
    try {
      setExporting(true);
      await apiClient.exportTests(promptId, versionNumber);
    } catch (err) {
      console.error('Export failed', err);
    } finally {
      setExporting(false);
    }
  };

  useEffect(() => {
    const fetchTests = async () => {
      try {
        setLoading(true);
        const tests = await apiClient.getPromptTests(promptId, versionNumber);
        
        const groups: Record<string, TestResult[]> = {};
        const singles: TestResult[] = [];
        
        tests.forEach(t => {
          if (t.batch_id) {
            if (!groups[t.batch_id]) groups[t.batch_id] = [];
            groups[t.batch_id].push(t);
          } else {
            singles.push(t);
          }
        });

        const historyItems: HistoryItem[] = [
          ...Object.entries(groups).map(([bid, tests]) => ({
            type: 'batch' as const,
            batch_id: bid,
            data: tests,
            created_at: tests[0].created_at || ''
          })),
          ...singles.map(t => ({
            type: 'single' as const,
            data: [t],
            created_at: t.created_at || ''
          }))
        ];

        // Sort by date with safety fallback
        historyItems.sort((a, b) => {
          const dateA = new Date(a.created_at).getTime() || 0;
          const dateB = new Date(b.created_at).getTime() || 0;
          return dateB - dateA;
        });

        setItems(historyItems);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch tests');
      } finally {
        setLoading(false);
      }
    };

    if (promptId && versionNumber) {
      fetchTests();
    }
  }, [promptId, versionNumber]);

  if (loading) return <Loading message="Carregando histórico..." />;
  if (error) return <div className="error-message">{error}</div>;
  if (items.length === 0) return <p className="no-tests">Nenhum teste executado.</p>;

  return (
    <div className="test-history">
      <h3>Histórico de Testes</h3>

      {selectedTest ? (
        <div className="test-detail-view">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-lg)' }}>
            <button className="btn btn-secondary back-btn" style={{ marginBottom: 0 }} onClick={() => setSelectedTest(null)}>
              ← Voltar
            </button>
            <button 
              className="btn btn-primary btn-small" 
              onClick={handleExport}
              disabled={exporting}
            >
              {exporting ? 'Exportando...' : 'Exportar Versão'}
            </button>
          </div>
          <div className="test-detail">
            <h4>Detalhes do Teste</h4>
            <div className="detail-section">
              <label>Entrada</label>
              <pre className="code-block">{selectedTest.input}</pre>
            </div>
            <div className="detail-section">
              <label>Saída</label>
              <pre className="code-block">{selectedTest.output || 'Nenhuma saída'}</pre>
            </div>
            <div className="metrics-grid">
              <div className="metric">
                <label>Latência</label>
                <span>{selectedTest.latency_ms}ms</span>
              </div>
              <div className="metric">
                <label>Status</label>
                <span className={`status-badge status-${selectedTest.status}`}>{selectedTest.status}</span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="test-list">
          {items.map((item, idx) => {
            if (item.type === 'batch') {
              const successCount = item.data.filter(t => t.status === 'completed').length;
              const previewInputs = item.data.slice(0, 3); // Preview das 3 primeiras entradas
              
              return (
                <div key={idx} className="test-item batch-item" onClick={() => onViewBatch?.(item.data.map(t => t.id))}>
                  <div className="item-content-top">
                    <div className="test-header">
                      <span className="batch-badge">📦 LOTE ({item.data.length} testes)</span>
                      <span className="test-date">{new Date(item.created_at).toLocaleString('pt-BR')}</span>
                    </div>
                    
                    <div className="batch-preview-list">
                      {previewInputs.map((t, i) => (
                        <div key={i} className="batch-preview-item">
                          {t.input.substring(0, 80)}{t.input.length > 80 ? '...' : ''}
                        </div>
                      ))}
                      {item.data.length > 3 && <div className="batch-preview-item text-muted">... e mais {item.data.length - 3} testes</div>}
                    </div>
                  </div>

                  <div className="batch-summary">
                    <span className="stats">
                      {successCount} sucessos, {item.data.length - successCount} outros.
                    </span>
                    <button className="btn btn-secondary btn-small">
                      Ver detalhes do lote →
                    </button>
                  </div>
                </div>
              );
            } else {
              const test = item.data[0];
              return (
                <div key={idx} className={`test-item status-${test.status}`} onClick={() => setSelectedTest(test)}>
                  <div className="item-content-top">
                    <div className="test-header">
                      <span className={`status-badge status-${test.status}`}>{test.status}</span>
                      <span className="test-date">{new Date(test.created_at || '').toLocaleString('pt-BR')}</span>
                    </div>
                    <div className="test-preview" style={{marginTop: 'var(--spacing-sm)'}}>
                      <p className="input-preview">
                        <strong>Entrada:</strong> {test.input.substring(0, 120)}{test.input.length > 120 ? '...' : ''}
                      </p>
                    </div>
                  </div>
                  
                  <div className="batch-summary">
                    <span className="stats text-muted">Teste Individual</span>
                    <button className="btn btn-secondary btn-small">
                      Abrir detalhes →
                    </button>
                  </div>
                </div>
              );
            }
          })}
        </div>
      )}
    </div>
  );
};

export default TestHistory;
