import { API_URL } from './api'
import type { User } from './types'

export function roleKey(role: string | undefined): string {
  const normalized = (role || '').trim().toLocaleLowerCase('ru-RU')
  if (['admin', 'administrator', 'администратор'].includes(normalized)) return 'admin'
  if (['manager', 'менеджер'].includes(normalized)) return 'manager'
  return 'user'
}

export function fullName(user: User): string {
  return [user.last_name, user.first_name, user.middle_name].filter(Boolean).join(' ')
}

export function money(value: number | string): string {
  return `${Number(value || 0).toLocaleString('ru-RU', {
    maximumFractionDigits: 2,
    minimumFractionDigits: 2,
  })} ₽`
}

export function dateTime(value: string): string {
  return new Date(value).toLocaleString('ru-RU', {
    dateStyle: 'short',
    timeStyle: 'short',
  })
}

export function localDateTime(value: string): string {
  const date = new Date(value)
  const offset = date.getTimezoneOffset()
  return new Date(date.getTime() - offset * 60_000).toISOString().slice(0, 16)
}

export function imageUrl(path: string | null | undefined): string {
  if (!path) return '/images/picture.png'
  if (/^https?:\/\//i.test(path)) return path
  if (path.startsWith('/media/')) return `${API_URL}${path}`
  if (path.startsWith('/images/products/')) {
    return `${API_URL}/media/products/${path.split('/').pop() || 'picture.png'}`
  }
  if (path.startsWith('/')) return `${API_URL}${path}`

  const filename = path.split(/[\\/]/).pop()
  return `${API_URL}/media/products/${filename || 'picture.png'}`
}
