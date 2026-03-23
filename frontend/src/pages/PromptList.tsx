import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Loading from '../components/Loading';
import Alert from '../components/Alert';
import { usePrompts } from '../hooks/useApiData';
import apiClient from '../services/api';
import '../styles/PromptList.css';

const PromptList: React.FC = () => {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const { prompts, loading, error } = usePrompts(search);
  const [deleting, setDeleting] = useState<string | null>(null);

  // Listen for new prompt creation
  useEffect(() => {
    const handleStorageChange = () => {
      const flag = localStorage.getItem('newPromptCreated');
      if (flag === 'true') {
        console.log('New prompt created, refreshing list...');
        localStorage.removeItem('newPromptCreated');
        // Force full page reload to get new prompts
        window.location.reload();
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const handleDelete = async (id: string) => {
    if (confirm('Tem certeza que deseja deletar este prompt e todas as suas versões?')) {
      setDeleting(id);
      try {
        await apiClient.deletePrompt(id);
        // Refresh list
        window.location.reload();
      } catch (err) {
        alert(`Erro ao deletar: ${err instanceof Error ? err.message : 'Unknown error'}`);
        setDeleting(null);
      }
    }
  };

  return (
    <>
      <Header />
      <div className="prompt-list-page">
        <div className="page-header">
          <h1>Meus Prompts</h1>
          <button className="btn btn-primary" onClick={() => navigate('/create-prompt')}>
            + Novo Prompt
          </button>
        </div>

        <div className="search-box">
          <input
            type="text"
            placeholder="Buscar prompts por nome..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {loading ? (
          <Loading message="Carregando prompts..." />
        ) : error ? (
          <Alert type="error" message={error} />
        ) : (
          <div className="prompts-grid">
            {prompts.length === 0 ? (
              <div className="no-prompts">
                <p>Nenhum prompt encontrado.</p>
                <button
                  className="btn btn-primary"
                  onClick={() => navigate('/create-prompt')}
                >
                  Criar Primeiro Prompt
                </button>
              </div>
            ) : (
              prompts.map((prompt) => (
                <div key={prompt.id} className="prompt-card">
                  <div className="card-header">
                    <h3>{prompt.name}</h3>
                    <span className="version-badge">v{prompt.current_version}</span>
                  </div>
                  <p className="card-description">{prompt.description}</p>
                  <div className="card-meta">
                    <span className="date">
                      {new Date(prompt.created_at).toLocaleDateString('pt-BR')}
                    </span>
                  </div>
                  <div className="card-actions">
                    <button
                      className="btn btn-primary"
                      onClick={() => navigate(`/prompts/${prompt.id}`)}
                    >
                      Abrir
                    </button>
                    <button
                      className="btn btn-danger"
                      disabled={deleting === prompt.id}
                      onClick={() => handleDelete(prompt.id)}
                    >
                      {deleting === prompt.id ? 'Deletando...' : 'Deletar'}
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </>
  );
};

export default PromptList;
