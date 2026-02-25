import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const STATIC_DIR = path.resolve(__dirname, '../static')

const MIME = {
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif':  'image/gif',
  '.svg':  'image/svg+xml',
  '.webp': 'image/webp',
  '.ico':  'image/x-icon',
  '.css':  'text/css',
  '.js':   'application/javascript',
  '.json': 'application/json',
  '.woff': 'font/woff',
  '.woff2':'font/woff2',
}

/** Serve web/static/ at /static/ during development */
const staticMiddleware = {
  name: 'evennia-static',
  configureServer(server) {
    server.middlewares.use('/static', (req, res, next) => {
      // Decode URL-encoded characters (e.g., %20 for spaces)
      const decodedUrl = decodeURIComponent(req.url.split('?')[0])
      const filePath = path.join(STATIC_DIR, decodedUrl)
      try {
        const stat = fs.statSync(filePath)
        if (stat.isFile()) {
          const ext  = path.extname(filePath).toLowerCase()
          const mime = MIME[ext] || 'application/octet-stream'
          res.setHeader('Content-Type', mime)
          res.setHeader('Cache-Control', 'no-cache')
          res.end(fs.readFileSync(filePath))
          return
        }
      } catch (_) {}
      next()
    })
  },
}

export default defineConfig({
  plugins: [react(), staticMiddleware],
  server: {
    port: 3000,
    proxy: {
      // Game — Evennia WebSocket server on port 4002
      '/webclient': { target: 'http://localhost:4002', changeOrigin: true, ws: true },
      // Future backend services (no backends yet)
      '/ws/combat': { target: 'http://localhost:5001', changeOrigin: true, ws: true },
      '/ws/world':  { target: 'http://localhost:5002', changeOrigin: true, ws: true },
      '/ws/chat':   { target: 'http://localhost:5003', changeOrigin: true, ws: true },
      // Note: /static is served by staticMiddleware above, not proxied
    }
  }
})
