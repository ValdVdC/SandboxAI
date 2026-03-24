import React from 'react';
import '../styles/ProviderSelector.css';

interface ProviderStatus {
  [key: string]: {
    available: boolean;
    reason: string;
  };
}

interface ProviderSelectorProps {
  value: string;
  onChange: (provider: string) => void;
  status: ProviderStatus;
}

const PROVIDER_INFO: Record<string, { label: string; icon: string; color: string }> = {
  groq: {
    label: 'Groq',
    icon: '⚡',
    color: '#f39c12'
  },
  ollama: {
    label: 'Ollama',
    icon: '🦙',
    color: '#9b59b6'
  },
  openai: {
    label: 'OpenAI',
    icon: '🤖',
    color: '#3498db'
  },
  anthropic: {
    label: 'Anthropic',
    icon: '🧠',
    color: '#e74c3c'
  },
};

const ProviderSelector: React.FC<ProviderSelectorProps> = ({ value, onChange, status }) => {
  return (
    <div className="provider-selector">
      <label className="provider-label">Selecione o Provider</label>
      <div className="provider-grid">
        {Object.entries(PROVIDER_INFO).map(([key, info]) => {
          const isAvailable = status[key]?.available === true;
          const isSelected = value === key;

          return (
            <button
              key={key}
              type="button"
              className={`provider-card ${isSelected ? 'selected' : ''} ${!isAvailable ? 'disabled' : ''}`}
              onClick={() => {
                if (isAvailable) {
                  onChange(key);
                }
              }}
              disabled={!isAvailable}
              title={!isAvailable ? status[key]?.reason : ''}
            >
              <div className="provider-icon">{info.icon}</div>
              <div className="provider-name">{info.label}</div>
              {!isAvailable && (
                <div className="provider-status">
                  <span className="status-badge">❌ Desativado</span>
                </div>
              )}
              {isAvailable && (
                <div className="provider-status">
                  <span className="status-badge available">✓ Disponível</span>
                </div>
              )}
              {!isAvailable && (
                <div className="provider-reason">{status[key]?.reason}</div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default ProviderSelector;
