import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Header from '../components/Header'
import Loading from '../components/Loading'
import Alert from '../components/Alert'
import apiClient from '../services/api'
import { useApiData } from '../hooks/useApiData'
import { Prompt, PlaygroundColumnResult, PlaygroundConfig } from '../types'
import '../styles/Playground.css'

const DEFAULT_MODELS: Record<string, string[]> = {
  groq: ['llama-3.3-70b-versatile', 'gemma2-9b-it', 'llama-3.1-8b-instant'],
  openai: ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo'],
  ollama: ['llama3', 'mistral', 'llama2', 'neural-chat'],
  anthropic: [
    'claude-3-5-sonnet-latest',
    'claude-3-opus-latest',
    'claude-3-haiku-20240307',
  ],
}

const PROVIDER_COLORS: Record<string, string> = {
  openai: 'var(--success-color, #10b981)',
  groq: '#ff6b00',
  ollama: 'var(--primary-color, #3b82f6)',
  anthropic: '#cc5a5a',
}

const Playground: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [prompt, setPrompt] = useState<Prompt | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [alert, setAlert] = useState<{
    type: 'success' | 'error'
    message: string
  } | null>(null)

  // Playground state
  const [promptContent, setPromptContent] = useState('')
  const [testInput, setTestInput] = useState('')
  const [expectedOutput, setExpectedOutput] = useState('')
  const [executing, setExecuting] = useState(false)

  // Availability status of providers
  const [providerStatus, setProviderStatus] = useState<
    Record<string, { available: boolean; reason: string }>
  >({})

  // Configs for the up to 3 comparison columns
  const [configs, setConfigs] = useState<PlaygroundConfig[]>([
    { provider: 'groq', model: 'llama-3.3-70b-versatile' },
    { provider: 'openai', model: 'gpt-4o' },
    { provider: 'ollama', model: 'mistral' },
  ])

  // Results for the 3 columns
  const [results, setResults] = useState<(PlaygroundColumnResult | null)[]>([
    null,
    null,
    null,
  ])
  const [savingIndex, setSavingIndex] = useState<number | null>(null)

  // Load initial prompt, version, and provider status using useApiData
  const {
    data: initData,
    loading: initLoading,
    error: initError,
  } = useApiData(async () => {
    if (!id) return null
    const [promptData, versionsData, statusData] = await Promise.all([
      apiClient.getPrompt(id),
      apiClient.getPromptVersions(id),
      apiClient.getProviderStatus(),
    ])
    return { promptData, versionsData, statusData }
  }, [id])

  useEffect(() => {
    if (initLoading) {
      setLoading(true)
      return
    }
    if (initError) {
      setError(initError)
      setLoading(false)
      return
    }
    if (initData) {
      setError(null)
      const { promptData, versionsData, statusData } = initData
      setPrompt(promptData)

      if (versionsData.items.length > 0) {
        const sorted = versionsData.items.sort((a, b) => b.version - a.version)
        setPromptContent(sorted[0].content)

        const latest = sorted[0]
        setConfigs([
          { provider: latest.provider, model: latest.model },
          {
            provider: latest.provider === 'openai' ? 'groq' : 'openai',
            model:
              latest.provider === 'openai'
                ? 'llama-3.3-70b-versatile'
                : 'gpt-4o',
          },
          { provider: 'ollama', model: 'mistral' },
        ])
      }
      setProviderStatus(statusData)
    }
    setLoading(false)
  }, [initData, initLoading, initError])

  const handleConfigChange = (
    index: number,
    key: keyof PlaygroundConfig,
    value: string
  ) => {
    const updated = [...configs]
    updated[index] = { ...updated[index], [key]: value }

    // If changing provider, auto-select the first available model for the new provider
    if (key === 'provider') {
      const models = DEFAULT_MODELS[value] || []
      updated[index].model = models[0] || ''
    }

    setConfigs(updated)
  }

  const handleExecute = async () => {
    if (!promptContent.trim()) {
      setAlert({
        type: 'error',
        message: 'O conteúdo do prompt não pode ser vazio.',
      })
      return
    }

    setExecuting(true)
    setAlert(null)
    // Pulse animation/Skeleton reset
    setResults([null, null, null])

    try {
      const activeConfigs = configs.slice(0, 3)
      const response = await apiClient.executePlayground({
        prompt_content: promptContent,
        input: testInput,
        expected: expectedOutput || undefined,
        configs: activeConfigs,
      })

      // Map back to 3 columns
      const updatedResults = [
        null,
        null,
        null,
      ] as (PlaygroundColumnResult | null)[]
      response.results.forEach((res, i) => {
        updatedResults[i] = res
      })

      setResults(updatedResults)
    } catch (err) {
      console.error('Playground execution failed:', err)
      setAlert({
        type: 'error',
        message:
          err instanceof Error
            ? err.message
            : 'Erro ao executar o teste paralelo.',
      })
    } finally {
      setExecuting(false)
    }
  }

  const handleSaveAsVersion = async () => {
    if (!id || !prompt) return

    // Pegando as configurações da Coluna A (índice 0) como referência principal para o Prompt
    const mainConfig = configs[0]

    try {
      setSavingIndex(0) // Mostra estado de loading

      await apiClient.createVersion(id, {
        content: promptContent,
        provider: mainConfig.provider,
        model: mainConfig.model,
      })

      setAlert({
        type: 'success',
        message: `Prompt salvo com sucesso como Nova Versão! (Configuração: ${mainConfig.provider} / ${mainConfig.model})`,
      })
    } catch (err) {
      console.error('Failed to save version:', err)
      setAlert({
        type: 'error',
        message:
          err instanceof Error
            ? err.message
            : 'Falha ao salvar o prompt como nova versão.',
      })
    } finally {
      setSavingIndex(null)
    }
  }

  if (loading)
    return <Loading message="Inicializando ambiente do Playground..." />
  if (error)
    return (
      <div className="playground-error">
        <Alert type="error" message={error} />
      </div>
    )
  if (!prompt)
    return (
      <div className="playground-error">
        <Alert type="error" message="Prompt não encontrado." />
      </div>
    )

  return (
    <>
      <Header />
      <div className="playground-container">
        <div className="playground-header-bar">
          <div className="back-nav">
            <button
              className="btn-back"
              onClick={() => navigate(`/prompts/${id}`)}
            >
              ← Voltar para {prompt.name}
            </button>
          </div>
          <div className="title-section">
            <h1>Playground Multi-Provedor A/B/C</h1>
            <p className="subtitle">
              Execute e compare a performance de diferentes modelos em tempo
              real
            </p>
          </div>
        </div>

        {alert && (
          <Alert
            type={alert.type}
            message={alert.message}
            onClose={() => setAlert(null)}
          />
        )}

        <div className="playground-workspace">
          {/* LEFT SIDEBAR: Prompt Editor & Configs */}
          <div className="playground-editor-panel">
            <div className="panel-section">
              <h3>1. Template do Prompt</h3>
              <textarea
                className="prompt-template-textarea"
                value={promptContent}
                onChange={(e) => setPromptContent(e.target.value)}
                placeholder="Insira o prompt aqui. Use {{variável}} para substituições dinâmicas."
                rows={10}
              />
              <small className="help-text">
                Dica: O SandboxAI renderiza este prompt usando{' '}
                <code>Jinja2</code>. Use <code>{'{{variavel}}'}</code> para
                colmatar campos dinâmicos.
              </small>
            </div>

            <div className="panel-section">
              <h3>2. Variáveis de Teste (Entrada JSON ou Texto)</h3>
              <textarea
                className="input-textarea"
                value={testInput}
                onChange={(e) => setTestInput(e.target.value)}
                placeholder='Ex: {"nome": "Maria", "produto": "Mesa"} ou apenas texto livre...'
                rows={4}
              />
            </div>

            <div className="panel-section">
              <h3>3. Saída Esperada (Opcional - Similaridade Semântica)</h3>
              <textarea
                className="expected-textarea"
                value={expectedOutput}
                onChange={(e) => setExpectedOutput(e.target.value)}
                placeholder="Insira a saída esperada para realizar validação semântica..."
                rows={3}
              />
            </div>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                className="btn-execute-playground"
                onClick={handleExecute}
                disabled={executing}
                style={{ flex: 1 }}
              >
                {executing ? (
                  <>
                    <span className="spinner-mini"></span> Processando
                    colunas...
                  </>
                ) : (
                  '🚀 Executar Teste A/B/C'
                )}
              </button>

              <button
                className="btn-save-version-top"
                onClick={handleSaveAsVersion}
                disabled={savingIndex !== null}
                style={{
                  flex: 1,
                  backgroundColor: 'var(--success-color, #10b981)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontWeight: 'bold',
                }}
              >
                {savingIndex !== null
                  ? '💾 Salvando...'
                  : '💾 Salvar como Nova Versão (Usando Coluna A)'}
              </button>
            </div>
          </div>

          {/* RIGHT VIEW: 3 Parallel Columns */}
          <div className="playground-comparison-view">
            {configs.map((config, index) => {
              const result = results[index]
              const isAvailable =
                providerStatus[config.provider]?.available ?? true
              const statusReason = providerStatus[config.provider]?.reason ?? ''
              const borderThemeColor =
                PROVIDER_COLORS[config.provider] || 'var(--primary-color)'

              return (
                <div
                  key={index}
                  className="comparison-column"
                  style={
                    {
                      '--column-theme-color': borderThemeColor,
                    } as React.CSSProperties
                  }
                >
                  {/* Column Config Header */}
                  <div className="column-config-header">
                    <span className="column-label">
                      Coluna {String.fromCharCode(65 + index)}
                    </span>
                    <div className="config-inputs">
                      <select
                        value={config.provider}
                        onChange={(e) =>
                          handleConfigChange(index, 'provider', e.target.value)
                        }
                        className="select-provider"
                      >
                        <option value="groq">Groq</option>
                        <option value="openai">OpenAI</option>
                        <option value="ollama">Ollama</option>
                        <option value="anthropic">Anthropic</option>
                      </select>

                      <select
                        value={config.model}
                        onChange={(e) =>
                          handleConfigChange(index, 'model', e.target.value)
                        }
                        className="select-model"
                      >
                        {(DEFAULT_MODELS[config.provider] || []).map(
                          (modelName) => (
                            <option key={modelName} value={modelName}>
                              {modelName}
                            </option>
                          )
                        )}
                      </select>
                    </div>

                    {!isAvailable && (
                      <div className="provider-offline-badge">
                        ⚠️ Indisponível: {statusReason}
                      </div>
                    )}
                  </div>

                  {/* Column Output Body */}
                  <div className="column-output-container">
                    {executing && !result ? (
                      <div className="column-skeleton-loader">
                        <div className="skeleton-line pulse"></div>
                        <div
                          className="skeleton-line pulse"
                          style={{ width: '80%' }}
                        ></div>
                        <div
                          className="skeleton-line pulse"
                          style={{ width: '90%' }}
                        ></div>
                        <div className="skeleton-pulse-circle pulse"></div>
                      </div>
                    ) : result ? (
                      <div className="column-result-content">
                        {/* Result Badges */}
                        <div className="result-badges-row">
                          <span className={`status-pill ${result.status}`}>
                            {result.status.toUpperCase()}
                          </span>

                          {result.is_correct !== null &&
                            result.is_correct !== undefined && (
                              <span
                                className={`validation-pill ${result.is_correct ? 'pass' : 'fail'}`}
                              >
                                {result.is_correct ? '✅ PASS' : '❌ FAIL'} (
                                {(result.score || 0).toFixed(2)})
                              </span>
                            )}
                        </div>

                        {/* Cost/Performance Glassmorphic Metrics */}
                        {result.status === 'completed' && (
                          <div className="column-metrics-grid">
                            <div className="metric-box">
                              <span className="metric-lbl">Latência</span>
                              <span className="metric-val">
                                {result.latency_ms.toFixed(0)}ms
                              </span>
                            </div>
                            <div className="metric-box">
                              <span className="metric-lbl">Tokens</span>
                              <span className="metric-val">
                                {result.tokens_used}
                              </span>
                            </div>
                            <div className="metric-box">
                              <span className="metric-lbl">Custo</span>
                              <span className="metric-val">
                                ${result.cost_usd.toFixed(6)}
                              </span>
                            </div>
                          </div>
                        )}

                        {/* Raw Output Block */}
                        <div className="output-scroll-box">
                          {result.status === 'completed' ? (
                            <pre className="output-raw-text">
                              {result.output}
                            </pre>
                          ) : (
                            <div className="error-display-box">
                              <h4>Falha na execução</h4>
                              <p>{result.error_message}</p>
                            </div>
                          )}
                        </div>

                        {/* Save Action moved to the top */}
                      </div>
                    ) : (
                      <div className="column-empty-state">
                        <span className="empty-icon">📊</span>
                        <p>Aguardando execução do teste A/B/C...</p>
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </>
  )
}

export default Playground
