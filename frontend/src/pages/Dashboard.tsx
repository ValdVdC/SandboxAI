import React, { useEffect, useState } from 'react';
import Header from '../components/Header';
import Loading from '../components/Loading';
import apiClient from '../services/api';
import { Metrics } from '../types';
import '../styles/Dashboard.css';

const Dashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const data = await apiClient.getMetrics();
        setMetrics(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch metrics');
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    // Refresh metrics every 30 seconds
    const interval = setInterval(fetchMetrics, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <Loading message="Carregando dashboard..." />;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <>
      <Header />
      <div className="dashboard">
        <h1>Dashboard</h1>

        {metrics ? (
          <div className="metrics-container">
            <div className="metrics-grid">
              <div className="metric-card">
                <h3>Total de Testes</h3>
                <div className="metric-value">{metrics.total_tests || 0}</div>
                <div className="metric-subtext">Executados</div>
              </div>

              <div className="metric-card">
                <h3>Custo Total</h3>
                <div className="metric-value">
                  ${typeof metrics.total_cost_usd === 'number' ? metrics.total_cost_usd.toFixed(4) : '0.0000'}
                </div>
                <div className="metric-subtext">USD</div>
              </div>

              <div className="metric-card">
                <h3>Tokens Consumidos</h3>
                <div className="metric-value">{(metrics.total_tokens || 0).toLocaleString()}</div>
                <div className="metric-subtext">Total</div>
              </div>

              <div className="metric-card">
                <h3>Latência Média</h3>
                <div className="metric-value">{Math.round(metrics.avg_latency_ms || 0)}ms</div>
                <div className="metric-subtext">Por teste</div>
              </div>
            </div>

            <div className="charts-section">
              <div className="chart-card">
                <h3>Testes por Provider</h3>
                <div className="provider-stats">
                  {Object.entries(metrics.tests_by_provider || {}).map(([provider, count]) => (
                    <div key={provider} className="stat-row">
                      <span className="provider-name">{provider}</span>
                      <span className="stat-value">{count}</span>
                    </div>
                  ))}
                  {!metrics.tests_by_provider && <p className="no-data">Sem dados</p>}
                </div>
              </div>

              <div className="chart-card">
                <h3>Testes por Status</h3>
                <div className="status-stats">
                  {Object.entries(metrics.tests_by_status || {}).map(([status, count]) => (
                    <div key={status} className={`stat-row status-${status}`}>
                      <span className="status-name">{status}</span>
                      <span className="stat-value">{count}</span>
                    </div>
                  ))}
                  {!metrics.tests_by_status && <p className="no-data">Sem dados</p>}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <p>Nenhum dado de métrica disponível no momento.</p>
        )}
      </div>
    </>
  );
};

export default Dashboard;
