import React, { useEffect, useState, useCallback } from 'react'
import apiClient from '../services/api'
import { TestResult } from '../types'
import Loading from './Loading'
import '../styles/TestResults.css'

interface TestResultsProps {
  promptId: string
  versionNumber: number
  testId: string
  autoRefresh?: boolean
  onBack?: () => void
}

const TestResults: React.FC<TestResultsProps> = ({
  promptId,
  versionNumber,
  testId,
  autoRefresh = true,
  onBack,
}) => {
  const [result, setResult] = useState<TestResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [exporting, setExporting] = useState(false)

  const handleExport = async () => {
    try {
      setExporting(true)
      await apiClient.exportTests(promptId, versionNumber)
    } catch (err) {
      console.error('Export failed', err)
    } finally {
      setExporting(false)
    }
  }

  const handleOverride = async (isCorrect: boolean) => {
    if (!result) return
    try {
      const updatedResult = await apiClient.overrideTestResult(
        result.id,
        isCorrect
      )
      setResult(updatedResult)
    } catch (err) {
      console.error('Failed to override test result', err)
      alert('Falha ao registrar override manual.')
    }
  }

  const fetchResult = useCallback(async () => {
    try {
      const resultData = await apiClient.getTestExecution(testId)
      setResult(resultData as TestResult)
    } catch (err) {
      console.error('Error fetching test result:', err)
      setError(
        err instanceof Error ? err.message : 'Failed to fetch test result'
      )
    } finally {
      setLoading(false)
    }
  }, [testId])

  // Initial fetch
  useEffect(() => {
    fetchResult()
  }, [fetchResult])

  // Polling loop
  useEffect(() => {
    if (
      autoRefresh &&
      (result?.status === 'queued' ||
        result?.status === 'pending' ||
        result?.status === 'running')
    ) {
      const interval = setInterval(fetchResult, 1000)
      return () => clearInterval(interval)
    }
  }, [result?.status, autoRefresh, fetchResult])

  if (loading) return <Loading message="Carregando resultados do teste..." />

  if (error) {
    return <div className="error-message">{error}</div>
  }

  if (!result) {
    return <div className="error-message">Teste não encontrado</div>
  }

  return (
    <div className="test-results">
      <div className="test-results-header">
        {onBack && (
          <button className="btn btn-secondary back-btn" onClick={onBack}>
            ← Voltar
          </button>
        )}
        <h2>Resultados do Teste</h2>
        {result && (
          <button
            className="btn btn-primary btn-small"
            onClick={handleExport}
            disabled={
              exporting ||
              result.status === 'queued' ||
              result.status === 'pending' ||
              result.status === 'running'
            }
          >
            {exporting ? 'Exportando...' : 'Exportar Versão'}
          </button>
        )}
      </div>

      <div className="test-status">
        <span className={`status-badge status-${result.status}`}>
          {result.status}
        </span>
        {result.status === 'completed' &&
          result.is_correct !== null &&
          result.is_correct !== undefined && (
            <span
              className={`validation-badge ${result.is_correct ? 'pass' : 'fail'}`}
            >
              {result.is_correct ? '✅ PASS' : '❌ FAIL'}
            </span>
          )}
        {result.is_human_overridden && (
          <span className="override-badge override-badge-lg">
            ⚠️ Override Manual
          </span>
        )}
        {result.status === 'completed' && (
          <span className="override-actions ml-8">
            <button
              className="btn btn-secondary btn-small-actions"
              onClick={() => handleOverride(true)}
              title="Aprovar"
              aria-label="Aprovar"
            >
              👍
            </button>
            <button
              className="btn btn-secondary btn-small-action"
              onClick={() => handleOverride(false)}
              title="Reprovar"
              aria-label="Reprovar"
            >
              👎
            </button>
          </span>
        )}
        {result.created_at && (
          <span className="test-date">
            {new Date(result.created_at).toLocaleString('pt-BR')}
          </span>
        )}
      </div>

      {result.status === 'queued' && (
        <div className="running-indicator">
          <span className="spinner"></span>
          Teste em execução...
        </div>
      )}

      <div className="test-input-output">
        <div className="section">
          <h3>Entrada</h3>
          <pre className="code-block">{result.input || 'Sem entrada'}</pre>
        </div>

        {result.expected && (
          <div className="section">
            <h3>Saída Esperada</h3>
            <pre className="code-block">{result.expected}</pre>
          </div>
        )}

        {result.status === 'completed' && (
          <div className="section">
            <h3>Saída Real</h3>
            <pre className="code-block">{result.output || 'Sem saída'}</pre>
          </div>
        )}

        {result.status === 'failed' && (
          <div className="section error">
            <h3>Erro</h3>
            <pre className="code-block">
              {result.error_message || 'Erro desconhecido'}
            </pre>
          </div>
        )}
      </div>

      {result.status === 'completed' && (
        <div className="metrics-grid">
          <div className="metric">
            <label>Latência</label>
            <span className="value">{result.latency_ms || 0}ms</span>
          </div>
          <div className="metric">
            <label>Tokens</label>
            <span className="value">{result.tokens_used || 0}</span>
          </div>
          <div className="metric">
            <label>Custo USD</label>
            <span className="value">
              $
              {typeof result.cost_usd === 'number'
                ? result.cost_usd.toFixed(6)
                : '0.000000'}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}

export default TestResults
