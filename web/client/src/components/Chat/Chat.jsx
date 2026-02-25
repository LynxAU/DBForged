import React, { useState, useRef, useEffect } from 'react'

/**
 * Chat - Chat window with command input
 */
export function Chat({ messages, onSendCommand }) {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = (e) => {
    e.preventDefault()
    const cmd = input.trim()
    if (cmd) {
      onSendCommand(cmd)
      setInput('')
    }
  }

  return (
    <div className="glass-panel chat-panel">
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`chat-message ${msg.type}`}>
            <span 
              dangerouslySetInnerHTML={{ 
                __html: msg.text.replace(/\n/g, '<br/>') 
              }} 
            />
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <form onSubmit={handleSubmit} className="chat-input-container">
        <input
          type="text"
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter command..."
          autoFocus
        />
      </form>
    </div>
  )
}

export default Chat
