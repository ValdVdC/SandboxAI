import React, { useEffect, useState } from 'react';
import apiClient from '../services/api';
import { PromptVersion } from '../types';
import '../styles/VersionList.css';

interface VersionListProps {
  promptId: string;
  selectedVersionId?: string;
  versionRefreshTrigger?: number;
  onSelectVersion: (version: PromptVersion) => void;
}

const VersionList: React.FC<VersionListProps> = ({ promptId, selectedVersionId, versionRefreshTrigger, onSelectVersion }) => {
  const [versions, setVersions] = useState<PromptVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchVersions = async () => {
      try {
        setLoading(true);
        const response = await apiClient.getPromptVersions(promptId);
        const sorted = response.items.sort((a, b) => b.version - a.version);
        setVersions(sorted);
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Failed to fetch versions';
        console.error('Error fetching versions:', { error: err, errorMsg });
        setError(errorMsg);
      } finally {
        setLoading(false);
      }
    };

    if (promptId) {
      fetchVersions();
    }
  }, [promptId, versionRefreshTrigger]);

  if (loading) return <div className="version-list-loading">Carregando versões...</div>;
  if (error) return <div className="version-list-error">{error}</div>;

  return (
    <div className="version-list">
      <h3>Histórico de Versões</h3>
      {versions.length === 0 ? (
        <p className="no-versions">Nenhuma versão encontrada</p>
      ) : (
        <ul>
          {versions.map((v) => (
            <li
              key={v.id}
              onClick={() => onSelectVersion(v)}
              className={`version-item ${selectedVersionId === v.id ? 'active' : ''}`}
            >
              <div className="version-header">
                <span className="version-number">v{v.version}</span>
                <span className="version-date">
                  {new Date(v.created_at).toLocaleDateString('pt-BR')}
                </span>
              </div>
              {v.change_description && (
                <p className="version-description">{v.change_description}</p>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default VersionList;
