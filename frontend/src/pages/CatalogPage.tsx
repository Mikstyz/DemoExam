import { useCallback, useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { API_URL, apiErrorMessage, request } from '../api'
import { imageUrl, money, roleKey } from '../utils'
import type {
  CartLine,
  Category,
  Product,
  ProductDetail,
  ProductForm,
  OrderDetail,
  Subcategory,
  User,
} from '../types'

type CatalogPageProps = {
  user: User | null
  onLogin: () => void
  showError: (value: unknown) => void
  showNotice: (message: string) => void
}

const blankProductForm: ProductForm = {
  category_id: '',
  subcategory_id: '',
  product_name: '',
  manufacturer: '',
  description: '',
  composition: '',
  price: '',
}

export function CatalogPage({ user, onLogin, showError, showNotice }: CatalogPageProps) {
  const role = roleKey(user?.role)
  const canEdit = role === 'manager' || role === 'admin'
  const [products, setProducts] = useState<Product[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [subcategories, setSubcategories] = useState<Subcategory[]>([])
  const [formSubcategories, setFormSubcategories] = useState<Subcategory[]>([])
  const [search, setSearch] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [subcategoryId, setSubcategoryId] = useState('')
  const [sort, setSort] = useState('')
  const [loading, setLoading] = useState(true)
  const [cart, setCart] = useState<CartLine[]>([])
  const [expanded, setExpanded] = useState<Record<number, ProductDetail | null>>({})
  const [selectedSizes, setSelectedSizes] = useState<Record<number, number>>({})
  const [quantities, setQuantities] = useState<Record<number, number>>({})
  const [editing, setEditing] = useState<ProductDetail | 'new' | null>(null)
  const [productForm, setProductForm] = useState<ProductForm>(blankProductForm)
  const [isCheckingOut, setCheckingOut] = useState(false)
  const [isSavingProduct, setSavingProduct] = useState(false)

  const loadProducts = useCallback(async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (categoryId) params.set('category_id', categoryId)
      if (subcategoryId) params.set('subcategory_id', subcategoryId)
      if (search.trim()) params.set('search', search.trim())
      if (sort) params.set('sort', sort)
      const data = await request<Product[]>(`/api/products${params.size ? `?${params}` : ''}`, {}, user)
      setProducts(data)
    } catch (e) { showError(e) } finally { setLoading(false) }
  }, [categoryId, subcategoryId, search, sort, user?.user_id])

  useEffect(() => { void loadProducts() }, [loadProducts])
  useEffect(() => {
    request<Category[]>('/api/categories', {}, user).then(setCategories).catch(showError)
  }, [user?.user_id])

  useEffect(() => {
    setSubcategoryId('')
    if (!categoryId) {
      setSubcategories([])
      return
    }
    const params = new URLSearchParams({ category_id: categoryId })
    request<Subcategory[]>(`/api/subcategories?${params}`, {}, user)
      .then(items => {
        const unique = new Map<string, Subcategory>()
        for (const item of items) {
          const key = item.name.trim().replace(/\s+/g, ' ').toLocaleLowerCase('ru-RU')
          if (!unique.has(key)) unique.set(key, item)
        }
        setSubcategories([...unique.values()])
      })
      .catch(showError)
  }, [categoryId, user?.user_id])

  useEffect(() => {
    const selectedCategory = productForm.category_id
    if (!selectedCategory) {
      setFormSubcategories([])
      return
    }
    request<Subcategory[]>(`/api/subcategories?category_id=${encodeURIComponent(selectedCategory)}`, {}, user)
      .then(items => {
        const unique = new Map<string, Subcategory>()
        for (const item of items) {
          const key = item.name.trim().replace(/\s+/g, ' ').toLocaleLowerCase('ru-RU')
          if (!unique.has(key)) unique.set(key, item)
        }
        setFormSubcategories([...unique.values()])
      })
      .catch(showError)
  }, [productForm.category_id, user?.user_id])

  const cartTotal = cart.reduce((sum, line) => sum + Number(line.product.discounted_price) * line.quantity, 0)
  const cartCount = cart.reduce((sum, line) => sum + line.quantity, 0)

  async function toggleDetails(product: Product) {
    if (expanded[product.product_id]) { setExpanded(prev => ({ ...prev, [product.product_id]: null })); return }
    try {
      const detail = await request<ProductDetail>(`/api/products/${product.product_id}`, {}, user)
      setExpanded(prev => ({ ...prev, [product.product_id]: detail }))
      const available = detail.sizes.find(s => s.quantity_available > 0)
      if (available) setSelectedSizes(prev => ({ ...prev, [product.product_id]: prev[product.product_id] || available.size_id }))
    } catch (e) { showError(e) }
  }

  function addToCart(product: Product, detail: ProductDetail | null) {
    const sizeId = selectedSizes[product.product_id]
    const size = detail?.sizes.find(s => s.size_id === sizeId)
    const quantity = Math.max(1, Number(quantities[product.product_id] || 1))
    if (!size || size.quantity_available < 1) { showError('Выберите доступный размер'); return }
    const already = cart.find(line => line.product.product_id === product.product_id && line.size_id === size.size_id)?.quantity || 0
    if (already + quantity > size.quantity_available) { showError(`Для размера ${size.size_value} доступно ${size.quantity_available} пар`); return }
    setCart(prev => {
      const found = prev.find(line => line.product.product_id === product.product_id && line.size_id === size.size_id)
      if (found) return prev.map(line => line === found ? { ...line, quantity: line.quantity + quantity } : line)
      return [...prev, { product, size_id: size.size_id, size_value: size.size_value, quantity }]
    })
    showNotice(`${product.product_name} добавлен в корзину`)
  }

  function changeCartQuantity(index: number, quantity: number) {
    if (quantity <= 0) { setCart(prev => prev.filter((_, i) => i !== index)); return }
    setCart(prev => prev.map((line, i) => i === index ? { ...line, quantity } : line))
  }

  async function checkout() {
    if (!user) { onLogin(); showNotice('Войдите по логину, чтобы оформить заказ.'); return }
    if (!cart.length) return
    setCheckingOut(true)
    try {
      const result = await request<OrderDetail>('/api/orders', {
        method: 'POST',
        body: JSON.stringify({
          items: cart.map(line => ({
            product_id: line.product.product_id,
            size_id: line.size_id,
            quantity: line.quantity,
          })),
        }),
      }, user)
      const orderedProductIds = [...new Set(cart.map(line => line.product.product_id))]
      setCart([])
      showNotice(`Заказ №${result.order_id} оформлен`)
      await loadProducts()
      const refreshedDetails = await Promise.all(
        orderedProductIds.map(async productId => {
          try {
            return [productId, await request<ProductDetail>(`/api/products/${productId}`, {}, user)] as const
          } catch (error) {
            showError(error)
            return [productId, null] as const
          }
        }),
      )
      setExpanded(prev => {
        const next = { ...prev }
        for (const [productId, detail] of refreshedDetails) {
          if (detail) next[productId] = detail
        }
        return next
      })
    } catch (e) { showError(e) } finally { setCheckingOut(false) }
  }

  function openProductEditor(product?: ProductDetail) {
    if (product) {
      setEditing(product)
      setProductForm({
        category_id: String(product.category_id), subcategory_id: product.subcategory_id ? String(product.subcategory_id) : '',
        product_name: product.product_name, manufacturer: product.manufacturer,
        description: product.description || '', composition: product.composition || '', price: String(product.price),
      })
    } else {
      setEditing('new'); setProductForm({ ...blankProductForm, category_id: categories[0] ? String(categories[0].category_id) : '' })
    }
  }

  async function uploadProductImage(productId: number, file: File) {
    const form = new FormData()
    form.append('image', file)
    const headers = new Headers()
    if (user) headers.set('X-User-ID', String(user.user_id))
    const response = await fetch(`${API_URL}/api/products/${productId}/image`, { method: 'POST', headers, body: form })
    const text = await response.text()
    let data: unknown = null
    try { data = text ? JSON.parse(text) : null } catch { data = text }
    if (!response.ok) throw new Error(apiErrorMessage(data) || `Ошибка HTTP ${response.status}`)
  }

  async function saveProduct(event: FormEvent) {
    event.preventDefault()
    setSavingProduct(true)
    const imageInput = document.getElementById('product-image') as HTMLInputElement | null
    const imageFile = imageInput?.files?.[0] || null
    if (editing === 'new' && !imageFile) { showError('Выберите изображение товара'); setSavingProduct(false); return }
    const body = {
      category_id: Number(productForm.category_id), subcategory_id: productForm.subcategory_id ? Number(productForm.subcategory_id) : null,
      product_name: productForm.product_name.trim(), manufacturer: productForm.manufacturer.trim(),
      description: productForm.description.trim() || null, composition: productForm.composition.trim() || null, price: Number(productForm.price),
    }
    let keepEditorOpen = false
    try {
      if (editing === 'new') {
        const created = await request<ProductDetail>('/api/products', { method: 'POST', body: JSON.stringify(body) }, user)
        setEditing(created)
        keepEditorOpen = true
        if (imageFile) { await uploadProductImage(created.product_id, imageFile); if (imageInput) imageInput.value = '' }
        const detail = await request<ProductDetail>(`/api/products/${created.product_id}`, {}, user)
        setEditing(detail)
        showNotice('Карточка создана. Теперь можно добавить размеры и остатки ниже.')
      } else if (editing) {
        await request<ProductDetail>(`/api/products/${editing.product_id}`, { method: 'PATCH', body: JSON.stringify(body) }, user)
        if (imageFile) { await uploadProductImage(editing.product_id, imageFile); if (imageInput) imageInput.value = '' }
        showNotice('Карточка товара сохранена')
      }
      if (!keepEditorOpen) setEditing(null)
      await loadProducts()
    } catch (error) {
      showError(error)
      await loadProducts()
    } finally {
      setSavingProduct(false)
    }
  }

  async function deleteProduct(product: Product) {
    if (!window.confirm(`Удалить товар «${product.product_name}»?`)) return
    try {
      await request(`/api/products/${product.product_id}`, { method: 'DELETE' }, user)
      showNotice('Товар удалён'); await loadProducts()
    } catch (e) { showError(e) }
  }

  async function saveStock(productId: number, sizeId: number, quantity: number) {
    try {
      await request(`/api/products/${productId}/stock/${sizeId}`, { method: 'PUT', body: JSON.stringify({ quantity_available: quantity }) }, user)
      const detail = await request<ProductDetail>(`/api/products/${productId}`, {}, user)
      setExpanded(prev => ({ ...prev, [productId]: detail }))
      await loadProducts(); showNotice('Остаток сохранён')
    } catch (e) { showError(e) }
  }

  async function saveStockByValue(productId: number, sizeValue: string, quantity: number) {
    try {
      await request(
        `/api/products/${productId}/stock/by-value`,
        {
          method: 'PUT',
          body: JSON.stringify({
            size_value: sizeValue,
            quantity_available: quantity,
          }),
        },
        user,
      )
      const detail = await request<ProductDetail>(`/api/products/${productId}`, {}, user)
      setExpanded(prev => ({ ...prev, [productId]: detail }))
      setEditing(detail)
      await loadProducts(); showNotice(`Размер ${sizeValue} сохранён`)
    } catch (e) { showError(e) }
  }

  return (
    <main className="page-content">
      <div className="page-heading">
        <div>
          <span className="eyebrow">КАТАЛОГ</span>
          <h1>Обувь в наличии</h1>
          <p className="muted">Выберите модель, размер и количество пар.</p>
        </div>
        {canEdit && (
          <button
            className="button button-primary"
            onClick={() => openProductEditor()}
          >
            + Добавить товар
          </button>
        )}
      </div>

      <section className="filters panel">
        <label className="search-field">
          <span>Поиск</span>
          <input
            value={search}
            onChange={event => setSearch(event.target.value)}
            placeholder="Название или описание"
          />
        </label>

        <label>
          <span>Категория</span>
          <select
            value={categoryId}
            onChange={event => {
              setCategoryId(event.target.value)
              setSubcategoryId('')
            }}
          >
            <option value="">Все категории</option>
            {categories.map(category => (
              <option key={category.category_id} value={category.category_id}>
                {category.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          <span>Подкатегория</span>
          <select
            value={subcategoryId}
            disabled={!categoryId}
            onChange={event => setSubcategoryId(event.target.value)}
          >
            <option value="">
              {categoryId ? 'Все подкатегории' : 'Сначала выберите категорию'}
            </option>
            {subcategories.map(subcategory => (
              <option
                key={subcategory.subcategory_id}
                value={subcategory.subcategory_id}
              >
                {subcategory.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          <span>Сортировка</span>
          <select value={sort} onChange={event => setSort(event.target.value)}>
            <option value="">По названию</option>
            <option value="price_asc">Сначала дешевле</option>
            <option value="price_desc">Сначала дороже</option>
          </select>
        </label>
      </section>

      {user && cart.length > 0 && (
        <section className="cart-panel panel">
          <div className="section-heading">
            <div>
              <h2>Корзина</h2>
              <p className="muted">
                Позиций: {cart.length} · Пар: {cartCount}
              </p>
            </div>
            <strong className="cart-total">{money(cartTotal)}</strong>
          </div>

          <div className="cart-lines">
            {cart.map((line, index) => (
              <div
                className="cart-line"
                key={`${line.product.product_id}-${line.size_id}`}
              >
                <div className="cart-line-title">
                  <strong>{line.product.product_name}</strong>
                  <span className="muted">Размер {line.size_value}</span>
                </div>

                <div className="quantity-control">
                  <button
                    onClick={() => changeCartQuantity(index, line.quantity - 1)}
                    aria-label="Уменьшить количество"
                  >
                    −
                  </button>
                  <span>{line.quantity}</span>
                  <button
                    onClick={() => changeCartQuantity(index, line.quantity + 1)}
                    aria-label="Увеличить количество"
                  >
                    +
                  </button>
                </div>

                <strong>
                  {money(Number(line.product.discounted_price) * line.quantity)}
                </strong>
                <button
                  className="text-button danger-text"
                  onClick={() => changeCartQuantity(index, 0)}
                >
                  Убрать
                </button>
              </div>
            ))}
          </div>

          <div className="cart-actions">
            <span className="muted">
              Остаток будет проверен при оформлении заказа.
            </span>
            <button
              className="button button-primary"
              onClick={checkout}
              disabled={isCheckingOut}
            >
              {isCheckingOut ? 'Оформляем…' : 'Оформить заказ'}
            </button>
          </div>
        </section>
      )}

      {editing && (
        <section className="editor-panel panel">
          <div className="section-heading">
            <h2>
              {editing === 'new' ? 'Новый товар' : 'Редактирование товара'}
            </h2>
            <button
              className="button button-plain"
              onClick={() => setEditing(null)}
            >
              Закрыть
            </button>
          </div>

          <form className="product-form" onSubmit={saveProduct}>
            <label>
              <span>Название</span>
              <input
                required
                value={productForm.product_name}
                onChange={event =>
                  setProductForm({
                    ...productForm,
                    product_name: event.target.value,
                  })
                }
              />
            </label>

            <label>
              <span>Производитель</span>
              <input
                required
                value={productForm.manufacturer}
                onChange={event =>
                  setProductForm({
                    ...productForm,
                    manufacturer: event.target.value,
                  })
                }
              />
            </label>

            <label>
              <span>Категория</span>
              <select
                required
                value={productForm.category_id}
                onChange={event =>
                  setProductForm({
                    ...productForm,
                    category_id: event.target.value,
                    subcategory_id: '',
                  })
                }
              >
                <option value="">Выберите</option>
                {categories.map(category => (
                  <option
                    key={category.category_id}
                    value={category.category_id}
                  >
                    {category.name}
                  </option>
                ))}
              </select>
            </label>

            <label>
              <span>Подкатегория</span>
              <select
                value={productForm.subcategory_id}
                onChange={event =>
                  setProductForm({
                    ...productForm,
                    subcategory_id: event.target.value,
                  })
                }
              >
                <option value="">Без подкатегории</option>
                {formSubcategories.map(subcategory => (
                  <option
                    key={subcategory.subcategory_id}
                    value={subcategory.subcategory_id}
                  >
                    {subcategory.name}
                  </option>
                ))}
              </select>
            </label>

            <label>
              <span>Цена, ₽</span>
              <input
                required
                type="number"
                min="0.01"
                step="0.01"
                value={productForm.price}
                onChange={event =>
                  setProductForm({
                    ...productForm,
                    price: event.target.value,
                  })
                }
              />
            </label>

            <label>
              <span>Изображение товара{editing === 'new' ? ' *' : ''}</span>
              <input
                id="product-image"
                type="file"
                accept="image/png,image/jpeg,image/webp,image/gif"
                required={editing === 'new'}
              />
              <small>
                JPG, PNG, WEBP или GIF, до 10 МБ. Файл сохранится на backend.
              </small>
              {editing !== 'new' && editing.image_path && (
                <small>
                  Текущее изображение: {editing.image_path.split('/').pop()}
                </small>
              )}
            </label>

            <label className="span-two">
              <span>Описание</span>
              <textarea
                rows={2}
                value={productForm.description}
                onChange={event =>
                  setProductForm({
                    ...productForm,
                    description: event.target.value,
                  })
                }
              />
            </label>

            <label className="span-two">
              <span>Состав</span>
              <input
                value={productForm.composition}
                onChange={event =>
                  setProductForm({
                    ...productForm,
                    composition: event.target.value,
                  })
                }
              />
            </label>

            <div className="form-actions span-two">
              <button className="button button-primary" disabled={isSavingProduct}>
                {isSavingProduct ? 'Сохраняем…' : 'Сохранить товар'}
              </button>
              <button
                type="button"
                className="button button-plain"
                onClick={() => setEditing(null)}
              >
                Отмена
              </button>
            </div>
          </form>

          {editing !== 'new' && (
            <StockEditor
              key={editing.product_id}
              product={editing}
              onSave={saveStock}
              onSaveByValue={saveStockByValue}
            />
          )}
        </section>
      )}

      {loading ? (
        <div className="empty-state">Загружаем каталог…</div>
      ) : products.length === 0 ? (
        <div className="empty-state">По вашему запросу ничего не найдено.</div>
      ) : (
        <section className="product-list" aria-label="Каталог товаров">
          {products.map(product => {
            const detail = expanded[product.product_id] || null
            const selected = detail?.sizes.find(
              size => size.size_id === selectedSizes[product.product_id],
            )

            return (
              <article
                className={`product-card ${product.low_stock ? 'low-stock' : ''}`}
                key={product.product_id}
              >
                <div className="product-image-wrap">
                  <img
                    src={imageUrl(product.image_path)}
                    alt={product.product_name}
                    onError={event => {
                      event.currentTarget.onerror = null
                      event.currentTarget.src = '/images/picture.png'
                    }}
                  />
                </div>

                <div className="product-info">
                  <div className="product-category">
                    {product.category}
                    {product.subcategory ? ` / ${product.subcategory}` : ''}
                  </div>
                  <h2>{product.product_name}</h2>
                  <div className="muted">
                    Производитель: {product.manufacturer}
                  </div>

                  {product.description && (
                    <p className="product-description">{product.description}</p>
                  )}
                  {product.composition && (
                    <p className="product-composition">
                      <span>Состав:</span> {product.composition}
                    </p>
                  )}

                  <div className="stock-line">
                    <span>Всего доступно:</span>
                    <strong className={product.low_stock ? 'stock-warning' : ''}>
                      {product.total_quantity} пар
                    </strong>
                    {product.low_stock && (
                      <span className="stock-badge">Мало на складе</span>
                    )}
                  </div>

                  {detail && (
                    <div className="size-picker">
                      <label>
                        <span>Размер</span>
                        <select
                          value={selectedSizes[product.product_id] || ''}
                          onChange={event =>
                            setSelectedSizes(prev => ({
                              ...prev,
                              [product.product_id]: Number(event.target.value),
                            }))
                          }
                        >
                          <option value="">Выберите размер</option>
                          {detail.sizes.map(size => (
                            <option
                              key={size.size_id}
                              value={size.size_id}
                              disabled={size.quantity_available < 1}
                            >
                              {size.size_value} · в наличии {size.quantity_available}
                            </option>
                          ))}
                        </select>
                      </label>

                      <label className="quantity-field">
                        <span>Количество</span>
                        <input
                          type="number"
                          min="1"
                          max={selected?.quantity_available || 1}
                          value={quantities[product.product_id] || 1}
                          onChange={event =>
                            setQuantities(prev => ({
                              ...prev,
                              [product.product_id]: Math.max(
                                1,
                                Number(event.target.value) || 1,
                              ),
                            }))
                          }
                        />
                      </label>
                    </div>
                  )}

                  {canEdit && (
                    <div className="product-admin-actions">
                      <button
                        className="text-button"
                        onClick={async () => {
                          const productDetail =
                            detail ||
                            (await request<ProductDetail>(
                              `/api/products/${product.product_id}`,
                              {},
                              user,
                            ).catch(error => {
                              showError(error)
                              return null
                            }))
                          if (productDetail) openProductEditor(productDetail)
                        }}
                      >
                        Редактировать карточку / остатки
                      </button>
                      <button
                        className="text-button danger-text"
                        onClick={() => deleteProduct(product)}
                      >
                        Удалить
                      </button>
                    </div>
                  )}
                </div>

                <div className="product-buy">
                  <div className="price-block">
                    {product.discount_percent > 0 && (
                      <div className="old-price">{money(product.price)}</div>
                    )}
                    <div className="current-price">
                      {money(product.discounted_price)}
                    </div>
                    {product.discount_percent > 0 && (
                      <span className="discount-badge">
                        −{product.discount_percent}%
                      </span>
                    )}
                  </div>

                  {!detail ? (
                    <button
                      className="button button-primary"
                      onClick={() => void toggleDetails(product)}
                    >
                      Выбрать размер
                    </button>
                  ) : !user ? (
                    <button className="button button-primary" onClick={onLogin}>
                      Войти для заказа
                    </button>
                  ) : (
                    <button
                      className="button button-primary"
                      onClick={() => addToCart(product, detail)}
                      disabled={!selected || selected.quantity_available < 1}
                    >
                      В корзину
                    </button>
                  )}
                  {detail && (
                    <button
                      className="button button-plain"
                      onClick={() => void toggleDetails(product)}
                    >
                      Скрыть размеры
                    </button>
                  )}
                </div>
              </article>
            )
          })}
        </section>
      )}
    </main>
  )
}

function StockEditor({
  product,
  onSave,
  onSaveByValue,
}: {
  product: ProductDetail
  onSave: (productId: number, sizeId: number, quantity: number) => Promise<void>
  onSaveByValue: (productId: number, sizeValue: string, quantity: number) => Promise<void>
}) {
  const [stockValues, setStockValues] = useState<Record<number, string>>(() =>
    Object.fromEntries(
      product.sizes.map(size => [size.size_id, String(size.quantity_available)]),
    ),
  )
  const [sizeValue, setSizeValue] = useState('')
  const [quantity, setQuantity] = useState('0')

  return (
    <div className="stock-editor">
      <h3>Остатки по размерам</h3>

      {product.sizes.length ? (
        product.sizes.map(size => (
          <div className="stock-edit-row" key={size.size_id}>
            <span>Размер {size.size_value}</span>
            <input
              aria-label={`Количество размера ${size.size_value}`}
              type="number"
              min="0"
              value={stockValues[size.size_id] ?? String(size.quantity_available)}
              onChange={event =>
                setStockValues(prev => ({
                  ...prev,
                  [size.size_id]: event.target.value,
                }))
              }
            />
            <button
              type="button"
              className="button button-secondary"
              onClick={() =>
                void onSave(
                  product.product_id,
                  size.size_id,
                  Number(stockValues[size.size_id]),
                )
              }
            >
              Сохранить
            </button>
          </div>
        ))
      ) : (
        <p className="muted">У товара пока нет размеров. Добавьте первый размер ниже.</p>
      )}

      <form
        className="stock-add-row"
        onSubmit={event => {
          event.preventDefault()
          const value = sizeValue.trim()
          if (value && Number(quantity) >= 0) {
            void onSaveByValue(product.product_id, value, Number(quantity))
            setSizeValue('')
          }
        }}
      >
        <label>
          <span>Размер</span>
          <input
            required
            maxLength={50}
            value={sizeValue}
            onChange={event => setSizeValue(event.target.value)}
            placeholder="Например, 38 или 38.5"
          />
        </label>
        <label>
          <span>Количество</span>
          <input
            required
            type="number"
            min="0"
            max="1000000"
            value={quantity}
            onChange={event => setQuantity(event.target.value)}
          />
        </label>
        <button className="button button-secondary">Добавить / изменить размер</button>
      </form>
    </div>
  )
}
