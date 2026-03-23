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
  const chatEndRef = useRef(null)
  const textareaRef = useRef(null)

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
        localStorage.setItem('session_id', data.session_id)
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

  return (
    <div className="app">
      {/* Chat area */}
      <div className="chat-container">
        {messages.length === 0 ? (
          // Welcome screen
          <div className="welcome">
            <h1>Agent Hub</h1>
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
                <path d="M22 2L11 13M22 2L15 22L11 13L2 9L22 2Z" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
