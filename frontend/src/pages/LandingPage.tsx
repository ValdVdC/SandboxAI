import React, { useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import '../styles/LandingPage.css'

const LandingPage: React.FC = () => {
  const revealRefs = useRef<(HTMLElement | null)[]>([])

  useEffect(() => {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px',
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('reveal-visible')
        }
      })
    }, observerOptions)

    revealRefs.current.forEach((ref) => {
      if (ref) observer.observe(ref)
    })

    return () => observer.disconnect()
  }, [])

  const addToRefs = (el: HTMLElement | null) => {
    if (el && !revealRefs.current.includes(el)) {
      revealRefs.current.push(el)
    }
  }

  return (
    <div className="landing-page">
      {/* Background Decor */}
      <div className="bg-glow top-glow"></div>
      <div className="bg-grid"></div>

      {/* Hero Section */}
      <header className="hero reveal" ref={addToRefs}>
        <div className="eyebrow-container">
          <span className="eyebrow">A Nova Era da Engenharia de Prompts</span>
        </div>
        <h1>
          Domine seus LLMs com <span className="text-gradient">Dados</span>, não
          Sorte.
        </h1>
        <p className="hero-subtitle">
          A plataforma open-source para desenvolvedores que levam a sério a
          performance, o custo e a precisão de suas integrações com IA.
        </p>

        <div className="hero-actions">
          <Link to="/register" className="cta-button primary-glow">
            Comece Gratuitamente
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </Link>
          <div className="friction-hint">docker-compose up -d</div>
        </div>

        {/* Mockup Preview */}
        <div className="hero-mockup-container reveal" ref={addToRefs}>
          <div className="mockup-window">
            <div className="mockup-header">
              <span className="dot"></span>
              <span className="dot"></span>
              <span className="dot"></span>
            </div>
            <div className="mockup-content">
              <div className="mockup-sidebar"></div>
              <div className="mockup-main">
                <div className="mockup-card"></div>
                <div className="mockup-list">
                  <div className="mockup-line"></div>
                  <div className="mockup-line w-75"></div>
                  <div className="mockup-line w-50"></div>
                </div>
              </div>
            </div>
          </div>
          <div className="floating-badge badge-1">GPT-4 vs Llama 3</div>
          <div className="floating-badge badge-2">Latência: 450ms</div>
        </div>
      </header>

      {/* Bento Grid Features */}
      <section className="features-bento">
        <h2 className="section-title reveal" ref={addToRefs}>
          Tudo sob controle, em um só lugar.
        </h2>
        <div className="bento-grid">
          {/* Versionamento - Large (2x2) */}
          <div className="bento-card large reveal" ref={addToRefs}>
            <div className="card-top">
              <h3>Versionamento Estilo Git</h3>
              <p>
                Nunca mais perca aquele prompt que funcionava perfeitamente.
                Volte no tempo com um histórico visual completo de todas as
                alterações.
              </p>
            </div>
            <div className="card-visual"></div>
          </div>

          {/* Multi-Provedor - Medium (1x2) */}
          <div className="bento-card medium reveal" ref={addToRefs}>
            <div className="card-top">
              <h3>Multi-Provedor</h3>
              <p>
                Groq, OpenAI e Anthropic. Compare resultados lado a lado e
                escolha o modelo ideal para cada caso de uso.
              </p>
            </div>
            <div className="card-visual"></div>
          </div>

          {/* Bulk Testing - Full Width (2x1) */}
          <div className="bento-card full-width reveal" ref={addToRefs}>
            <div className="card-top">
              <h3>Bulk Testing Automatizado</h3>
              <p>
                Teste centenas de inputs e valide a qualidade das respostas em
                segundos, garantindo consistência em produção.
              </p>
            </div>
          </div>

          {/* Custo - Small (1x1) */}
          <div className="bento-card small reveal" ref={addToRefs}>
            <div className="card-top">
              <h3>Custo Real</h3>
              <p>
                Previsibilidade financeira total baseada no consumo real de
                tokens.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Trust Section */}
      <section className="trust reveal" ref={addToRefs}>
        <div className="trust-card">
          <h2>Privacidade é o nosso Padrão.</h2>
          <p>
            O SandboxAI é totalmente <strong>Self-Hosted</strong>. Seus prompts
            sensíveis e chaves de API nunca tocam nossos servidores. Você tem o
            controle total da sua infraestrutura e segurança.
          </p>
        </div>
      </section>

      {/* FAQ Modern */}
      <section className="faq-modern">
        <h2 className="section-title reveal" ref={addToRefs}>
          Perguntas Frequentes
        </h2>
        <div className="faq-grid">
          {[
            {
              q: 'Onde meus dados ficam?',
              a: 'No seu próprio banco de dados PostgreSQL dentro do seu container. Privacidade absoluta e controle total.',
            },
            {
              q: 'Quais modelos são suportados?',
              a: 'Suportamos nativamente OpenAI, Anthropic e todos os modelos de alta performance via Groq (Llama, Mixtral).',
            },
            {
              q: 'É complexo configurar?',
              a: 'Não. Um único comando Docker e toda a infraestrutura (API, Banco, Worker e Frontend) está pronta para rodar.',
            },
            {
              q: 'Posso comparar custos entre modelos?',
              a: 'Sim, calculamos o custo estimado em tempo real baseado no consumo de tokens de cada provedor.',
            },
          ].map((item, i) => (
            <div key={i} className="faq-card reveal" ref={addToRefs}>
              <h4>{item.q}</h4>
              <p>{item.a}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Final CTA */}
      <footer className="footer-cta reveal" ref={addToRefs}>
        <div className="footer-content">
          <h2>Pronto para profissionalizar sua IA?</h2>
          <Link
            to="/register"
            className="cta-button primary-glow"
            style={{ margin: '0 auto' }}
          >
            Comece Agora Gratuitamente
          </Link>
          <div className="footer-bottom">
            <p>
              &copy; {new Date().getFullYear()} SandboxAI - Open Source Prompt
              Engineering Dashboard.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage
