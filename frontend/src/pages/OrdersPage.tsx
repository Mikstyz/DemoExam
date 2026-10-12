import { useCallback, useEffect, useState } from 'react'
import { request } from '../api'
import { dateTime, localDateTime, money, roleKey } from '../utils'
import type { OrderDetail, OrderItem, OrderSummary, User } from '../types'

type OrdersPageProps = {
  user: User
  showError: (value: unknown) => void
  showNotice: (message: string) => void
}

export function OrdersPage({ user, showError, showNotice }: OrdersPageProps) {
  const role = roleKey(user.role)
  const isStaff = role === 'manager' || role === 'admin'
  const isAdmin = role === 'admin'
  const [orders, setOrders] = useState<OrderSummary[]>([])
  const [selectedOrder, setSelectedOrder] = useState<OrderDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [dateValue, setDateValue] = useState('')
  const [saving, setSaving] = useState(false)
  const [quantityDrafts, setQuantityDrafts] = useState<Record<number, string>>({})

  const loadOrders = useCallback(async () => {
    setLoading(true)
    try {
      const data = await request<OrderSummary[]>(isStaff ? '/api/orders' : '/api/orders/my', {}, user)
      setOrders(data)
    } catch (e) { showError(e) } finally { setLoading(false) }
  }, [isStaff, user.user_id])
  useEffect(() => { void loadOrders() }, [loadOrders])

  async function openOrder(orderId: number) {
    try {
      const data = await request<OrderDetail>(`/api/orders/${orderId}`, {}, user)
      setSelectedOrder(data)
      setDateValue(localDateTime(data.order_date))
      setQuantityDrafts(
        Object.fromEntries(
          data.items.map(item => [item.order_item_id, String(item.quantity)]),
        ),
      )
    } catch (e) { showError(e) }
  }
  async function deleteOrder(orderId: number) {
    if (!window.confirm(`Удалить заказ №${orderId}? Остатки товара будут восстановлены.`)) return
    try {
      await request(`/api/orders/${orderId}`, { method: 'DELETE' }, user)
      setSelectedOrder(null); showNotice(`Заказ №${orderId} удалён`); await loadOrders()
    } catch (e) { showError(e) }
  }
  async function saveDate() {
    if (!selectedOrder || !dateValue) return
    setSaving(true)
    try {
      const updated = await request<OrderSummary>(
        `/api/orders/${selectedOrder.order_id}/date`,
        { method: 'PATCH', body: JSON.stringify({ order_date: dateValue }) },
        user,
      )
      setSelectedOrder(prev => prev ? { ...prev, order_date: updated.order_date } : prev)
      showNotice('Дата заказа изменена'); await loadOrders()
    } catch (e) { showError(e) } finally { setSaving(false) }
  }
  async function deleteItem(itemId: number) {
    if (!selectedOrder || !window.confirm('Удалить позицию из заказа? Остаток будет восстановлен.')) return
    try {
      await request(`/api/orders/${selectedOrder.order_id}/items/${itemId}`, { method: 'DELETE' }, user)
      await openOrder(selectedOrder.order_id); await loadOrders(); showNotice('Позиция удалена')
    } catch (e) { showError(e) }
  }
  async function updateQuantity(item: OrderItem, quantity: number) {
    if (!selectedOrder || quantity < 1 || quantity === item.quantity) return
    try {
      const updated = await request<OrderDetail>(
        `/api/orders/${selectedOrder.order_id}/items/${item.order_item_id}?quantity=${quantity}`,
        { method: 'PATCH' },
        user,
      )
      setSelectedOrder(updated)
      setQuantityDrafts(
        Object.fromEntries(
          updated.items.map(row => [row.order_item_id, String(row.quantity)]),
        ),
      )
      await loadOrders()
      showNotice('Количество обновлено')
    } catch (error) {
      showError(error)
      setQuantityDrafts(prev => ({
        ...prev,
        [item.order_item_id]: String(item.quantity),
      }))
    }
  }

  return (
    <main className="page-content">
      <div className="page-heading">
        <div>
          <span className="eyebrow">ЗАКАЗЫ</span>
          <h1>{isStaff ? 'Все заказы' : 'Мои заказы'}</h1>
          <p className="muted">Дата, клиент, состав и итоговая стоимость заказа.</p>
        </div>
      </div>

      <div className="orders-layout">
        <section className="orders-list panel">
          {loading ? (
            <div className="empty-state">Загружаем заказы…</div>
          ) : orders.length === 0 ? (
            <div className="empty-state">Заказов пока нет.</div>
          ) : (
            orders.map(order => (
              <button
                key={order.order_id}
                className={`order-row ${
                  selectedOrder?.order_id === order.order_id ? 'selected' : ''
                }`}
                onClick={() => void openOrder(order.order_id)}
              >
                <span className="order-number">
                  Заказ №{order.order_id}
                  <small>{dateTime(order.order_date)}</small>
                </span>
                <span className="order-customer">{order.customer_full_name}</span>
                <strong>{money(order.total)}</strong>
              </button>
            ))
          )}
        </section>

        <section className="order-detail panel">
          {!selectedOrder ? (
            <div className="empty-state">
              Выберите заказ слева, чтобы посмотреть состав.
            </div>
          ) : (
            <>
              <div className="section-heading">
                <div>
                  <span className="eyebrow">ЗАКАЗ №{selectedOrder.order_id}</span>
                  <h2>Состав заказа</h2>
                </div>
                {isStaff && (
                  <button
                    className="button button-danger"
                    onClick={() => void deleteOrder(selectedOrder.order_id)}
                  >
                    Удалить заказ
                  </button>
                )}
              </div>

              <div className="order-meta">
                <div>
                  <span>Клиент</span>
                  <strong>{selectedOrder.customer_full_name}</strong>
                </div>
                <div>
                  <span>Дата заказа</span>
                  <strong>{dateTime(selectedOrder.order_date)}</strong>
                </div>
                <div>
                  <span>Итого</span>
                  <strong className="current-price">{money(selectedOrder.total)}</strong>
                </div>
              </div>

              {isAdmin && (
                <div className="edit-date">
                  <label>
                    <span>Изменить дату заказа</span>
                    <input
                      type="datetime-local"
                      value={dateValue}
                      onChange={event => setDateValue(event.target.value)}
                    />
                  </label>
                  <button
                    className="button button-secondary"
                    onClick={() => void saveDate()}
                    disabled={saving}
                  >
                    {saving ? 'Сохраняем…' : 'Сохранить дату'}
                  </button>
                </div>
              )}

              <div className="order-items">
                {selectedOrder.items.length === 0 ? (
                  <p className="muted">В заказе не осталось позиций.</p>
                ) : (
                  selectedOrder.items.map(item => (
                    <div className="order-item" key={item.order_item_id}>
                      <div className="order-item-name">
                        <strong>{item.product_name}</strong>
                        <span className="muted">
                          {item.manufacturer} · размер {item.size_value}
                        </span>
                        <small>{money(item.price)} за пару</small>
                      </div>

                      {isAdmin ? (
                        <label className="item-quantity">
                          <span>Количество</span>
                          <input
                            aria-label={`Количество ${item.product_name}`}
                            type="number"
                            min="1"
                            value={quantityDrafts[item.order_item_id] ?? String(item.quantity)}
                            onChange={event =>
                              setQuantityDrafts(prev => ({
                                ...prev,
                                [item.order_item_id]: event.target.value,
                              }))
                            }
                            onBlur={() =>
                              void updateQuantity(
                                item,
                                Number(quantityDrafts[item.order_item_id] ?? item.quantity),
                              )
                            }
                          />
                        </label>
                      ) : (
                        <span className="item-count">{item.quantity} пар</span>
                      )}

                      <strong>{money(item.line_total)}</strong>
                      {isAdmin && (
                        <button
                          className="text-button danger-text"
                          onClick={() => void deleteItem(item.order_item_id)}
                        >
                          Удалить позицию
                        </button>
                      )}
                    </div>
                  ))
                )}
              </div>

              <div className="order-total-row">
                <span>Итоговая стоимость</span>
                <strong>{money(selectedOrder.total)}</strong>
              </div>
            </>
          )}
        </section>
      </div>

      {isStaff && (
        <p className="hint">
          Менеджер и администратор могут удалять заказы. Только администратор
          может менять дату, количество и удалять отдельные позиции.
        </p>
      )}
    </main>
  )
}
