export type ChatResult = Record<string, unknown>

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
  })
  if (!response.ok) throw new Error(`请求失败（${response.status}）`)
  return response.json() as Promise<T>
}

export function chat(message: string, conversationId?: string): Promise<ChatResult> {
  return request<ChatResult>('/api/v1/chat', {
    method: 'POST', body: JSON.stringify({ message, conversation_id: conversationId }),
  })
}

export function propose(action: string, arguments_: Record<string, unknown>): Promise<ChatResult> {
  return request<ChatResult>('/api/v1/tools/propose', {
    method: 'POST', body: JSON.stringify({ action, arguments: arguments_ }),
  })
}

export function decide(approvalId: string, decision: 'approved' | 'rejected'): Promise<ChatResult> {
  return request<ChatResult>(`/api/v1/approvals/${approvalId}/decision`, {
    method: 'POST', body: JSON.stringify({ decision, operator: 'console-user' }),
  })
}

export function listApprovals(): Promise<ChatResult[]> {
  return request<ChatResult[]>('/api/v1/approvals')
}

export function auditEvents(): Promise<ChatResult[]> {
  return request<ChatResult[]>('/api/v1/approvals/audit/events')
}

export async function uploadMarkdown(file: File): Promise<ChatResult> {
  const response = await fetch(`${API_BASE}/api/v1/knowledge/markdown`, {
    method: 'POST', headers: { 'Content-Type': 'text/markdown', 'x-filename': file.name }, body: await file.text(),
  })
  if (!response.ok) throw new Error(`上传失败（${response.status}）`)
  return response.json() as Promise<ChatResult>
}
