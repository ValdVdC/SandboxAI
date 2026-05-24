import React, { useState, useRef } from 'react';
import Papa from 'papaparse';
import apiClient from '../services/api';
import Alert from './Alert';
import '../styles/TestRunner.css';

interface TestRunnerProps {
  promptId: string;
  versionNumber: number;
  onTestStarted: (testId: string) => void;
  onBulkStarted?: (testIds: string[]) => void;
}

const TestRunner: React.FC<TestRunnerProps> = ({ promptId, versionNumber, onTestStarted, onBulkStarted }) => {
  const [testInput, setTestInput] = useState('');
  const [expectedOutput, setExpectedOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<'single' | 'bulk' | 'upload'>('single');
  const [file, setFile] = useState<File | null>(null);
  const [previewHeaders, setPreviewHeaders] = useState<string[]>([]);
  const [previewRows, setPreviewRows] = useState<string[][]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;
    
    setFile(selectedFile);
    
    // Create preview
    if (selectedFile.name.endsWith('.csv')) {
      Papa.parse(selectedFile, {
        header: true,
        preview: 3,
        complete: (results: Papa.ParseResult<Record<string, string>>) => {
          if (results.meta.fields) {
            setPreviewHeaders(results.meta.fields);
            setPreviewRows(results.data.map((row) => results.meta.fields!.map(f => row[f] ?? '')));
          }
        }
      });
    } else if (selectedFile.name.endsWith('.json')) {
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const json = JSON.parse(event.target?.result as string) as Record<string, unknown>[];
          if (Array.isArray(json) && json.length > 0) {
            const headers = Object.keys(json[0]);
            setPreviewHeaders(headers);
            setPreviewRows(json.slice(0, 3).map((obj) => headers.map(h => String(obj[h] ?? ''))));
          }
        } catch (errorParse) {
          setError('Failed to parse JSON for preview');
        }
      };
      reader.readAsText(selectedFile);
    }
  };

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
      } else if (mode === 'bulk') {
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
      } else if (mode === 'upload') {
        if (!file) throw new Error('Selecione um arquivo CSV ou JSON.');
        const response = await apiClient.executeBulkTestsUpload(promptId, versionNumber, file);
        setFile(null);
        setPreviewHeaders([]);
        setPreviewRows([]);
        if (fileInputRef.current) fileInputRef.current.value = '';
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
          Teste em Lote (Manual)
        </button>
        <button 
          className={`tab-btn ${mode === 'upload' ? 'active' : ''}`}
          onClick={() => setMode('upload')}
        >
          Upload Dataset (CSV/JSON)
        </button>
      </div>

      <form className="test-runner" onSubmit={handleSubmit}>
        <h3>{mode === 'single' ? 'Executar Teste' : mode === 'bulk' ? 'Executar Testes em Lote' : 'Upload de Dataset'}</h3>

        {error && <Alert type="error" message={error} onClose={() => setError(null)} />}

        {mode === 'upload' ? (
          <div className="form-group">
            <label>Selecione um arquivo .csv ou .json</label>
            <input 
              type="file" 
              accept=".csv,.json" 
              onChange={handleFileChange} 
              ref={fileInputRef}
              required 
              className="d-block-mb-1"
            />
            {file && previewHeaders.length > 0 && (
              <div className="dataset-preview">
                <h4>Preview ({file.name})</h4>
                <div className="overflow-x-auto">
                  <table className="preview-table">
                    <thead>
                      <tr>
                        {previewHeaders.map((h, i) => (
                          <th key={i} style={h.toLowerCase() === 'expected' ? { color: 'var(--success-color)' } : {}}>{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {previewRows.map((row, i) => (
                        <tr key={i}>
                          {row.map((cell, j) => (
                            <td key={j}>{String(cell).length > 50 ? String(cell).substring(0, 50) + '...' : String(cell)}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <small className="text-muted">Apenas as 3 primeiras linhas são exibidas.</small>
              </div>
            )}
          </div>
        ) : (
          <>
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
          </>
        )}

        <button type="submit" disabled={loading || (mode === 'upload' && !file)} className="btn btn-primary">
          {loading ? 'Processando...' : mode === 'single' ? 'Executar Teste' : mode === 'bulk' ? `Executar ${testInput.split('\n').filter(l => l.trim()).length} Testes` : 'Fazer Upload e Executar'}
        </button>
      </form>
    </div>
  );
};

export default TestRunner;
