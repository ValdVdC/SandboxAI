import React, { useState, useEffect } from 'react';
import apiClient from '../services/api';
import { PromptVersion } from '../types';
import Alert from './Alert';
import '../styles/CreateVersion.css';

interface CreateVersionProps {
  promptId: string;
  currentVersion?: PromptVersion;
  onVersionCreated: (version: PromptVersion) => void;
  onCancel: () => void;
}

const PROVIDER_MODELS: Record<string, string[]> = {
  ollama: ['llama2:7b', 'mistral', 'neural-chat'],
  groq: ['llama-3.3-70b-versatile', 'openai/gpt-oss-120b', 'llama-3.1-8b-instant'],
  openai: ['gpt-4', 'gpt-3.5-turbo'],
  anthropic: ['claude-3-opus', 'claude-3-sonnet'],
};

const CreateVersion: React.FC<CreateVersionProps> = ({
  promptId,
  currentVersion,
  onVersionCreated,
  onCancel,
}) => {
  const [content, setContent] = useState(currentVersion?.content || '');
  const [provider, setProvider] = useState(currentVersion?.provider || 'groq');
  const [model, setModel] = useState(currentVersion?.model || 'llama-3.3-70b-versatile');
  const [changeDescription, setChangeDescription] = useState('');
  const [availableModels, setAvailableModels] = useState<string[]>(
    PROVIDER_MODELS[currentVersion?.provider || 'groq'] || []
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // Update available models when provider changes
  useEffect(() => {
    const models = PROVIDER_MODELS[provider] || [];
    setAvailableModels(models);
    if (!models.includes(model)) {
      setModel(models[0] || '');
    }
  }, [provider, model]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (!content.trim()) {
        throw new Error('Conteúdo do prompt é obrigatório');
      }

      const versionData = { 
        content, 
        provider, 
        model,
        change_description: changeDescription,
      };
      const newVersion = await apiClient.createVersion(promptId, versionData);

      setSuccess(true);
      setTimeout(() => {
        onVersionCreated(newVersion);
      }, 1500);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to create version';
    //   console.error('Version creation error:', err);
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-version">
      <div className="create-version-header">
        <h3>Nova Versão do Prompt</h3>
        <p className="subtitle">
          {currentVersion ? 'Baseado na versão v' + currentVersion.version : 'Criar primeira versão'}
        </p>
      </div>

      {error && <Alert type="error" message={error} onClose={() => setError(null)} />}
      {success && (
        <Alert type="success" message="Versão criada com sucesso!" />
      )}

      <form className="version-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="content">Conteúdo do Prompt</label>
          <textarea
            id="content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Digite o conteúdo do novo prompt..."
            required
            rows={8}
            className="form-control"
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="provider">Provider</label>
            <select
              id="provider"
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              className="form-control"
            >
              <option value="groq">Groq</option>
              <option value="ollama">Ollama (Local)</option>
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="model">Modelo</label>
            <select
              id="model"
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="form-control"
            >
              {availableModels.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
            <small>Modelos disponíveis para {provider}</small>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="changeDescription">Descrição da Mudança (Opcional)</label>
          <input
            id="changeDescription"
            type="text"
            value={changeDescription}
            onChange={(e) => setChangeDescription(e.target.value)}
            placeholder="Descreva o que mudou nesta versão..."
            className="form-control"
          />
        </div>

        <div className="form-actions">
          <button
            type="button"
            onClick={onCancel}
            disabled={loading}
            className="btn btn-secondary"
          >
            Cancelar
          </button>
          <button type="submit" disabled={loading} className="btn btn-primary">
            {loading ? 'Criando...' : 'Criar Nova Versão'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CreateVersion;
