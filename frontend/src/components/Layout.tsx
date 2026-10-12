import type { FormEvent } from 'react'
import type { Page, User } from '../types'
import { fullName, roleKey } from '../utils'

type HeaderProps = {
  user: User | null
  page: Page
  setPage: (page: Page) => void
  logout: () => void
}

export function Header({ user, page, setPage, logout }: HeaderProps) {
  const role = roleKey(user?.role)

  return (
    <header className="site-header">
      <div className="brand-row">
        <img className="store-image" src="/images/store-image.png" alt="Чудо Обувь" />
        <div className="brand-copy">
          <div className="brand-title">Чудо Обувь</div>
          <div className="brand-subtitle">Каталог и оформление заказов</div>
        </div>
      </div>

      <nav className="nav-tabs" aria-label="Основная навигация">
        <button className={page === 'main' ? 'nav-tab active' : 'nav-tab'} onClick={() => setPage('main')}>
          Каталог
        </button>
        {user && (
          <button className={page === 'orders' ? 'nav-tab active' : 'nav-tab'} onClick={() => setPage('orders')}>
            Заказы
          </button>
        )}
      </nav>

      <div className="account-box">
        {user ? (
          <>
            <div className="account-name">
              {fullName(user)}
              <span className="role-label">
                {role === 'admin' ? 'Администратор' : role === 'manager' ? 'Менеджер' : 'Пользователь'}
              </span>
            </div>
            <button className="button button-plain" onClick={logout}>Выйти</button>
          </>
        ) : (
          <button className="button button-primary" onClick={() => setPage('login')}>Войти</button>
        )}
      </div>
    </header>
  )
}

type LoginPageProps = {
  login: string
  setLogin: (value: string) => void
  onSubmit: (event: FormEvent) => void
  busy: boolean
  onBrowse: () => void
}

export function LoginPage({ login, setLogin, onSubmit, busy, onBrowse }: LoginPageProps) {
  return (
    <main className="login-page">
      <div className="login-banner">
        <img src="/images/store-image.png" alt="" />
        <div>
          <span className="eyebrow">МАГАЗИН ОБУВИ</span>
          <h1>Чудо Обувь</h1>
          <p>Выберите подходящую пару и оформите заказ.</p>
        </div>
      </div>

      <form className="login-card" onSubmit={onSubmit}>
        <h2>Вход в систему</h2>
        <p className="muted">Введите логин из списка пользователей. Пароль не требуется.</p>
        <label htmlFor="login">Логин</label>
        <input
          id="login"
          autoComplete="username"
          value={login}
          onChange={event => setLogin(event.target.value)}
          placeholder="Например, ivanov"
          required
          autoFocus
        />
        <button className="button button-primary button-wide" type="submit" disabled={busy}>
          {busy ? 'Входим…' : 'Войти'}
        </button>
        <button className="button button-plain button-wide" type="button" onClick={onBrowse}>
          Смотреть каталог без входа
        </button>
      </form>
    </main>
  )
}
