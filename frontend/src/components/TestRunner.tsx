import React, { useState } from 'react';
import apiClient from '../services/api';
import Alert from './Alert';
import '../styles/TestRunner.css';

interface TestRunnerProps {
  promptId: string;
  versionId: string;
  versionNumber: number;
  onTestStarted: (testId: string) => void;
}

const TestRunner: React.FC<TestRunnerProps> = ({ promptId, versionId, versionNumber, onTestStarted }) => {
  const [testInput, setTestInput] = useState('');
  const [expectedOutput, setExpectedOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Debug log
  console.log('TestRunner props:', { promptId, versionId, versionNumber });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    console.log('Submit handler called with:', { promptId, versionNumber, testInput, expectedOutput });
    
    // Validation: ensure versionNumber is valid
    if (!versionNumber || versionNumber <= 0) {
      const errorMsg = 'Versão inválida. Selecione uma versão válida.';
      console.error(errorMsg, { versionNumber });
      setError(errorMsg);
      return;
    }
    
    setLoading(true);
    setError(null);

    try {
      const payload = {
        input: testInput,
        expected: expectedOutput || undefined,
      };
      console.log('Executing test with:', { promptId, versionNumber, payload });
      const test = await apiClient.executeTest(
        promptId,
        versionNumber,
        payload
      );
      console.log('Test response:', test);
      console.log('Test test_id:', test.test_id);
      setTestInput('');
      setExpectedOutput('');
      if (test.test_id) {
        console.log('Calling onTestStarted with:', test.test_id);
        onTestStarted(test.test_id);
      } else {
        throw new Error('No test_id in response');
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to start test';
      console.error('Test execution error:', { error: err, errorMsg });
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="test-runner" onSubmit={handleSubmit}>
      <h3>Executar Teste</h3>

      {error && <Alert type="error" message={error} onClose={() => setError(null)} />}

      <div className="form-group">
        <label htmlFor="input">Entrada de Teste</label>
        <textarea
          id="input"
          value={testInput}
          onChange={(e) => setTestInput(e.target.value)}
          placeholder="Digite o texto de entrada para testar o prompt"
          required
          rows={4}
        />
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
        {loading ? 'Executando...' : 'Executar Teste'}
      </button>
    </form>
  );
};

export default TestRunner;
