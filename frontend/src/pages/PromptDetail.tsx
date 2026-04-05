import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Loading from '../components/Loading';
import VersionList from '../components/VersionList';
import TestRunner from '../components/TestRunner';
import TestResults from '../components/TestResults';
import TestHistory from '../components/TestHistory';
import BulkResults from '../components/BulkResults';
import PromptAnalytics from '../components/PromptAnalytics';
import CreateVersion from '../components/CreateVersion';
import { usePromptDetail } from '../hooks/useApiData';
import { PromptVersion } from '../types';
import apiClient from '../services/api';
import '../styles/PromptDetail.css';

const PromptDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { prompt, loading, error } = usePromptDetail(id || '');
  const [selectedVersion, setSelectedVersion] = useState<PromptVersion | null>(null);
  const [versions, setVersions] = useState<PromptVersion[]>([]);
  const [versionsLoading, setVersionsLoading] = useState(true);
  const [activeTest, setActiveTest] = useState<string | null>(null);
  const [bulkTestIds, setBulkTestIds] = useState<string[] | null>(null);
  const [compareMode, setCompareMode] = useState(false);
  const [showCreateVersion, setShowCreateVersion] = useState(false);
  const [showTestHistory, setShowTestHistory] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [versionRefreshTrigger, setVersionRefreshTrigger] = useState(0);

  // Load versions and auto-select LATEST one
  useEffect(() => {
    const loadVersions = async () => {
      if (!id) return;
      try {
        setVersionsLoading(true);
        const response = await apiClient.getPromptVersions(id);
        const sorted = response.items.sort((a, b) => b.version - a.version);
        setVersions(sorted);
        // Auto-select the LATEST version (first in descending order) only on initial load
        setSelectedVersion((prev) => (prev === null && sorted.length > 0 ? sorted[0] : prev));
      } catch (err) {
        console.error('Failed to load versions:', err);
      } finally {
        setVersionsLoading(false);
      }
    };

    loadVersions();
  }, [id]);

  const handleVersionCreated = (newVersion: PromptVersion) => {
    // Force VersionList to refetch
    setVersionRefreshTrigger((prev: number) => prev + 1);
    
    // Immediately reload versions and select the new one
    if (id) {
      const loadVersions = async () => {
        try {
          const response = await apiClient.getPromptVersions(id);
          const sorted = response.items.sort((a, b) => b.version - a.version);
          setVersions(sorted);
          // Select the newly created version
          setSelectedVersion(newVersion);
          setShowCreateVersion(false);
        } catch (err) {
          console.error('Failed to reload versions:', err);
        }
      };
      loadVersions();
    }
  };

  if (!id) return <div>Prompt not found</div>;
  if (loading) return <Loading message="Carregando prompt..." />;
  if (error) return <div className="error-message">{error}</div>;
  if (!prompt) return <div>Prompt não encontrado</div>;
  if (versionsLoading) return <Loading message="Carregando versões..." />;
  if (versions.length === 0) return <div className="error-message">Nenhuma versão encontrada para este prompt</div>;

  return (
    <>
      <Header />
      <div className="prompt-detail">
        <div className="detail-header">
          <h1>{prompt.name}</h1>
          <p className="description">{prompt.description}</p>
          <div className="meta">
            <span>Versão atual: v{prompt.current_version}</span>
            <span>
              Criado em: {new Date(prompt.created_at).toLocaleDateString('pt-BR')}
            </span>
          </div>
        </div>

        <div className="detail-content">
          <div className="sidebar">
            <VersionList
              promptId={id}
              selectedVersionId={selectedVersion?.id}
              versionRefreshTrigger={versionRefreshTrigger}
              onSelectVersion={(version) => {
                setSelectedVersion(version);
              }}
            />
          </div>

          <div className="main-content">
            {bulkTestIds ? (
              <BulkResults testIds={bulkTestIds} onBack={() => setBulkTestIds(null)} />
            ) : activeTest ? (
              <TestResults testId={activeTest} autoRefresh={true} onBack={() => setActiveTest(null)} />
            ) : showAnalytics ? (
              <PromptAnalytics 
                promptId={id || ''} 
                selectedVersionNumber={selectedVersion?.version}
                onBack={() => setShowAnalytics(false)} 
              />
            ) : (
              <>
                {selectedVersion && (
                  <div className="version-info">
                    <div className="version-header">
                      <h3>Versão Selecionada: v{selectedVersion.version}</h3>
                      <div className="version-meta">
                        <span className="provider-badge">{selectedVersion.provider.toUpperCase()}</span>
                        <span className="model-badge">{selectedVersion.model}</span>
                        <span className="date">{new Date(selectedVersion.created_at).toLocaleDateString('pt-BR')}</span>
                      </div>
                    </div>
                    {selectedVersion.change_description && (
                      <div className="version-change">
                        <h4>Descrição da Mudança:</h4>
                        <p>{selectedVersion.change_description}</p>
                      </div>
                    )}
                    <div className="version-content">
                      <h4>Conteúdo do Prompt:</h4>
                      <pre className="code-block">{selectedVersion.content}</pre>
                    </div>
                  </div>
                )}

                <div className="version-actions">
                  <button
                    className={`tab-btn ${!showCreateVersion && !showTestHistory && !showAnalytics ? 'active' : ''}`}
                    onClick={() => {
                      setShowCreateVersion(false);
                      setShowTestHistory(false);
                      setShowAnalytics(false);
                    }}
                  >
                    Executar Teste
                  </button>
                  <button
                    className={`tab-btn ${showTestHistory ? 'active' : ''}`}
                    onClick={() => {
                      setShowTestHistory(true);
                      setShowCreateVersion(false);
                      setShowAnalytics(false);
                    }}
                  >
                    Histórico de Testes
                  </button>
                  <button
                    className={`tab-btn ${showAnalytics ? 'active' : ''}`}
                    onClick={() => {
                      setShowAnalytics(true);
                      setShowTestHistory(false);
                      setShowCreateVersion(false);
                    }}
                  >
                    Analytics
                  </button>
                  <button
                    className={`tab-btn ${showCreateVersion ? 'active' : ''}`}
                    onClick={() => {
                      setShowCreateVersion(true);
                      setShowTestHistory(false);
                      setShowAnalytics(false);
                    }}
                  >
                    + Nova Versão
                  </button>
                  <button
                    className="tab-btn"
                    onClick={() => navigate(`/prompts/${id}/compare`)}
                  >
                    Comparar Versões
                  </button>
                </div>

                {showCreateVersion ? (
                  <CreateVersion
                    promptId={id}
                    currentVersion={selectedVersion ?? undefined}
                    onVersionCreated={handleVersionCreated}
                    onCancel={() => setShowCreateVersion(false)}
                  />
                ) : showTestHistory && selectedVersion ? (
                  <TestHistory 
                    key={`${id}-${selectedVersion.version}`} 
                    promptId={id} 
                    versionNumber={selectedVersion.version}
                    onViewBatch={(ids) => setBulkTestIds(ids)}
                  />
                ) : (
                  <TestRunner
                    promptId={id}
                    versionNumber={selectedVersion?.version || prompt.current_version}
                    onTestStarted={setActiveTest}
                    onBulkStarted={(ids) => setBulkTestIds(ids)}
                  />
                )}

                {selectedVersion && compareMode && (
                  <div className="comparison-view">
                    <h2>Comparação de Versões</h2>
                    <div className="comparison-container">
                      <div className="version-panel">
                        <h3>Versão Atual (v{prompt.current_version})</h3>
                        <pre className="code-block">{/* Current version content would go here */}</pre>
                      </div>
                      <div className="version-panel">
                        <h3>
                          Versão Selecionada (v{selectedVersion.version})
                        </h3>
                        <pre className="code-block">{selectedVersion.content}</pre>
                      </div>
                    </div>
                    <div className="comparison-actions">
                      <button
                        className="btn btn-secondary"
                        onClick={() => setCompareMode(false)}
                      >
                        Voltar
                      </button>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default PromptDetail;
