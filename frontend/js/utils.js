// Общие функции интерфейса: форматирование и подготовка данных для вывода.

export function readSavedUser() {
  try {
    return JSON.parse(localStorage.getItem('chudo-obuv-user') || 'null');
  } catch {
    return null;
  }
}

export function roleKey(role) {
  const value = String(role || '').trim().toLocaleLowerCase('ru-RU');
  if (['admin', 'administrator', 'администратор'].includes(value)) return 'admin';
  if (['manager', 'менеджер'].includes(value)) return 'manager';
  return 'user';
}

export function fullName(user) {
  return [user.last_name, user.first_name, user.middle_name].filter(Boolean).join(' ');
}

export function money(value) {
  return `${Number(value || 0).toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ₽`;
}

export function dateTime(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Дата не указана';
  return date.toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' });
}

export function localDateTime(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
}

export function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
}

export function imageUrl(path) {
  if (!path) return '/images/picture.png';
  if (/^https?:\/\//i.test(path) || path.startsWith('/')) return path;
  return `/media/products/${encodeURIComponent(path.split(/[\\/]/).pop())}`;
}

export function messageFrom(body) {
  if (typeof body === 'string') return body;
  if (body && typeof body === 'object' && 'detail' in body) {
    return typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail);
  }
  return 'Не удалось выполнить запрос';
}
