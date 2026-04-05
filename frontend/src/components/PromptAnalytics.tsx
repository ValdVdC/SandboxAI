import React, { useEffect, useState } from 'react';
import apiClient from '../services/api';
import Loading from './Loading';
import '../styles/PromptAnalytics.css';

interface EvolutionData {
  version: number;
  avg_latency: number;
  avg_cost: number;
  avg_tokens: number;
  test_count: number;
  success_count: number;
  fail_count: number;
}

interface PromptAnalyticsProps {
  promptId: string;
  selectedVersionNumber?: number;
  onBack: () => void;
}

const PromptAnalytics: React.FC<PromptAnalyticsProps> = ({ promptId, selectedVersionNumber, onBack }) => {
  const [data, setData] = useState<EvolutionData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEvolution = async () => {
      try {
        setLoading(true);
        const evolution = await apiClient.getPromptEvolution(promptId);
        setData(evolution);
      } catch (err) {
        console.error('Failed to fetch prompt evolution', err);
      } finally {
        setLoading(false);
      }
    };
    fetchEvolution();
  }, [promptId]);

  if (loading) return <Loading message="Calculando métricas contextuais..." />;

  // Versions with successful data for record calculations
  const successfulVersions = data.filter(d => d.success_count > 0);
  
  // Current active data point (either selected or the latest)
  const activeVersionNumber = selectedVersionNumber || (data.length > 0 ? data[data.length - 1].version : 0);
  const activeData = data.find(v => v.version === activeVersionNumber) || (data.length > 0 ? data[data.length - 1] : null);
  
  // Helper to check if active version has valid data
  const activeHasData = activeData && activeData.test_count > 0;
  const activeHasSuccess = activeData && activeData.success_count > 0;

  // Find overall insights (ONLY from successful tests)
  const bestLatency = successfulVersions.length > 0 ? [...successfulVersions].sort((a, b) => a.avg_latency - b.avg_latency)[0] : null;
  const bestCost = successfulVersions.length > 0 ? [...successfulVersions].sort((a, b) => a.avg_cost - b.avg_cost)[0] : null;

  const renderBarChart = (title: string, subtitle: string, field: keyof EvolutionData, unit: string, color: string, lowerIsBetter = true) => {
    // Only use values from versions that have data for the scale
    const chartValues = data.filter(v => v.test_count > 0).map(v => v[field] as number);
    const max = chartValues.length > 0 ? Math.max(...chartValues, 0.0001) : 1;

    // Trend calculation: Compare active with nearest PREVIOUS version that HAS data
    let trendNode = null;
    const activeIdx = data.findIndex(v => v.version === activeVersionNumber);
    
    // Search backwards for the first version with data before activeIdx
    let prevData = null;
    for (let j = activeIdx - 1; j >= 0; j--) {
      if (data[j].test_count > 0) {
        prevData = data[j];
        break;
      }
    }

    if (activeHasData && prevData) {
      const currentVal = activeData[field] as number;
      const previousVal = prevData[field] as number;
      
      if (previousVal > 0) {
        const diffPercent = ((currentVal - previousVal) / previousVal) * 100;
        const isBetter = lowerIsBetter ? diffPercent < 0 : diffPercent > 0;
        const isWorse = lowerIsBetter ? diffPercent > 0 : diffPercent < 0;
        
        trendNode = (
          <span className={`trend-tag ${isBetter ? 'better' : isWorse ? 'worse' : 'neutral'}`}>
            {diffPercent > 0 ? '+' : ''}{diffPercent.toFixed(1)}% vs v{prevData.version}
          </span>
        );
      }
    }

    return (
      <div className="chart-card">
        <div className="chart-card-header">
          <div className="chart-title">
            <h4>{title}</h4>
            <span>{subtitle}</span>
          </div>
          {trendNode}
        </div>
        <div className="chart-container">
          {data.map((v, i) => {
            const hasTests = v.test_count > 0;
            const isSelected = v.version === activeVersionNumber;
            const val = v[field] as number;
            const height = hasTests ? (val / max) * 100 : 0;
            
            return (
              <div key={i} className="bar-wrapper">
                <div className="bar-value-popup">{hasTests ? val.toFixed(unit === '$' ? 4 : 1) + unit : 'N/A'}</div>
                <div 
                  className={`bar ${isSelected ? 'selected' : 'not-selected'} ${!hasTests ? 'no-data' : ''}`}
                  style={{ 
                    height: `${Math.max(height, 4)}%`,
                    backgroundColor: isSelected ? color : 'var(--color-bg-tertiary)'
                  }}
                ></div>
                <span className="bar-label">v{v.version}</span>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="prompt-analytics">
      <div className="analytics-header" style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-lg)', marginBottom: 'var(--spacing-md)' }}>
        <button className="btn btn-secondary back-btn" style={{ marginBottom: 0 }} onClick={onBack}>
          ← Voltar
        </button>
        <h2 style={{ margin: 0 }}>Analytics: v{activeVersionNumber}</h2>
      </div>

      <div className="analytics-summary-cards">
        <div className="insight-card">
          <span className="label">Latência v{activeVersionNumber}</span>
          <span className="value">{activeHasSuccess ? `${activeData.avg_latency.toFixed(0)}ms` : '---'}</span>
          <span className="sub">
            {activeHasSuccess && bestLatency && activeData.avg_latency <= bestLatency.avg_latency 
              ? 'Recorde de velocidade!' 
              : bestLatency ? `Melhor global: ${bestLatency.avg_latency.toFixed(0)}ms` : 'Sem recordes ainda'}
          </span>
        </div>
        <div className="insight-card">
          <span className="label">Custo v{activeVersionNumber}</span>
          <span className="value">{activeHasSuccess ? `$${activeData.avg_cost.toFixed(4)}` : '---'}</span>
          <span className="sub">
            {activeHasSuccess && bestCost && activeData.avg_cost <= bestCost.avg_cost 
              ? 'Versão mais econômica' 
              : bestCost ? `Mínimo global: $${bestCost.avg_cost.toFixed(4)}` : 'Sem recordes ainda'}
          </span>
        </div>
        <div className="insight-card">
          <span className="label">Taxa de Sucesso</span>
          <span className="value">{activeHasData ? `${((activeData.success_count / activeData.test_count) * 100).toFixed(1)}%` : '---'}</span>
          <span className="sub">
            {activeHasData ? `${activeData.success_count} sucessos em ${activeData.test_count} testes` : 'Aguardando testes'}
          </span>
        </div>
        <div className="insight-card">
          <span className="label">Amostragem</span>
          <span className="value">{data.reduce((acc, curr) => acc + curr.test_count, 0)} testes</span>
          <span className="sub">Total acumulado do prompt</span>
        </div>
      </div>

      <div className="analytics-grid">
        {renderBarChart('Velocidade', 'Comparação de latência (ms)', 'avg_latency', 'ms', 'var(--color-primary)')}
        {renderBarChart('Custos', 'Comparação de custo ($)', 'avg_cost', '$', 'var(--color-success)')}
        
        {/* Reliability Chart with fixed red box bug */}
        <div className="chart-card">
          <div className="chart-card-header">
            <div className="chart-title">
              <h4>Confiabilidade</h4>
              <span>Sucesso vs Falha (%)</span>
            </div>
          </div>
          <div className="chart-container">
            {data.map((v, i) => {
              const hasData = v.test_count > 0;
              const isSelected = v.version === activeVersionNumber;
              const successRate = hasData ? (v.success_count / v.test_count) * 100 : 0;
              const failRate = hasData ? (v.fail_count / v.test_count) * 100 : 0;
              
              return (
                <div key={i} className="bar-wrapper">
                  <div className="bar-value-popup">{hasData ? successRate.toFixed(0) + '%' : 'N/A'}</div>
                  <div 
                    className={`bar ${isSelected ? 'selected' : 'not-selected'} ${!hasData ? 'no-data' : ''}`}
                    style={{ 
                      height: `${Math.max(successRate + failRate, 4)}%`,
                      backgroundColor: 'var(--color-success)',
                    }}
                  >
                    {hasData && v.fail_count > 0 && (
                      <div className="error-fill" style={{ height: `${(v.fail_count / (v.success_count + v.fail_count)) * 100}%` }} />
                    )}
                  </div>
                  <span className="bar-label">v{v.version}</span>
                </div>
              );
            })}
          </div>
        </div>

        {renderBarChart('Volume', 'Testes realizados', 'test_count', '', 'var(--color-text-muted)', false)}
      </div>

      <div className="data-table-section">
        <h4>Histórico Completo de Métricas</h4>
        <table className="analytics-table">
          <thead>
            <tr>
              <th>Versão</th>
              <th>Status (S/F)</th>
              <th>Total Testes</th>
              <th>Latência Média</th>
              <th>Custo Médio</th>
              <th>Foco</th>
            </tr>
          </thead>
          <tbody>
            {[...data].reverse().map((v) => (
              <tr key={v.version} style={v.version === activeVersionNumber ? {backgroundColor: 'rgba(88, 166, 255, 0.05)'} : {}}>
                <td><strong>v{v.version}</strong></td>
                <td>
                  <div className="status-cell">
                    <span className="dot success"></span> {v.success_count}
                    <span className="dot fail"></span> {v.fail_count}
                  </div>
                </td>
                <td>{v.test_count}</td>
                <td>{v.avg_latency > 0 ? `${v.avg_latency.toFixed(0)}ms` : '---'}</td>
                <td>{v.avg_cost > 0 ? `$${v.avg_cost.toFixed(4)}` : '---'}</td>
                <td>{v.version === activeVersionNumber ? '🎯 Ativa' : ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PromptAnalytics;
