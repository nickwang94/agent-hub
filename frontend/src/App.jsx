import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import './App.css'

// API Configuration
const API_BASE_URL = 'http://localhost:8080'

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [sessions, setSessions] = useState([])
  const [currentSessionId, setCurrentSessionId] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const chatEndRef = useRef(null)
  const textareaRef = useRef(null)

  // Load sessions on mount
  useEffect(() => {
    fetchSessions()
    const savedSessionId = localStorage.getItem('session_id')
    if (savedSessionId) {
      setCurrentSessionId(savedSessionId)
    }
  }, [])

  // Auto scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // Auto adjust textarea height
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px'
    }
  }, [input])

  // Fetch sessions list
  const fetchSessions = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/sessions`)
      setSessions(response.data.sessions || [])
    } catch (err) {
      console.error('Error fetching sessions:', err)
    }
  }

  // Create new session
  const createNewSession = () => {
    setMessages([])
    setCurrentSessionId(null)
    localStorage.removeItem('session_id')
    setError(null)
  }

  // Load session messages
  const loadSession = async (sessionId) => {
    try {
      // Fetch session with messages from backend
      const response = await axios.get(`${API_BASE_URL}/sessions/${sessionId}`)

      if (response.data.session) {
        const session = response.data.session
        // Load messages from the session
        const messages = session.messages.map(msg => ({
          role: msg.role,
          content: msg.content
        }))
        setMessages(messages)
        setCurrentSessionId(sessionId)
        localStorage.setItem('session_id', sessionId)
        setError(null)
      }
    } catch (err) {
      console.error('Error loading session:', err)
      // If failed to load, still switch to the session
      setCurrentSessionId(sessionId)
      localStorage.setItem('session_id', sessionId)
      setMessages([])
    }
  }

  // Delete session
  const deleteSession = async (sessionId, e) => {
    e.stopPropagation()
    try {
      await axios.delete(`${API_BASE_URL}/sessions/${sessionId}`)

      // If deleting current session, create a new one
      if (sessionId === currentSessionId) {
        createNewSession()
      }

      // Refresh sessions list
      fetchSessions()
    } catch (err) {
      console.error('Error deleting session:', err)
      alert('Failed to delete session')
    }
  }

  // Send message
  const sendMessage = async (message = input) => {
    if (!message.trim()) return

    const userMessage = { role: 'user', content: message.trim() }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)
    setError(null)

    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message: message.trim(),
        session_id: localStorage.getItem('session_id') || null
      })

      const data = response.data
      if (data.session_id) {
        const newSessionId = data.session_id
        localStorage.setItem('session_id', newSessionId)
        setCurrentSessionId(newSessionId)
        // Refresh sessions list to update the session
        fetchSessions()
      }

      setMessages(prev => [...prev, { role: 'assistant', content: data.response }])
    } catch (err) {
      setError(err.message || 'Failed to send. Please check if the backend server is running.')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  // Handle key press
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  // Suggested questions
  const suggestions = [
    { title: 'Greeting', text: 'Hello, introduce yourself' },
    { title: 'Ask a question', text: 'What can you help me with?' },
    { title: 'Learn programming', text: 'How to learn Python?' },
    { title: 'Chat', text: 'Nice weather today, let\'s chat' },
  ]

  // Format session date
  const formatDate = (timestamp) => {
    const date = new Date(timestamp * 1000)
    const now = new Date()
    const diff = now - date

    if (diff < 60000) return 'Just now'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
    return date.toLocaleDateString()
  }

  return (
    <div className="app">
      {/* Sidebar overlay for mobile */}
      {sidebarOpen && (
        <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h2 className="sidebar-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="sidebar-icon">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            Agent Hub
          </h2>
          <button className="sidebar-toggle-mobile" onClick={() => setSidebarOpen(false)}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <button className="new-chat-button" onClick={createNewSession}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          New Chat
        </button>

        <div className="sessions-list">
          <div className="sessions-header">
            <span>Recent Sessions</span>
            <button className="refresh-button" onClick={fetchSessions} title="Refresh">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M23 4v6h-6M1 20v-6h6"/>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
              </svg>
            </button>
          </div>

          {sessions.length === 0 ? (
            <div className="no-sessions">
              <p>No sessions yet</p>
              <p className="no-sessions-hint">Start a conversation!</p>
            </div>
          ) : (
            sessions.map((session) => (
              <div
                key={session.id}
                className={`session-item ${session.id === currentSessionId ? 'active' : ''}`}
                onClick={() => loadSession(session.id)}
              >
                <div className="session-info">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="session-icon">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                  </svg>
                  <div className="session-details">
                    <span className="session-name">
                      {session.messages?.[0]?.content?.slice(0, 30) || 'New Chat'}
                      {session.messages?.[0]?.content?.length > 30 ? '...' : ''}
                    </span>
                    <span className="session-time">{formatDate(session.updated_at)}</span>
                  </div>
                </div>
                <button
                  className="delete-session-button"
                  onClick={(e) => deleteSession(session.id, e)}
                  title="Delete session"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                  </svg>
                </button>
              </div>
            ))
          )}
        </div>
      </aside>

      {/* Main chat area */}
      <main className={`main-content ${sidebarOpen ? '' : 'sidebar-closed'}`}>
        {/* Header */}
        <header className="main-header">
          <button className="menu-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 12h18M3 6h18M3 18h18"/>
            </svg>
          </button>
          <h1 className="main-title">Agent Hub</h1>
        </header>

        {/* Chat container */}
        <div className="chat-container">
          {messages.length === 0 ? (
            // Welcome screen
            <div className="welcome">
              <h1>Agent Hub</h1>
              <p className="welcome-subtitle">Your AI-powered multi-agent assistant</p>
              <div className="suggestions">
                {suggestions.map((item, index) => (
                  <div
                    key={index}
                    className="suggestion"
                    onClick={() => sendMessage(item.text)}
                  >
                    <div className="suggestion-title">{item.title}</div>
                    <div className="suggestion-text">{item.text}</div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            // Message list
            <>
              {messages.map((msg, index) => (
                <div key={index} className={`message ${msg.role}`}>
                  <div className="message-content">
                    <div className={`avatar ${msg.role}`}>
                      {msg.role === 'user' ? 'You' : 'AI'}
                    </div>
                    <div className="message-text">{msg.content}</div>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="message assistant">
                  <div className="message-content">
                    <div className="avatar assistant">AI</div>
                    <div className="message-text">
                      <div className="typing">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              {error && (
                <div className="error-message">{error}</div>
              )}
              <div ref={chatEndRef} />
            </>
          )}
        </div>

        {/* Input area */}
        <div className="input-container">
          <div className="input-wrapper">
            <div className="input-box">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Send a message to AI assistant..."
                rows={1}
              />
              <button
                className="send-button"
                onClick={() => sendMessage()}
                disabled={loading || !input.trim()}
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 2L11 13M22 2L15 22L11 13L2 9L2 22Z" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
