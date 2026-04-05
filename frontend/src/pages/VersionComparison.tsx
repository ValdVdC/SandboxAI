import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Loading from '../components/Loading';
import apiClient from '../services/api';
import { Prompt, PromptVersion, TestResult } from '../types';
import '../styles/VersionComparison.css';

interface DiffLine {
  type: 'added' | 'removed' | 'unchanged';
  content: string;
}

interface VersionStats {
  total_tests: number;
  avg_latency: number;
  avg_tokens: number;
  avg_cost: number;
  success_rate: number;
}

interface MatchedTest {
  input: string;
  v1?: TestResult;
  v2?: TestResult;
}

const VersionComparison: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [prompt, setPrompt] = useState<Prompt | null>(null);
  const [versions, setVersions] = useState<PromptVersion[]>([]);
  const [v1Id, setV1Id] = useState<string>('');
  const [v2Id, setV2Id] = useState<string>('');
  const [v1, setV1] = useState<PromptVersion | null>(null);
  const [v2, setV2] = useState<PromptVersion | null>(null);
  const [stats, setStats] = useState<{ v1: VersionStats; v2: VersionStats } | null>(null);
  const [matchedTests, setMatchedTests] = useState<MatchedTest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!id) return;
      try {
        setLoading(true);
        const [promptData, versionsData] = await Promise.all([
          apiClient.getPrompt(id),
          apiClient.getPromptVersions(id)
        ]);
        
        setPrompt(promptData);
        setVersions(versionsData.items);
        
        if (versionsData.items.length >= 2) {
          // Latest versions are usually at the beginning of the list (sorted desc)
          setV1Id(versionsData.items[1].id);
          setV2Id(versionsData.items[0].id);
        } else if (versionsData.items.length === 1) {
          setV1Id(versionsData.items[0].id);
        }
      } catch (err) {
        setError('Falha ao carregar dados do prompt');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  useEffect(() => {
    const fetchDetails = async () => {
      if (!id || !v1Id || !v2Id) return;
      try {
        // Find version numbers from IDs
        const ver1Num = versions.find(v => v.id === v1Id)?.version;
        const ver2Num = versions.find(v => v.id === v2Id)?.version;

        if (ver1Num === undefined || ver2Num === undefined) return;

        const [v1Data, v2Data, statsData, v1Tests, v2Tests] = await Promise.all([
          apiClient.getVersion(id, v1Id),
          apiClient.getVersion(id, v2Id),
          apiClient.compareVersions(v1Id, v2Id),
          apiClient.getPromptTests(id, ver1Num),
          apiClient.getPromptTests(id, ver2Num)
        ]);

        setV1(v1Data);
        setV2(v2Data);
        setStats(statsData);

        // Logic to match tests by input
        const matchedMap = new Map<string, MatchedTest>();
        
        v1Tests.forEach(t => {
          if (t.status === 'completed') {
            const normalizedInput = t.input.trim();
            matchedMap.set(normalizedInput, { input: t.input, v1: t });
          }
        });

        v2Tests.forEach(t => {
          if (t.status === 'completed') {
            const normalizedInput = t.input.trim();
            const existing = matchedMap.get(normalizedInput);
            if (existing) {
              existing.v2 = t;
            } else {
              matchedMap.set(normalizedInput, { input: t.input, v2: t });
            }
          }
        });

        // Convert map to array and filter to show ONLY those that exist in both versions
        // or prioritize those that exist in both.
        const aligned = Array.from(matchedMap.values())
          .sort((a, b) => {
            // Sort to show matches first
            if (a.v1 && a.v2 && (!b.v1 || !b.v2)) return -1;
            if ((!a.v1 || !a.v2) && b.v1 && b.v2) return 1;
            return 0;
          })
          .slice(0, 10); // Show top 10

        setMatchedTests(aligned);

      } catch (err) {
        console.error('Error fetching details', err);
      }
    };
    fetchDetails();
  }, [id, v1Id, v2Id, versions]);

  const computeDiff = (oldText: string, newText: string): { left: DiffLine[], right: DiffLine[] } => {
    const oldLines = (oldText || '').split('\n');
    const newLines = (newText || '').split('\n');
    const left: DiffLine[] = [];
    const right: DiffLine[] = [];
    const maxLines = Math.max(oldLines.length, newLines.length);
    
    for (let i = 0; i < maxLines; i++) {
      const oldLine = oldLines[i];
      const newLine = newLines[i];
      
      if (oldLine === newLine) {
        left.push({ type: 'unchanged', content: oldLine || '' });
        right.push({ type: 'unchanged', content: newLine || '' });
      } else {
        if (oldLine !== undefined && newLine !== undefined) {
          left.push({ type: 'removed', content: oldLine });
          right.push({ type: 'added', content: newLine });
        } else if (oldLine !== undefined) {
          left.push({ type: 'removed', content: oldLine });
          right.push({ type: 'unchanged', content: '' });
        } else {
          left.push({ type: 'unchanged', content: '' });
          right.push({ type: 'added', content: newLine });
        }
      }
    }
    return { left, right };
  };

  const renderMetric = (label: string, v1Val: number, v2Val: number, unit: string, lowerIsBetter = true) => {
    const diff = v2Val - v1Val;
    const percent = v1Val !== 0 ? (diff / v1Val) * 100 : 0;
    const isBetter = lowerIsBetter ? diff < 0 : diff > 0;
    const isWorse = lowerIsBetter ? diff > 0 : diff < 0;

    return (
      <tr>
        <td>{label}</td>
        <td>{v1Val.toFixed(unit === '$' ? 4 : 2)}{unit === '$' ? '' : unit}</td>
        <td>
          <div className="metric-value-container">
            {v2Val.toFixed(unit === '$' ? 4 : 2)}{unit === '$' ? '' : unit}
            {diff !== 0 && (
              <span className={`metric-change ${isBetter ? 'change-better' : isWorse ? 'change-worse' : ''}`}>
                {diff > 0 ? '+' : ''}{percent.toFixed(1)}%
              </span>
            )}
          </div>
        </td>
      </tr>
    );
  };

  const textDiff = v1 && v2 ? computeDiff(v1.content, v2.content) : null;

  if (loading) return <Loading message="Carregando comparação..." />;

  return (
    <>
      <Header />
      <div className="version-comparison-page page-container">
        <button className="btn btn-secondary back-btn" onClick={() => navigate(`/prompts/${id}`)}>
          ← Voltar para Detalhes
        </button>

        <div className="comparison-header">
          <h1>Análise de Regressão: {prompt?.name}</h1>
        </div>

        <div className="comparison-card">
          <div className="comparison-selectors">
            <div className="form-group selector-group">
              <label>Versão Base (De)</label>
              <select value={v1Id} onChange={(e) => setV1Id(e.target.value)}>
                <option value="">Selecione...</option>
                {versions.map(v => (
                  <option key={v.id} value={v.id}>Versão {v.version}</option>
                ))}
              </select>
            </div>
            <div className="form-group selector-group">
              <label>Versão Comparada (Para)</label>
              <select value={v2Id} onChange={(e) => setV2Id(e.target.value)}>
                <option value="">Selecione...</option>
                {versions.map(v => (
                  <option key={v.id} value={v.id}>Versão {v.version}</option>
                ))}
              </select>
            </div>
          </div>

          {v1 && v2 && (
            <>
              <h3 className="diff-section-title">📊 Desempenho Médio</h3>
              <div className="performance-comparison">
                <table className="perf-table">
                  <thead>
                    <tr>
                      <th>Métrica</th>
                      <th>v{v1.version}</th>
                      <th>v{v2.version}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats ? (
                      <>
                        {renderMetric('Latência Média', stats.v1.avg_latency, stats.v2.avg_latency, 'ms')}
                        {renderMetric('Custo Médio', stats.v1.avg_cost, stats.v2.avg_cost, '$')}
                        {renderMetric('Tokens Médios', stats.v1.avg_tokens, stats.v2.avg_tokens, '')}
                        {renderMetric('Taxa de Sucesso', stats.v1.success_rate, stats.v2.success_rate, '%', false)}
                      </>
                    ) : (
                      <tr><td colSpan={3}>Carregando métricas...</td></tr>
                    )}
                  </tbody>
                </table>
              </div>

              <div className="ab-comparison-section">
                <h3 className="diff-section-title">🚀 Comparação de Respostas (A/B)</h3>
                <p className="section-help">Compara as saídas reais para os mesmos inputs em ambas as versões.</p>
                
                {matchedTests.length > 0 ? (
                  <div className="ab-table-container">
                    <table className="ab-table">
                      <thead>
                        <tr>
                          <th>Input</th>
                          <th>Resposta v{v1.version}</th>
                          <th>Resposta v{v2.version}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {matchedTests.map((pair, idx) => (
                          <tr key={idx}>
                            <td className="col-ab-input">{pair.input}</td>
                            <td className="col-ab-version">
                              <div className={`response-box ${!pair.v1 ? 'empty' : ''}`}>
                                {pair.v1?.output || 'Nenhum teste nesta versão'}
                              </div>
                              {pair.v1 && (
                                <div className="ab-meta">
                                  <span>⏱️ {pair.v1.latency_ms}ms</span>
                                  <span>🪙 {pair.v1.tokens_used} tokens</span>
                                </div>
                              )}
                            </td>
                            <td className="col-ab-version">
                              <div className={`response-box ${!pair.v2 ? 'empty' : ''}`}>
                                {pair.v2?.output || 'Nenhum teste nesta versão'}
                              </div>
                              {pair.v2 && (
                                <div className="ab-meta">
                                  <span>⏱️ {pair.v2.latency_ms}ms</span>
                                  <span>🪙 {pair.v2.tokens_used} tokens</span>
                                </div>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="no-selection" style={{padding: '20px'}}>
                    Nenhum input em comum encontrado para comparação A/B. Rode testes com o mesmo input em ambas as versões.
                  </div>
                )}
              </div>

              <h3 className="diff-section-title">⚙️ Configurações</h3>
              <div className="comparison-meta-diff">
                <div className="meta-column">
                  <div className="meta-item">
                    <span className="meta-label">Provider</span>
                    <span className={`meta-value ${v1.provider !== v2.provider ? 'text-warning' : ''}`}>
                      {v1.provider} {v1.provider !== v2.provider ? '→ ' + v2.provider : ''}
                    </span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">Modelo</span>
                    <span className={`meta-value ${v1.model !== v2.model ? 'text-warning' : ''}`}>
                      {v1.model} {v1.model !== v2.model ? '→ ' + v2.model : ''}
                    </span>
                  </div>
                </div>
                <div className="meta-column">
                  <div className="meta-item">
                    <span className="meta-label">Diferença de Data</span>
                    <span className="meta-value">v{v2.version} criada {Math.floor((new Date(v2.created_at).getTime() - new Date(v1.created_at).getTime()) / (1000 * 60 * 60 * 24))} dias depois</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">Descrição da v{v2.version}</span>
                    <span className="meta-value">{v2.change_description || 'Sem descrição.'}</span>
                  </div>
                </div>
              </div>

              <h3 className="diff-section-title">📝 Conteúdo do Prompt</h3>
              <div className="diff-wrapper">
                <div className="diff-container">
                  <div className="diff-header">
                    <div className="diff-header-item">v{v1.version} (Original)</div>
                    <div className="diff-header-item">v{v2.version} (Modificado)</div>
                  </div>
                  <div className="diff-content">
                    {textDiff?.left.map((line, idx) => (
                      <div key={idx} className="diff-row">
                        <div className={`diff-cell ${line.type} ${!line.content && line.type === 'unchanged' ? 'empty' : ''}`}>
                          {line.content || ' '}
                        </div>
                        <div className={`diff-cell ${textDiff.right[idx].type} ${!textDiff.right[idx].content && textDiff.right[idx].type === 'unchanged' ? 'empty' : ''}`}>
                          {textDiff.right[idx].content || ' '}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="diff-summary">
                  <div className="summary-item"><span className="indicator removed"></span> Remoções</div>
                  <div className="summary-item"><span className="indicator added"></span> Adições</div>
                </div>
              </div>
            </>
          )}

          {!v1 || !v2 && !error && (
            <div className="no-selection">
              Selecione as versões para iniciar a análise técnica.
            </div>
          )}

          {error && <div className="error-message">{error}</div>}
        </div>
      </div>
    </>
  );
};

export default VersionComparison;
