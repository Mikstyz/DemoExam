// Все HTTP-запросы к backend находятся в одном месте.
import { messageFrom } from './utils.js';

export function createApi(getUser) {
  return async function request(path, options = {}, user = getUser()) {
    const headers = new Headers(options.headers || {});

    if (options.body && !(options.body instanceof FormData) && !headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }
    if (user?.user_id) headers.set('X-User-ID', String(user.user_id));

    const response = await fetch(path, { ...options, headers });
    const raw = await response.text();
    let data = null;

    if (raw) {
      try {
        data = JSON.parse(raw);
      } catch {
        data = raw;
      }
    }

    if (!response.ok) throw new Error(messageFrom(data) || `Ошибка HTTP ${response.status}`);
    return data;
  };
}
