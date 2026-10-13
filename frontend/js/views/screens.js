/* Отрисовка экранов. Здесь только HTML-шаблоны и представление данных. */
export function createViews(context) {
  const { state, app, header, messages, roleKey, isStaff, isAdmin, fullName, money, dateTime, localDateTime, escapeHtml, imageUrl } = context;

  function renderMessages() {
    messages.innerHTML = [
      state.error ? `<div class="message message-error" role="alert"><span>${escapeHtml(state.error)}</span><button class="message-close" data-action="close-message" aria-label="Закрыть">×</button></div>` : '',
      state.notice ? `<div class="message message-success" role="status"><span>${escapeHtml(state.notice)}</span><button class="message-close" data-action="close-message" aria-label="Закрыть">×</button></div>` : ''
    ].join('');
  }

  function renderHeader() {
    if (state.page === 'login') { header.innerHTML = ''; return; }
    const user = state.user;
    const role = roleKey(user?.role);
    const roleText = role === 'admin' ? 'Администратор' : role === 'manager' ? 'Менеджер' : 'Пользователь';
    header.innerHTML = `
      <div class="site-header">
        <div class="brand-row"><img class="store-image" src="/images/store-image.png" alt="Чудо Обувь"><div class="brand-copy"><div class="brand-title">Чудо Обувь</div><div class="brand-subtitle">Каталог и оформление заказов</div></div></div>
        <nav class="nav-tabs" aria-label="Основная навигация">
          <button class="nav-tab ${state.page === 'catalog' ? 'active' : ''}" data-page="catalog">Каталог</button>
          ${user ? `<button class="nav-tab ${state.page === 'orders' ? 'active' : ''}" data-page="orders">Заказы</button>` : ''}
        </nav>
        <div class="account-box">${user ? `<div class="account-name">${escapeHtml(fullName(user))}<span class="role-label">${roleText}</span></div><button class="button button-plain" data-action="logout">Выйти</button>` : '<button class="button button-primary" data-page="login">Войти</button>'}</div>
      </div>`;
  }

  function renderLogin() {
    app.innerHTML = `
      <main class="login-page">
        <section class="login-banner"><img src="/images/store-image.png" alt=""><div><span class="eyebrow">МАГАЗИН ОБУВИ</span><h1>Чудо Обувь</h1><p>Выберите подходящую пару и оформите заказ.</p></div></section>
        <form class="login-card" id="login-form"><h2>Вход в систему</h2><p class="muted">Введите логин из списка пользователей. Пароль не требуется.</p>
          <label for="login">Логин</label><input id="login" name="login" autocomplete="username" placeholder="Например, ivanov" required autofocus>
          <button class="button button-primary button-wide" type="submit" ${state.busy ? 'disabled' : ''}>${state.busy ? 'Входим…' : 'Войти'}</button>
          <button class="button button-plain button-wide" type="button" data-action="browse">Смотреть каталог без входа</button>
        </form>
      </main>`;
  }

  function renderCatalog() {
    const canEdit = isStaff();
    const cartCount = state.cart.reduce((sum, line) => sum + line.quantity, 0);
    const cartTotal = state.cart.reduce((sum, line) => sum + Number(line.product.discounted_price) * line.quantity, 0);
    const categoryOptions = state.categories.map(item => `<option value="${item.category_id}" ${String(item.category_id) === state.categoryId ? 'selected' : ''}>${escapeHtml(item.name)}</option>`).join('');
    const subcategoryOptions = state.subcategories.map(item => `<option value="${item.subcategory_id}" ${String(item.subcategory_id) === state.subcategoryId ? 'selected' : ''}>${escapeHtml(item.name)}</option>`).join('');
    const cart = state.user && state.cart.length ? `
      <section class="cart-panel panel"><div class="section-heading"><div><h2>Корзина</h2><p class="muted">Позиций: ${state.cart.length} · Пар: ${cartCount}</p></div><strong class="cart-total">${money(cartTotal)}</strong></div>
      <div class="cart-lines">${state.cart.map((line, index) => `<div class="cart-line"><div class="cart-line-title"><strong>${escapeHtml(line.product.product_name)}</strong><span class="muted">Размер ${escapeHtml(line.size_value)}</span></div><div class="quantity-control"><button data-action="cart-minus" data-index="${index}" aria-label="Уменьшить количество">−</button><span>${line.quantity}</span><button data-action="cart-plus" data-index="${index}" aria-label="Увеличить количество">+</button></div><strong>${money(Number(line.product.discounted_price) * line.quantity)}</strong><button class="text-button danger-text" data-action="cart-remove" data-index="${index}">Убрать</button></div>`).join('')}</div>
      <div class="cart-actions"><span class="muted">Остаток будет проверен при оформлении заказа.</span><button class="button button-primary" data-action="checkout" ${state.busy ? 'disabled' : ''}>${state.busy ? 'Оформляем…' : 'Оформить заказ'}</button></div></section>` : '';
    const editor = state.editing ? renderProductEditor() : '';
    const products = state.loading ? '<div class="empty-state">Загружаем каталог…</div>' : !state.products.length ? '<div class="empty-state">По вашему запросу ничего не найдено.</div>' : `<section class="product-list" aria-label="Каталог товаров">${state.products.map(renderProduct).join('')}</section>`;

    app.innerHTML = `<main class="page-content">
      <div class="page-heading"><div><span class="eyebrow">КАТАЛОГ</span><h1>Обувь в наличии</h1><p class="muted">Выберите модель, размер и количество пар.</p></div>${canEdit ? '<button class="button button-primary" data-action="new-product">+ Добавить товар</button>' : ''}</div>
      <section class="filters panel"><label class="search-field"><span>Поиск</span><input id="search-filter" value="${escapeHtml(state.search)}" placeholder="Название или описание"></label>
        <label><span>Категория</span><select id="category-filter"><option value="">Все категории</option>${categoryOptions}</select></label>
        <label><span>Подкатегория</span><select id="subcategory-filter" ${state.categoryId ? '' : 'disabled'}><option value="">${state.categoryId ? 'Все подкатегории' : 'Сначала выберите категорию'}</option>${subcategoryOptions}</select></label>
        <label><span>Сортировка</span><select id="sort-filter"><option value="" ${!state.sort ? 'selected' : ''}>По названию</option><option value="price_asc" ${state.sort === 'price_asc' ? 'selected' : ''}>Сначала дешевле</option><option value="price_desc" ${state.sort === 'price_desc' ? 'selected' : ''}>Сначала дороже</option></select></label>
      </section>${cart}${editor}${products}</main>`;
  }

  function renderProduct(product) {
    const detail = state.details[product.product_id];
    const selectedSizeId = state.selectedSizes[product.product_id];
    const selected = detail?.sizes.find(size => size.size_id === Number(selectedSizeId));
    const sizes = detail ? detail.sizes.map(size => `<option value="${size.size_id}" ${size.size_id === Number(selectedSizeId) ? 'selected' : ''} ${size.quantity_available < 1 ? 'disabled' : ''}>${escapeHtml(size.size_value)} · в наличии ${size.quantity_available}</option>`).join('') : '';
    return `<article class="product-card ${product.low_stock ? 'low-stock' : ''}">
      <div class="product-image-wrap"><img src="${escapeHtml(imageUrl(product.image_path))}" alt="${escapeHtml(product.product_name)}" data-fallback-image></div>
      <div class="product-info"><div class="product-category">${escapeHtml(product.category)}${product.subcategory ? ` / ${escapeHtml(product.subcategory)}` : ''}</div><h2>${escapeHtml(product.product_name)}</h2><div class="muted">Производитель: ${escapeHtml(product.manufacturer)}</div>
        ${product.description ? `<p class="product-description">${escapeHtml(product.description)}</p>` : ''}${product.composition ? `<p class="product-composition"><span>Состав:</span> ${escapeHtml(product.composition)}</p>` : ''}
        <div class="stock-line"><span>Всего доступно:</span><strong class="${product.low_stock ? 'stock-warning' : ''}">${product.total_quantity} пар</strong>${product.low_stock ? '<span class="stock-badge">Мало на складе</span>' : ''}</div>
        ${detail ? `<div class="size-picker"><label><span>Размер</span><select data-size-product="${product.product_id}"><option value="">Выберите размер</option>${sizes}</select></label><label class="quantity-field"><span>Количество</span><input data-quantity-product="${product.product_id}" type="number" min="1" max="${selected?.quantity_available || 1}" value="${state.quantities[product.product_id] || 1}"></label></div>` : ''}
        ${canManageProduct() ? `<div class="product-admin-actions"><button class="text-button" data-action="edit-product" data-id="${product.product_id}">Редактировать карточку / остатки</button><button class="text-button danger-text" data-action="delete-product" data-id="${product.product_id}">Удалить</button></div>` : ''}
      </div><div class="product-buy"><div class="price-block">${product.discount_percent > 0 ? `<div class="old-price">${money(product.price)}</div>` : ''}<div class="current-price">${money(product.discounted_price)}</div>${product.discount_percent > 0 ? `<span class="discount-badge">−${product.discount_percent}%</span>` : ''}</div>
        ${!detail ? `<button class="button button-primary" data-action="show-sizes" data-id="${product.product_id}">Выбрать размер</button>` : !state.user ? '<button class="button button-primary" data-page="login">Войти для заказа</button>' : `<button class="button button-primary" data-action="add-cart" data-id="${product.product_id}" ${!selected || selected.quantity_available < 1 ? 'disabled' : ''}>В корзину</button>`}
        ${detail ? `<button class="button button-plain" data-action="hide-sizes" data-id="${product.product_id}">Скрыть размеры</button>` : ''}</div></article>`;
  }

  function canManageProduct() { return isStaff(); }

  function renderProductEditor() {
    const product = state.editing === 'new' ? null : state.editing;
    const form = state.productForm || (state.productForm = {
      category_id: String(product?.category_id || state.categories[0]?.category_id || ''),
      subcategory_id: String(product?.subcategory_id || ''), product_name: product?.product_name || '',
      manufacturer: product?.manufacturer || '', description: product?.description || '',
      composition: product?.composition || '', price: String(product?.price || '')
    });
    const categoryOptions = state.categories.map(item => `<option value="${item.category_id}" ${String(item.category_id) === form.category_id ? 'selected' : ''}>${escapeHtml(item.name)}</option>`).join('');
    const subs = state.formSubcategories || [];
    return `<section class="editor-panel panel"><div class="section-heading"><h2>${product ? 'Редактирование товара' : 'Новый товар'}</h2><button class="button button-plain" data-action="close-editor">Закрыть</button></div>
      <form class="product-form" id="product-form"><label><span>Название</span><input name="product_name" required value="${escapeHtml(form.product_name)}"></label><label><span>Производитель</span><input name="manufacturer" required value="${escapeHtml(form.manufacturer)}"></label>
      <label><span>Категория</span><select name="category_id" required><option value="">Выберите</option>${categoryOptions}</select></label><label><span>Подкатегория</span><select name="subcategory_id"><option value="">Без подкатегории</option>${subs.map(item => `<option value="${item.subcategory_id}" ${String(item.subcategory_id) === form.subcategory_id ? 'selected' : ''}>${escapeHtml(item.name)}</option>`).join('')}</select></label>
      <label><span>Цена, ₽</span><input name="price" type="number" min="0.01" step="0.01" required value="${escapeHtml(form.price)}"></label><label><span>Изображение товара${product ? '' : ' *'}</span><input id="product-image" name="image" type="file" accept="image/png,image/jpeg,image/webp,image/gif" ${product ? '' : 'required'}><small>JPG, PNG, WEBP или GIF, до 10 МБ. Файл сохранится на backend.</small>${product?.image_path ? `<small>Текущее изображение: ${escapeHtml(product.image_path.split('/').pop())}</small>` : ''}</label>
      <label class="span-two"><span>Описание</span><textarea name="description" rows="2">${escapeHtml(form.description)}</textarea></label><label class="span-two"><span>Состав</span><input name="composition" value="${escapeHtml(form.composition)}"></label>
      <div class="form-actions span-two"><button class="button button-primary" ${state.busy ? 'disabled' : ''}>${state.busy ? 'Сохраняем…' : 'Сохранить товар'}</button><button type="button" class="button button-plain" data-action="close-editor">Отмена</button></div></form>
      ${product ? renderStockEditor(product) : ''}</section>`;
  }

  function renderStockEditor(product) {
    return `<div class="stock-editor"><h3>Остатки по размерам</h3>${product.sizes.length ? product.sizes.map(size => `<form class="stock-edit-row" data-stock-form data-product-id="${product.product_id}" data-size-id="${size.size_id}"><span>Размер ${escapeHtml(size.size_value)}</span><input name="quantity" aria-label="Количество размера ${escapeHtml(size.size_value)}" type="number" min="0" max="1000000" value="${size.quantity_available}" required><button class="button button-secondary">Сохранить</button></form>`).join('') : '<p class="muted">У товара пока нет размеров. Добавьте первый размер ниже.</p>'}
      <form class="stock-add-row" id="stock-add-form" data-product-id="${product.product_id}"><label><span>Размер</span><input name="size_value" required maxlength="50" placeholder="Например, 38 или 38.5"></label><label><span>Количество</span><input name="quantity" type="number" min="0" max="1000000" value="0" required></label><button class="button button-secondary">Добавить / изменить размер</button></form></div>`;
  }

  function renderOrders() {
    const orders = state.orders;
    const selected = state.selectedOrder;
    app.innerHTML = `<main class="page-content"><div class="page-heading"><div><span class="eyebrow">ЗАКАЗЫ</span><h1>${isStaff() ? 'Все заказы' : 'Мои заказы'}</h1><p class="muted">Дата, клиент, состав и итоговая стоимость заказа.</p></div></div>
      <div class="orders-layout"><section class="orders-list panel">${orders.length ? orders.map(order => `<button class="order-row ${selected?.order_id === order.order_id ? 'selected' : ''}" data-action="open-order" data-id="${order.order_id}"><span class="order-number">Заказ №${order.order_id}<small>${dateTime(order.order_date)}</small></span><span class="order-customer">${escapeHtml(order.customer_full_name)}</span><strong>${money(order.total)}</strong></button>`).join('') : '<div class="empty-state">Заказов пока нет.</div>'}</section>
      <section class="order-detail panel">${!selected ? '<div class="empty-state">Выберите заказ слева, чтобы посмотреть состав.</div>' : renderOrderDetail(selected)}</section></div>
      ${isStaff() ? '<p class="hint">Менеджер и администратор могут удалять заказы. Только администратор может менять дату, количество и удалять отдельные позиции.</p>' : ''}</main>`;
  }

  function renderOrderDetail(order) {
    return `<div class="section-heading"><div><span class="eyebrow">ЗАКАЗ №${order.order_id}</span><h2>Состав заказа</h2></div>${isStaff() ? `<button class="button button-danger" data-action="delete-order" data-id="${order.order_id}">Удалить заказ</button>` : ''}</div>
      <div class="order-meta"><div><span>Клиент</span><strong>${escapeHtml(order.customer_full_name)}</strong></div><div><span>Дата заказа</span><strong>${dateTime(order.order_date)}</strong></div><div><span>Итого</span><strong class="current-price">${money(order.total)}</strong></div></div>
      ${isAdmin() ? `<form class="edit-date" id="order-date-form"><label><span>Изменить дату заказа</span><input type="datetime-local" name="order_date" value="${escapeHtml(state.orderDate)}" required></label><button class="button button-secondary">Сохранить дату</button></form>` : ''}
      <div class="order-items">${order.items.length ? order.items.map(item => `<div class="order-item"><div class="order-item-name"><strong>${escapeHtml(item.product_name)}</strong><span class="muted">${escapeHtml(item.manufacturer)} · размер ${escapeHtml(item.size_value)}</span><small>${money(item.price)} за пару</small></div>${isAdmin() ? `<label class="item-quantity"><span>Количество</span><input type="number" min="1" max="10000" value="${item.quantity}" data-order-quantity="${item.order_item_id}" data-order-id="${order.order_id}"></label>` : `<span class="item-count">${item.quantity} пар</span>`}<strong>${money(item.line_total)}</strong>${isAdmin() ? `<button class="text-button danger-text" data-action="delete-order-item" data-id="${item.order_item_id}" data-order-id="${order.order_id}">Удалить позицию</button>` : ''}</div>`).join('') : '<p class="muted">В заказе не осталось позиций.</p>'}</div>
      <div class="order-total-row"><span>Итоговая стоимость</span><strong>${money(order.total)}</strong></div>`;
  }

  return { renderMessages, renderHeader, renderLogin, renderCatalog, renderProduct, canManageProduct, renderProductEditor, renderStockEditor, renderOrders, renderOrderDetail };
}
