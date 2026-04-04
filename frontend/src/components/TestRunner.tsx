import React, { useState } from 'react';
import apiClient from '../services/api';
import Alert from './Alert';
import '../styles/TestRunner.css';

interface TestRunnerProps {
  promptId: string;
  versionId: string;
  versionNumber: number;
  onTestStarted: (testId: string) => void;
  onBulkStarted?: (testIds: string[]) => void;
}

const TestRunner: React.FC<TestRunnerProps> = ({ promptId, versionId, versionNumber, onTestStarted, onBulkStarted }) => {
  const [testInput, setTestInput] = useState('');
  const [expectedOutput, setExpectedOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<'single' | 'bulk'>('single');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!versionNumber || versionNumber <= 0) {
      setError('Versão inválida. Selecione uma versão válida.');
      return;
    }
    
    setLoading(true);
    setError(null);

    try {
      if (mode === 'single') {
        const test = await apiClient.executeTest(promptId, versionNumber, {
          input: testInput,
          expected: expectedOutput || undefined,
        });
        setTestInput('');
        setExpectedOutput('');
        if (test.test_id) {
          onTestStarted(test.test_id);
        }
      } else {
        // Bulk mode
        const inputs = testInput.split('\n').map(i => i.trim()).filter(i => i.length > 0);
        if (inputs.length === 0) {
          throw new Error('Insira ao menos uma entrada válida por linha.');
        }
        
        const response = await apiClient.executeBulkTests(promptId, versionNumber, {
          inputs,
          expected: expectedOutput || undefined,
        });
        
        setTestInput('');
        setExpectedOutput('');
        if (onBulkStarted && response.test_ids) {
          onBulkStarted(response.test_ids);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao iniciar teste(s)');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="test-runner-container">
      <div className="runner-tabs">
        <button 
          className={`tab-btn ${mode === 'single' ? 'active' : ''}`}
          onClick={() => setMode('single')}
        >
          Teste Único
        </button>
        <button 
          className={`tab-btn ${mode === 'bulk' ? 'active' : ''}`}
          onClick={() => setMode('bulk')}
        >
          Teste em Lote (Bulk)
        </button>
      </div>

      <form className="test-runner" onSubmit={handleSubmit}>
        <h3>{mode === 'single' ? 'Executar Teste' : 'Executar Testes em Lote'}</h3>

        {error && <Alert type="error" message={error} onClose={() => setError(null)} />}

        <div className="form-group">
          <label htmlFor="input">
            {mode === 'single' ? 'Entrada de Teste' : 'Entradas de Teste (uma por linha)'}
          </label>
          <textarea
            id="input"
            value={testInput}
            onChange={(e) => setTestInput(e.target.value)}
            placeholder={mode === 'single' ? "Digite o texto de entrada..." : "Entrada 1\nEntrada 2\nEntrada 3..."}
            required
            rows={mode === 'single' ? 4 : 8}
          />
          {mode === 'bulk' && <small className="text-muted">Cada linha será executada como um teste independente.</small>}
        </div>

        <div className="form-group">
          <label htmlFor="expected">Saída Esperada (Opcional)</label>
          <textarea
            id="expected"
            value={expectedOutput}
            onChange={(e) => setExpectedOutput(e.target.value)}
            placeholder="Se definido, será comparado com a saída real"
            rows={3}
          />
        </div>

        <button type="submit" disabled={loading} className="btn btn-primary">
          {loading ? 'Processando...' : mode === 'single' ? 'Executar Teste' : `Executar ${testInput.split('\n').filter(l => l.trim()).length} Testes`}
        </button>
      </form>
    </div>
  );
};

export default TestRunner;
