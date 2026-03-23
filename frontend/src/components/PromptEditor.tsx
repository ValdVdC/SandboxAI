import React, { useState, useEffect } from 'react';
import apiClient from '../services/api';
import { CreatePromptRequest } from '../types';
import Alert from './Alert';
import '../styles/PromptEditor.css';

interface PromptEditorProps {
  initialName?: string;
  initialDescription?: string;
  initialContent?: string;
  initialProvider?: string;
  initialModel?: string;
  isNew?: boolean;
  onSave: (prompt: any) => void;
  onCancel: () => void;
}

interface ProviderStatus {
  [key: string]: {
    available: boolean;
    reason: string;
  };
}

const PROVIDER_MODELS: Record<string, string[]> = {
  ollama: ['llama2:7b', 'mistral', 'neural-chat'],
  groq: ['llama-3.3-70b-versatile', 'gemma2-9b-it', 'llama-3.1-8b-instant'],
  openai: ['gpt-4', 'gpt-3.5-turbo'],
  anthropic: ['claude-3-opus', 'claude-3-sonnet'],
};

const PromptEditor: React.FC<PromptEditorProps> = ({
  initialName = '',
  initialDescription = '',
  initialContent = '',
  initialProvider = 'groq',
  initialModel = 'llama-3.3-70b-versatile',
  isNew = true,
  onSave,
  onCancel,
}) => {
  const [name, setName] = useState(initialName);
  const [description, setDescription] = useState(initialDescription);
  const [content, setContent] = useState(initialContent);
  const [provider, setProvider] = useState(initialProvider);
  const [model, setModel] = useState(initialModel);
  const [availableModels, setAvailableModels] = useState<string[]>(
    PROVIDER_MODELS[initialProvider] || []
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [providerStatus, setProviderStatus] = useState<ProviderStatus>({
    groq: { available: true, reason: 'API key configured' },
    ollama: { available: false, reason: 'Service not running (disabled in this deployment)' },
    openai: { available: false, reason: 'API key not configured' },
    anthropic: { available: false, reason: 'API key not configured' },
  });
  const [loadingProviders, setLoadingProviders] = useState(true);

  // Fetch provider status on mount
  useEffect(() => {
    const fetchProviderStatus = async () => {
      try {
        const response = await fetch('http://localhost:8000/providers/status');
        if (response.ok) {
          const status = await response.json();
          setProviderStatus(status);
          
          // If current provider is not available, switch to first available one
          if (!status[provider]?.available) {
            const firstAvailable = Object.keys(status).find(p => status[p].available);
            if (firstAvailable) {
              setProvider(firstAvailable);
            }
          }
        }
      } catch (err) {
        console.error('Failed to fetch provider status:', err);
      } finally {
        setLoadingProviders(false);
      }
    };

    fetchProviderStatus();
  }, []);

  // Update available models when provider changes
  useEffect(() => {
    const models = PROVIDER_MODELS[provider] || [];
    setAvailableModels(models);
    // Set model to first available if current model not in list
    if (!models.includes(model)) {
      setModel(models[0] || '');
    }
  }, [provider, model]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (isNew) {
        // Step 1: Create prompt (only name and description)
        const createPromptData: CreatePromptRequest = { name, description };
        console.log('Creating prompt with:', createPromptData);
        const prompt = await apiClient.createPrompt(createPromptData);
        console.log('Prompt created:', prompt);
        
        // Step 2: Create initial version (content, provider, model)
        const versionData = { content, provider, model };
        console.log('Creating version with:', versionData);
        await apiClient.createVersion(prompt.id, versionData);
        console.log('Version created successfully');
        
        setSuccess(true);
        // Signal that a new prompt was created
        localStorage.setItem('newPromptCreated', 'true');
        setTimeout(() => onSave(prompt), 1500);
      } else {
        // Update flow - would need prompt ID
        setSuccess(true);
        setTimeout(() => onSave(null), 1500);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to save prompt';
      console.error('Prompt creation error:', err);
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="prompt-editor" onSubmit={handleSubmit}>
      <h2>{isNew ? 'Novo Prompt' : 'Editar Prompt'}</h2>

      {error && <Alert type="error" message={error} onClose={() => setError(null)} />}
      {success && <Alert type="success" message="Prompt salvo com sucesso!" />}

      <div className="form-group">
        <label htmlFor="name">Nome</label>
        <input
          id="name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Ex: Tradutor de Poesia"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="description">Descrição</label>
        <input
          id="description"
          type="text"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Descreva o propósito deste prompt"
        />
      </div>

      <div className="form-group">
        <label htmlFor="content">Conteúdo do Prompt</label>
        <textarea
          id="content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Digite o conteúdo do seu prompt aqui..."
          required
          rows={12}
        />
        <small>Dica: Use {'{input}'} para marcar onde a entrada do teste será inserida</small>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="provider">Provider</label>
          <select
            id="provider"
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            required
          >
            <option value="groq" disabled={providerStatus.groq?.available === false}>
              {providerStatus.groq?.available === false ? 'Groq (Desativado)' : 'Groq'}
            </option>
            <option value="ollama" disabled={providerStatus.ollama?.available === false}>
              {providerStatus.ollama?.available === false ? 'Ollama (Local) (Desativado)' : 'Ollama (Local)'}
            </option>
            <option value="openai" disabled={providerStatus.openai?.available === false}>
              {providerStatus.openai?.available === false ? 'OpenAI (Desativado)' : 'OpenAI'}
            </option>
            <option value="anthropic" disabled={providerStatus.anthropic?.available === false}>
              {providerStatus.anthropic?.available === false ? 'Anthropic (Desativado)' : 'Anthropic'}
            </option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="model">Modelo</label>
          <select
            id="model"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            required
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

      <div className="form-actions">
        <button type="submit" disabled={loading} className="btn btn-primary">
          {loading ? 'Salvando...' : 'Salvar'}
        </button>
        <button type="button" onClick={onCancel} className="btn btn-secondary">
          Cancelar
        </button>
      </div>
    </form>
  );
};

export default PromptEditor;
