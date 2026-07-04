/**
 * AI Chatbot Page — Multi-turn agriculture expert assistant
 */

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useChatSessions, useChatMessages, useSendMessage } from '../../api/hooks'
import { chatAPI } from '../../api'
import type { ChatMessage, ChatSession } from '../../types'

const SUGGESTED_QUESTIONS = [
  "What's the best fertilizer for paddy in kharif season?",
  "My tomato leaves have yellow spots — what disease is this?",
  "How much water does cotton need per week?",
  "What government schemes are available for small farmers?",
  "When is the best time to sell onions in Tamil Nadu?",
  "How to improve soil pH for wheat?",
]

function TypingIndicator() {
  return (
    <div style={{ display: 'flex', gap: '4px', padding: '12px 16px', alignItems: 'center' }}>
      {[0, 1, 2].map(i => (
        <div key={i} className="typing-dot" style={{ animationDelay: `${i * 0.2}s` }} />
      ))}
    </div>
  )
}

function MessageBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === 'user'
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      style={{ display: 'flex', flexDirection: isUser ? 'row-reverse' : 'row', gap: '10px', alignItems: 'flex-end' }}
    >
      <div style={{ width: '32px', height: '32px', borderRadius: '50%', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px', background: isUser ? 'var(--gradient-primary)' : 'var(--bg-card)', border: '1px solid var(--border)' }}>
        {isUser ? '👤' : '🤖'}
      </div>
      <div style={{ maxWidth: '75%' }}>
        <div className={`chat-bubble ${isUser ? 'chat-bubble-user' : 'chat-bubble-ai'}`}
          style={{ whiteSpace: 'pre-wrap' }}>
          {msg.content}
        </div>
        {!isUser && msg.confidence && (
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px', paddingLeft: '4px' }}>
            🤖 Confidence: {Math.round(msg.confidence * 100)}%
          </div>
        )}
        <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px', paddingLeft: '4px', textAlign: isUser ? 'right' : 'left' }}>
          {new Date(msg.created_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </motion.div>
  )
}

export default function ChatbotPage() {
  const [activeSessionId, setActiveSessionId] = useState<number | null>(null)
  const [inputText, setInputText] = useState('')
  const [language, setLanguage] = useState<'en' | 'ta'>('en')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const { data: sessions, refetch: refetchSessions } = useChatSessions()
  const { data: messages } = useChatMessages(activeSessionId ?? 0)
  const sendMutation = useSendMessage()

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  const handleNewSession = async () => {
    const res = await chatAPI.createSession('New Conversation', language)
    const session = res.data.data
    if (session) {
      setActiveSessionId(session.id)
      refetchSessions()
    }
  }

  const handleSend = async () => {
    if (!inputText.trim() || !activeSessionId) return
    const text = inputText.trim()
    setInputText('')
    setIsTyping(true)
    try {
      await sendMutation.mutateAsync({ sessionId: activeSessionId, content: text, language })
    } finally {
      setIsTyping(false)
    }
  }

  const handleSuggestion = async (q: string) => {
    if (!activeSessionId) {
      const res = await chatAPI.createSession('New Conversation', language)
      const session = res.data.data
      if (!session) return
      setActiveSessionId(session.id)
      await refetchSessions()
      setIsTyping(true)
      try {
        await sendMutation.mutateAsync({ sessionId: session.id, content: q, language })
      } finally {
        setIsTyping(false)
      }
      return
    }
    setInputText(q)
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr', gap: '24px', height: 'calc(100vh - 120px)' }}>
      {/* Sessions Sidebar */}
      <div className="card" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px', overflow: 'hidden' }}>
        <button id="new-chat-btn" className="btn btn-primary" style={{ width: '100%' }} onClick={handleNewSession}>
          + New Chat
        </button>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            className={`btn ${language === 'en' ? 'btn-primary' : 'btn-secondary'} btn-sm`}
            style={{ flex: 1 }}
            onClick={() => setLanguage('en')}
          >🇬🇧 English</button>
          <button
            className={`btn ${language === 'ta' ? 'btn-primary' : 'btn-secondary'} btn-sm`}
            style={{ flex: 1 }}
            onClick={() => setLanguage('ta')}
          >🇮🇳 Tamil</button>
        </div>

        <div style={{ overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {sessions?.map((s: ChatSession) => (
            <button
              key={s.id}
              onClick={() => setActiveSessionId(s.id)}
              style={{
                width: '100%', textAlign: 'left', padding: '10px 12px',
                borderRadius: '10px', border: `1px solid ${activeSessionId === s.id ? 'var(--primary)' : 'var(--border)'}`,
                background: activeSessionId === s.id ? 'var(--primary-glow)' : 'transparent',
                cursor: 'pointer', transition: 'all 0.15s',
              }}
            >
              <div style={{ fontSize: '13px', fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: 'var(--text-primary)' }}>
                💬 {s.title}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                {new Date(s.created_at).toLocaleDateString('en-IN')}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Chat Window */}
      <div className="card" style={{ padding: 0, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Chat Header */}
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'var(--gradient-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px' }}>🤖</div>
          <div>
            <div style={{ fontWeight: 700 }}>ROOTGS AI Assistant</div>
            <div style={{ fontSize: '12px', color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--success)' }} />
              Online • Agriculture Expert
            </div>
          </div>
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {!activeSessionId ? (
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', gap: '20px' }}>
              <div style={{ fontSize: '64px' }}>🌾</div>
              <h3>Ask ROOTGS AI Anything</h3>
              <p style={{ color: 'var(--text-muted)', maxWidth: '400px' }}>
                Your personal agriculture expert is ready to help with crop diseases, weather advisories, fertilizers, government schemes, and more.
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', width: '100%', maxWidth: '500px' }}>
                {SUGGESTED_QUESTIONS.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => handleSuggestion(q)}
                    style={{
                      padding: '12px', borderRadius: '10px', border: '1px solid var(--border)',
                      background: 'var(--bg)', cursor: 'pointer', fontSize: '13px',
                      textAlign: 'left', color: 'var(--text-secondary)', transition: 'all 0.15s',
                    }}
                    onMouseEnter={e => { e.currentTarget.style.background = 'var(--primary-glow)'; e.currentTarget.style.borderColor = 'var(--primary)'; }}
                    onMouseLeave={e => { e.currentTarget.style.background = 'var(--bg)'; e.currentTarget.style.borderColor = 'var(--border)'; }}
                  >
                    💬 {q}
                  </button>
                ))}
              </div>
              <button id="start-chat-btn" className="btn btn-primary btn-lg" onClick={handleNewSession}>
                Start New Conversation
              </button>
            </div>
          ) : (
            <>
              {messages?.map((msg: ChatMessage) => (
                <MessageBubble key={msg.id} msg={msg} />
              ))}
              {isTyping && (
                <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-end' }}>
                  <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'var(--bg-card)', border: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px' }}>🤖</div>
                  <div className="chat-bubble chat-bubble-ai" style={{ padding: '8px 12px' }}>
                    <TypingIndicator />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input */}
        {activeSessionId && (
          <div style={{ padding: '16px', borderTop: '1px solid var(--border)', display: 'flex', gap: '12px', alignItems: 'flex-end' }}>
            <textarea
              id="chat-input"
              value={inputText}
              onChange={e => setInputText(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
              placeholder={language === 'ta' ? 'உங்கள் கேள்வியை இங்கே தட்டச்சு செய்யுங்கள்...' : 'Ask about crops, diseases, weather, schemes... (Enter to send)'}
              className="input"
              style={{ flex: 1, resize: 'none', minHeight: '44px', maxHeight: '120px', lineHeight: 1.5, padding: '10px 14px' }}
              rows={1}
            />
            <button
              id="send-btn"
              className="btn btn-primary btn-icon"
              onClick={handleSend}
              disabled={!inputText.trim() || sendMutation.isPending}
              style={{ width: '44px', height: '44px', flexShrink: 0 }}
            >
              {sendMutation.isPending ? '⏳' : '➤'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
