import React from 'react'
import { useParams } from 'react-router-dom'
import Header from '../components/Header'
import TestRunner from '../components/TestRunner'
import TestResults from '../components/TestResults'
import Loading from '../components/Loading'
import { useState, useEffect } from 'react'
import apiClient from '../services/api'
import { PromptVersion } from '../types'
import '../styles/TestExecution.css'

const TestExecution: React.FC = () => {
  const { promptId } = useParams<{ promptId: string }>()
  const [activeTest, setActiveTest] = useState<string | null>(null)
  const [versions, setVersions] = useState<PromptVersion[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchVersions = async () => {
      if (!promptId) return
      try {
        setLoading(true)
        const response = await apiClient.getPromptVersions(promptId)
        const sorted = response.items.sort((a, b) => b.version - a.version)
        setVersions(sorted)
      } catch (err) {
        setError(
          err instanceof Error ? err.message : 'Failed to fetch versions'
        )
      } finally {
        setLoading(false)
      }
    }

    fetchVersions()
  }, [promptId])

  if (!promptId) return <div>Prompt not found</div>
  if (loading) return <Loading message="Carregando versões..." />
  if (error) return <div className="error-message">{error}</div>
  if (versions.length === 0)
    return (
      <div className="error-message">
        Nenhuma versão encontrada para este prompt
      </div>
    )

  const latestVersion = versions[0]

  return (
    <>
      <Header />
      <div className="test-execution-page">
        <div className="test-container">
          {activeTest ? (
            <TestResults
              promptId={promptId}
              versionNumber={latestVersion.version}
              testId={activeTest}
              autoRefresh={true}
              onBack={() => setActiveTest(null)}
            />
          ) : (
            <>
              <h1>Executar Teste - v{latestVersion.version}</h1>
              <TestRunner
                promptId={promptId}
                versionNumber={latestVersion.version}
                onTestStarted={setActiveTest}
              />
            </>
          )}
        </div>
      </div>
    </>
  )
}

export default TestExecution
