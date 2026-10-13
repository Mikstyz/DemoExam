import { createViews } from './views/screens.js';
import { createApi } from './api.js';
import { readSavedUser, roleKey, fullName, money, dateTime, localDateTime, escapeHtml, imageUrl } from './utils.js';

/* Главный контроллер приложения: состояние, события и сценарии пользователя. */
(() => {
  'use strict';

  const USER_KEY = 'chudo-obuv-user';

  const $ = (selector, root = document) => root.querySelector(selector);
  const app = $('#app-main');
  const header = $('#site-header');
  const messages = $('#messages');

  const state = {
    user: readSavedUser(), page: readSavedUser() ? 'catalog' : 'login',
    products: [], categories: [], subcategories: [], cart: [], details: {},
    selectedSizes: {}, quantities: {}, search: '', categoryId: '', subcategoryId: '', sort: '',
    editing: null, orders: [], selectedOrder: null, orderDate: '', loading: false,
    busy: false, notice: '', error: '', filterTimer: null
  };

  function isStaff() { return ['manager', 'admin'].includes(roleKey(state.user?.role)); }
  function isAdmin() { return roleKey(state.user?.role) === 'admin'; }
  const request = createApi(() => state.user);
  const views = createViews({ state, app, header, messages, roleKey, isStaff, isAdmin, fullName, money, dateTime, localDateTime, escapeHtml, imageUrl });
  const { renderMessages, renderHeader, renderLogin, renderCatalog, renderProduct, canManageProduct, renderProductEditor, renderStockEditor, renderOrders, renderOrderDetail } = views;


  function showNotice(text) { state.notice = text; state.error = ''; renderMessages(); }
  function showError(error) { state.error = error instanceof Error ? error.message : 'Произошла ошибка'; state.notice = ''; renderMessages(); }
  async function loadCategories() {
    state.categories = await request('/api/categories');
  }
  async function loadSubcategories(categoryId) {
    if (!categoryId) { state.subcategories = []; return; }
    const items = await request(`/api/subcategories?category_id=${encodeURIComponent(categoryId)}`);
    const unique = new Map();
    for (const item of items) {
      const key = item.name.trim().replace(/\s+/g, ' ').toLocaleLowerCase('ru-RU');
      if (!unique.has(key)) unique.set(key, item);
    }
    state.subcategories = [...unique.values()];
  }
  async function loadProducts() {
    state.loading = true;
    renderCatalog();
    const params = new URLSearchParams();
    if (state.categoryId) params.set('category_id', state.categoryId);
    if (state.subcategoryId) params.set('subcategory_id', state.subcategoryId);
    if (state.search.trim()) params.set('search', state.search.trim());
    if (state.sort) params.set('sort', state.sort);
    try {
      state.products = await request(`/api/products${params.size ? `?${params}` : ''}`);
    } catch (error) { showError(error); }
    finally { state.loading = false; render(); }
  }

  async function openProductEditor(productId = null) {
    try {
      if (productId) state.editing = await request(`/api/products/${productId}`);
      else state.editing = 'new';
      state.productForm = null;
      const form = state.editing === 'new' ? { category_id: String(state.categories[0]?.category_id || ''), subcategory_id: '', product_name: '', manufacturer: '', description: '', composition: '', price: '' } : {
        category_id: String(state.editing.category_id), subcategory_id: String(state.editing.subcategory_id || ''), product_name: state.editing.product_name,
        manufacturer: state.editing.manufacturer, description: state.editing.description || '', composition: state.editing.composition || '', price: String(state.editing.price)
      };
      state.productForm = form;
      await loadFormSubcategories(form.category_id);
      render();
    } catch (error) { showError(error); }
  }
  async function loadFormSubcategories(categoryId) {
    if (!categoryId) { state.formSubcategories = []; return; }
    try { state.formSubcategories = await request(`/api/subcategories?category_id=${encodeURIComponent(categoryId)}`); }
    catch (error) { showError(error); state.formSubcategories = []; }
  }

  async function saveProduct(formElement) {
    const formData = new FormData(formElement);
    const image = formData.get('image');
    if (state.editing === 'new' && !(image instanceof File && image.size)) throw new Error('Выберите изображение товара');
    const body = {
      category_id: Number(formData.get('category_id')),
      subcategory_id: formData.get('subcategory_id') ? Number(formData.get('subcategory_id')) : null,
      product_name: String(formData.get('product_name') || '').trim(),
      manufacturer: String(formData.get('manufacturer') || '').trim(),
      description: String(formData.get('description') || '').trim() || null,
      composition: String(formData.get('composition') || '').trim() || null,
      price: Number(formData.get('price'))
    };
    state.busy = true; render();
    try {
      let product;
      if (state.editing === 'new') {
        product = await request('/api/products', { method: 'POST', body: JSON.stringify(body) });
        state.editing = product;
        if (image instanceof File && image.size) await uploadImage(product.product_id, image);
        state.editing = await request(`/api/products/${product.product_id}`);
        showNotice('Товар создан. Теперь можно указать размеры и остатки.');
      } else {
        product = await request(`/api/products/${state.editing.product_id}`, { method: 'PATCH', body: JSON.stringify(body) });
        if (image instanceof File && image.size) await uploadImage(product.product_id, image);
        state.editing = null;
        showNotice('Карточка товара сохранена');
      }
      await loadProducts();
      if (state.editing) render();
    } catch (error) { showError(error); render(); }
    finally { state.busy = false; render(); }
  }
  async function uploadImage(productId, file) {
    const data = new FormData(); data.append('image', file);
    await request(`/api/products/${productId}/image`, { method: 'POST', body: data });
  }
  async function saveStock(productId, sizeId, quantity) {
    if (!Number.isInteger(quantity) || quantity < 0 || quantity > 1000000) throw new Error('Количество должно быть целым числом от 0 до 1 000 000');
    await request(`/api/products/${productId}/stock/${sizeId}`, { method: 'PUT', body: JSON.stringify({ quantity_available: quantity }) });
    state.editing = await request(`/api/products/${productId}`);
    state.details[productId] = state.editing;
    await loadProducts(); showNotice('Остаток сохранён');
  }
  async function saveStockByValue(productId, sizeValue, quantity) {
    if (!sizeValue.trim()) throw new Error('Укажите размер');
    if (!Number.isInteger(quantity) || quantity < 0 || quantity > 1000000) throw new Error('Количество должно быть целым числом от 0 до 1 000 000');
    await request(`/api/products/${productId}/stock/by-value`, { method: 'PUT', body: JSON.stringify({ size_value: sizeValue.trim(), quantity_available: quantity }) });
    state.editing = await request(`/api/products/${productId}`);
    state.details[productId] = state.editing;
    await loadProducts(); showNotice(`Размер ${sizeValue} сохранён`);
  }

  async function showSizes(productId) {
    try {
      const detail = await request(`/api/products/${productId}`);
      state.details[productId] = detail;
      const firstAvailable = detail.sizes.find(size => size.quantity_available > 0);
      if (!state.selectedSizes[productId] && firstAvailable) state.selectedSizes[productId] = firstAvailable.size_id;
      render();
    } catch (error) { showError(error); }
  }
  function addToCart(productId) {
    const product = state.products.find(item => item.product_id === productId);
    const detail = state.details[productId];
    const size = detail?.sizes.find(item => item.size_id === Number(state.selectedSizes[productId]));
    const quantity = Math.max(1, Number(state.quantities[productId] || 1));
    if (!product || !size || size.quantity_available < 1) { showError('Выберите доступный размер'); return; }
    const existing = state.cart.find(line => line.product.product_id === productId && line.size_id === size.size_id);
    if ((existing?.quantity || 0) + quantity > size.quantity_available) { showError(`Для размера ${size.size_value} доступно ${size.quantity_available} пар`); return; }
    if (existing) existing.quantity += quantity;
    else state.cart.push({ product, size_id: size.size_id, size_value: size.size_value, quantity });
    showNotice(`${product.product_name} добавлен в корзину`); render();
  }
  async function checkout() {
    if (!state.user) { state.page = 'login'; showNotice('Войдите по логину, чтобы оформить заказ.'); render(); return; }
    if (!state.cart.length) return;
    state.busy = true; render();
    try {
      const order = await request('/api/orders', { method: 'POST', body: JSON.stringify({ items: state.cart.map(line => ({ product_id: line.product.product_id, size_id: line.size_id, quantity: line.quantity })) }) });
      const productIds = [...new Set(state.cart.map(line => line.product.product_id))];
      state.cart = [];
      for (const id of productIds) {
        try { state.details[id] = await request(`/api/products/${id}`); } catch { /* каталог обновится отдельно */ }
      }
      await loadProducts(); showNotice(`Заказ №${order.order_id} оформлен`);
    } catch (error) { showError(error); }
    finally { state.busy = false; render(); }
  }

  async function loadOrders() {
    state.orders = await request(isStaff() ? '/api/orders' : '/api/orders/my');
  }
  async function openOrder(orderId) {
    try {
      state.selectedOrder = await request(`/api/orders/${orderId}`);
      state.orderDate = localDateTime(state.selectedOrder.order_date);
      render();
    } catch (error) { showError(error); }
  }
  async function render() {
    renderHeader(); renderMessages();
    if (state.page === 'login') { renderLogin(); return; }
    if (state.page === 'orders') {
      try { await loadOrders(); } catch (error) { showError(error); }
      renderOrders(); return;
    }
    renderCatalog();
  }

  async function navigate(page) {
    state.page = page;
    if (page === 'catalog') {
      try { if (!state.categories.length) await loadCategories(); await loadSubcategories(state.categoryId); await loadProducts(); }
      catch (error) { showError(error); }
    } else if (page === 'orders' && state.user) {
      try { await loadOrders(); } catch (error) { showError(error); }
    }
    render();
  }

  document.addEventListener('click', async event => {
    const target = event.target.closest('[data-action], [data-page]');
    if (!target) return;
    if (target.dataset.page) { await navigate(target.dataset.page); return; }
    const action = target.dataset.action;
    const id = Number(target.dataset.id);
    try {
      switch (action) {
        case 'close-message': state.error = ''; state.notice = ''; renderMessages(); break;
        case 'browse': await navigate('catalog'); break;
        case 'logout': localStorage.removeItem(USER_KEY); state.user = null; state.cart = []; state.page = 'catalog'; await navigate('catalog'); showNotice('Вы вышли из системы'); break;
        case 'new-product': await openProductEditor(); break;
        case 'close-editor': state.editing = null; state.productForm = null; render(); break;
        case 'show-sizes': await showSizes(id); break;
        case 'hide-sizes': delete state.details[id]; render(); break;
        case 'add-cart': addToCart(id); break;
        case 'cart-minus': changeCart(Number(target.dataset.index), -1); break;
        case 'cart-plus': changeCart(Number(target.dataset.index), 1); break;
        case 'cart-remove': state.cart.splice(Number(target.dataset.index), 1); render(); break;
        case 'checkout': await checkout(); break;
        case 'edit-product': await openProductEditor(id); break;
        case 'delete-product': {
          const product = state.products.find(item => item.product_id === id);
          if (product && confirm(`Удалить товар «${product.product_name}»?`)) {
            await request(`/api/products/${id}`, { method: 'DELETE' });
            showNotice('Товар удалён'); await loadProducts();
          }
          break;
        }
        case 'open-order': await openOrder(id); break;
        case 'delete-order':
          if (confirm(`Удалить заказ №${id}? Остатки товара будут восстановлены.`)) {
            await request(`/api/orders/${id}`, { method: 'DELETE' }); state.selectedOrder = null;
            showNotice(`Заказ №${id} удалён`); await loadOrders(); renderOrders();
          }
          break;
        case 'delete-order-item':
          if (confirm('Удалить позицию из заказа? Остаток будет восстановлен.')) {
            await request(`/api/orders/${target.dataset.orderId}/items/${id}`, { method: 'DELETE' });
            await openOrder(Number(target.dataset.orderId)); await loadOrders(); showNotice('Позиция удалена');
          }
          break;
      }
    } catch (error) { showError(error); }
  });

  function changeCart(index, difference) {
    const line = state.cart[index];
    if (!line) return;
    line.quantity += difference;
    if (line.quantity < 1) state.cart.splice(index, 1);
    render();
  }

  document.addEventListener('change', async event => {
    const target = event.target;
    try {
      if (target.id === 'category-filter') {
        state.categoryId = target.value; state.subcategoryId = ''; await loadSubcategories(state.categoryId); await loadProducts();
      } else if (target.id === 'subcategory-filter') {
        state.subcategoryId = target.value; await loadProducts();
      } else if (target.id === 'sort-filter') {
        state.sort = target.value; await loadProducts();
      } else if (target.matches('[data-size-product]')) {
        state.selectedSizes[target.dataset.sizeProduct] = Number(target.value); render();
      } else if (target.matches('[data-quantity-product]')) {
        state.quantities[target.dataset.quantityProduct] = Math.max(1, Number(target.value || 1));
      } else if (target.matches('[data-stock-form]')) {
        // Сохранение выполняется кнопкой формы, а не при каждом изменении поля.
      } else if (target.matches('[data-order-quantity]')) {
        const orderId = Number(target.dataset.orderId); const itemId = Number(target.dataset.orderQuantity); const quantity = Number(target.value);
        if (Number.isInteger(quantity) && quantity > 0 && quantity <= 10000) {
          const updated = await request(`/api/orders/${orderId}/items/${itemId}?quantity=${quantity}`, { method: 'PATCH' });
          state.selectedOrder = updated; await loadOrders(); renderOrders(); showNotice('Количество обновлено');
        } else showError('Количество должно быть целым числом от 1 до 10 000');
      }
    } catch (error) { showError(error); }
  });

  document.addEventListener('input', event => {
    const target = event.target;
    if (target.id === 'search-filter') {
      state.search = target.value;
      clearTimeout(state.filterTimer);
      state.filterTimer = setTimeout(() => { void loadProducts(); }, 300);
    }
  });

  document.addEventListener('submit', async event => {
    const form = event.target;
    event.preventDefault();
    try {
      if (form.id === 'login-form') {
        const login = String(new FormData(form).get('login') || '').trim();
        if (!login) throw new Error('Введите логин');
        state.busy = true; renderLogin();
        const user = await request('/api/auth/login', { method: 'POST', body: JSON.stringify({ login }) }, null);
        state.user = user; localStorage.setItem(USER_KEY, JSON.stringify(user)); state.page = 'catalog';
        showNotice(`Вход выполнен: ${fullName(user)}`); await navigate('catalog');
      } else if (form.id === 'product-form') {
        await saveProduct(form);
      } else if (form.matches('[data-stock-form]')) {
        const productId = Number(form.dataset.productId); const sizeId = Number(form.dataset.sizeId);
        await saveStock(productId, sizeId, Number(new FormData(form).get('quantity'))); render();
      } else if (form.id === 'stock-add-form') {
        const data = new FormData(form);
        await saveStockByValue(Number(form.dataset.productId), String(data.get('size_value') || ''), Number(data.get('quantity'))); render();
      } else if (form.id === 'order-date-form') {
        const date = String(new FormData(form).get('order_date') || '');
        if (!date) throw new Error('Укажите дату заказа');
        const updated = await request(`/api/orders/${state.selectedOrder.order_id}/date`, { method: 'PATCH', body: JSON.stringify({ order_date: date }) });
        state.selectedOrder.order_date = updated.order_date; state.orderDate = localDateTime(updated.order_date);
        await loadOrders(); renderOrders(); showNotice('Дата заказа изменена');
      }
    } catch (error) { showError(error); }
    finally { state.busy = false; }
  });

  document.addEventListener('change', async event => {
    const target = event.target;
    if (target.name === 'category_id' && target.closest('#product-form')) {
      const form = target.closest('#product-form');
      state.productForm = Object.fromEntries(new FormData(form).entries());
      state.productForm.category_id = target.value; state.productForm.subcategory_id = '';
      await loadFormSubcategories(target.value); render();
    }
  });

  document.addEventListener('error', event => {
    const image = event.target;
    if (image instanceof HTMLImageElement && image.hasAttribute('data-fallback-image')) {
      image.removeAttribute('data-fallback-image'); image.src = '/images/picture.png';
    }
  }, true);

  async function start() {
    try {
      await loadCategories();
      if (state.categoryId) await loadSubcategories(state.categoryId);
      if (state.page === 'orders' && !state.user) state.page = 'login';
      if (state.page === 'catalog') await loadProducts();
    } catch (error) { showError(error); }
    render();
  }

  start();
})();
