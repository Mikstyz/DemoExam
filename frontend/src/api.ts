import type { User } from './types'

export const API_URL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')
export const USER_KEY = 'chudo-obuv-user'

export function savedUser(): User | null {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY) || 'null') as User | null
  } catch {
    return null
  }
}

export function apiErrorMessage(body: unknown): string {
  if (typeof body === 'string') return body
  if (body && typeof body === 'object' && 'detail' in body) {
    const detail = (body as { detail: unknown }).detail
    if (typeof detail === 'string') return detail
    return JSON.stringify(detail)
  }
  return 'Не удалось выполнить запрос'
}

export async function request<T>(
  path: string,
  options: RequestInit = {},
  user?: User | null,
): Promise<T> {
  const headers = new Headers(options.headers)
  if (options.body && !(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const activeUser = user === undefined ? savedUser() : user
  if (activeUser) headers.set('X-User-ID', String(activeUser.user_id))

  const response = await fetch(`${API_URL}${path}`, { ...options, headers })
  const responseText = await response.text()
  let data: unknown = null

  if (responseText) {
    try {
      data = JSON.parse(responseText)
    } catch {
      data = responseText
    }
  }

  if (!response.ok) {
    throw new Error(apiErrorMessage(data) || `Ошибка HTTP ${response.status}`)
  }

  return data as T
}
