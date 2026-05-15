import http from 'node:http'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const __dirname = dirname(fileURLToPath(import.meta.url))

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

  if (req.method === 'OPTIONS') {
    res.writeHead(204)
    res.end()
    return
  }

  console.log(`${req.method} ${req.url}`)

  if (req.method === 'POST' && req.url === '/api/documents/upload') {
    let body = ''
    req.on('data', chunk => body += chunk)
    req.on('end', () => {
      res.writeHead(200, { 'Content-Type': 'application/json' })
      res.end(JSON.stringify({ document_id: 'doc-123' }))
    })
    return
  }

  if (req.method === 'POST' && req.url?.match(/^\/api\/documents\/.+\/generate$/)) {
    res.writeHead(200, { 'Content-Type': 'application/json' })
    res.end(JSON.stringify({
      review: `# Title Review: Chain of Assignments - Mortgage History\n\n## Summary\n\nThis document details the chain of assignments for a mortgage history.\n\n## Key Observations\n\n- Assignment 1: Transferred from Original Lender to Bank A on 2019-03-15\n- Assignment 2: Transferred from Bank A to Bank B on 2021-08-01\n- Assignment 3: Transferred from Bank B to Current Servicer on 2023-01-10\n\n## Issues Identified\n\n1. **Gap in Assignment Chain**: There appears to be a gap between 2020-02-01 and 2020-11-15 where no assignment was recorded.\n2. **Missing Notarization**: Assignment 2 lacks proper notarization stamps.\n\n## Recommendation\n\nReview the chain for completeness and ensure all assignments are properly notarized and recorded.`
    }))
    return
  }

  if (req.method === 'PUT' && req.url?.match(/^\/api\/documents\/.+\/review$/)) {
    res.writeHead(200, { 'Content-Type': 'application/json' })
    res.end(JSON.stringify({ status: 'saved' }))
    return
  }

  if (req.method === 'POST' && req.url === '/api/chat') {
    let body = ''
    req.on('data', chunk => body += chunk)
    req.on('end', () => {
      const { message } = JSON.parse(body)
      res.writeHead(200, { 'Content-Type': 'application/json' })
      res.end(JSON.stringify({
        response: `Regarding your query: "${message}"\n\nBased on the document, I would suggest focusing on the chain of title completeness and ensuring all assignments follow proper recording procedures.`
      }))
    })
    return
  }

  if (req.method === 'GET' && req.url === '/api/chat/history') {
    res.writeHead(200, { 'Content-Type': 'application/json' })
    res.end(JSON.stringify({ messages: [] }))
    return
  }

  res.writeHead(404)
  res.end()
})

server.listen(8000, () => {
  console.log('Mock API server on http://localhost:8000')
})
