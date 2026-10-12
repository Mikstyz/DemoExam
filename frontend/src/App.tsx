import { useState } from 'react'
import type { FormEvent } from 'react'
import { request, savedUser, USER_KEY } from './api'
import { Header, LoginPage } from './components/Layout'
import { CatalogPage } from './pages/CatalogPage'
import { OrdersPage } from './pages/OrdersPage'
import { fullName } from './utils'
import type { Page, User } from './types'

export default function App() {
  const [user, setUser] = useState<User | null>(() => savedUser())
  const [page, setPage] = useState<Page>(() => savedUser() ? 'main' : 'login')
  const [notice, setNotice] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [login, setLogin] = useState('')

  function showError(value: unknown) {
    setError(value instanceof Error ? value.message : 'Произошла ошибка')
    setNotice('')
  }

  function showNotice(message: string) {
    setNotice(message)
    setError('')
  }

  async function handleLogin(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError('')

    try {
      const nextUser = await request<User>(
        '/api/auth/login',
        { method: 'POST', body: JSON.stringify({ login: login.trim() }) },
        null,
      )
      localStorage.setItem(USER_KEY, JSON.stringify(nextUser))
      setUser(nextUser)
      setPage('main')
      setLogin('')
      showNotice(`Вход выполнен: ${fullName(nextUser)}`)
    } catch (error) {
      showError(error)
    } finally {
      setBusy(false)
    }
  }

  function logout() {
    localStorage.removeItem(USER_KEY)
    setUser(null)
    setPage('main')
    setError('')
    setNotice('')
  }

  return (
    <div className="app-shell">
      {page !== 'login' && (
        <Header user={user} page={page} setPage={setPage} logout={logout} />
      )}

      {error && (
        <div className="message message-error" role="alert">
          <span>{error}</span>
          <button className="message-close" onClick={() => setError('')} aria-label="Закрыть сообщение">×</button>
        </div>
      )}
      {notice && (
        <div className="message message-success" role="status">
          <span>{notice}</span>
          <button className="message-close" onClick={() => setNotice('')} aria-label="Закрыть сообщение">×</button>
        </div>
      )}

      {page === 'login' ? (
        <LoginPage
          login={login}
          setLogin={setLogin}
          onSubmit={handleLogin}
          busy={busy}
          onBrowse={() => setPage('main')}
        />
      ) : page === 'main' ? (
        <CatalogPage
          user={user}
          onLogin={() => setPage('login')}
          showError={showError}
          showNotice={showNotice}
        />
      ) : user ? (
        <OrdersPage user={user} showError={showError} showNotice={showNotice} />
      ) : (
        <LoginPage
          login={login}
          setLogin={setLogin}
          onSubmit={handleLogin}
          busy={busy}
          onBrowse={() => setPage('main')}
        />
      )}

      <footer className="footer">Чудо Обувь · учебный проект</footer>
    </div>
  )
}
