import React, { useState } from 'react'

export default function App() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [answer, setAnswer] = useState(null)
  const [sources, setSources] = useState([])
  const [error, setError] = useState(null)

  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setAnswer(null)
    setSources([])

    try {
      const resp = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      })

      if (!resp.ok) {
        const text = await resp.text()
        throw new Error(`${resp.status} ${text}`)
      }

      const data = await resp.json()
      setAnswer(data.answer || data.response || '')
      setSources(data.sources || data.chunks || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header>
        <h1>Chatbot Univ Lille</h1>
      </header>

      <main>
        <form onSubmit={handleSubmit} className="query-form">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Posez votre question..."
            rows={4}
          />
          <button type="submit" disabled={loading || !query.trim()}>
            {loading ? 'Recherche...' : 'Envoyer'}
          </button>
        </form>

        {error && <div className="error">Erreur: {error}</div>}

        {answer && (
          <section className="answer">
            <h2>Réponse</h2>
            <p>{answer}</p>
          </section>
        )}

        {sources && sources.length > 0 && (
          <section className="sources">
            <h3>Sources / Chunks récupérés</h3>
            <ul>
              {sources.map((s, i) => (
                <li key={i}>
                  <pre>{typeof s === 'string' ? s : JSON.stringify(s, null, 2)}</pre>
                </li>
              ))}
            </ul>
          </section>
        )}
      </main>
    </div>
  )
}
