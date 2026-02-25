import { useState, useRef, useEffect } from 'react'

/**
 * Sanitize Evennia HTML output to only allow safe color spans and line breaks.
 * Strips everything else to prevent XSS from injected event handlers or tags.
 * Allowed: <span style="color:..."> <br> plain text
 */
const SAFE_COLOR_RE = /^color:\s*(?:#[0-9a-fA-F]{3,8}|rgba?\([^)]{1,60}\)|[a-zA-Z]{2,32})$/

const sanitizeGameHtml = (html) => {
  if (!html) return ''
  // Replace <br/> and <br> variants before parsing so they survive
  const withBr = html.replace(/<br\s*\/?>/gi, '\x00BR\x00')
  const tmp = document.createElement('div')
  tmp.innerHTML = withBr
  const walk = (node, buf) => {
    if (node.nodeType === Node.TEXT_NODE) {
      buf.push(node.textContent
        .replace(/\x00BR\x00/g, '<br>')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;'))
      return
    }
    if (node.nodeType !== Node.ELEMENT_NODE) return
    const tag = node.tagName.toLowerCase()
    if (tag === 'span') {
      const style = (node.getAttribute('style') || '').trim()
      if (SAFE_COLOR_RE.test(style)) {
        buf.push(`<span style="${style}">`)
        node.childNodes.forEach(c => walk(c, buf))
        buf.push('</span>')
        return
      }
    }
    // Unwrap any other element — recurse into children
    node.childNodes.forEach(c => walk(c, buf))
  }
  const out = []
  tmp.childNodes.forEach(c => walk(c, out))
  return out.join('').replace(/\x00BR\x00/g, '<br>')
}

export function Chat({ messages, onSendCommand }) {
  const [input, setInput]   = useState('')
  const endRef              = useRef(null)
  const inputRef            = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const submit = (e) => {
    e.preventDefault()
    const cmd = input.trim()
    if (!cmd) return
    onSendCommand(cmd)
    setInput('')
  }

  return (
    <div className="terminal-chat">
      {/* Header bar */}
      <div className="terminal-chat-header">
        <div className="terminal-chat-dot" />
        <div className="terminal-chat-title">Command Terminal</div>
      </div>

      {/* Message stream */}
      <div className="terminal-messages">
        {messages.map((msg) => (
          <div key={msg.id ?? Math.random()} className={`terminal-msg ${msg.type ?? 'text'}`}>
            <span
              dangerouslySetInnerHTML={{
                __html: sanitizeGameHtml(msg.content?.html ?? msg.content ?? '')
              }}
            />
          </div>
        ))}
        <div ref={endRef} />
      </div>

      {/* Input */}
      <form onSubmit={submit} className="terminal-input-row">
        <div className="terminal-prompt">►</div>
        <input
          ref={inputRef}
          type="text"
          className="terminal-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter command…"
          autoFocus
          spellCheck={false}
          autoComplete="off"
        />
      </form>
    </div>
  )
}

export default Chat
