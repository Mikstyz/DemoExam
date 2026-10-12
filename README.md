# Чудо Обувь

Учебный проект магазина обуви: frontend на React + TypeScript + Vite, backend на FastAPI + SQLModel + PostgreSQL.

## Структура

- `frontend/src/App.tsx` — переключение страниц и состояние входа.
- `frontend/src/api.ts` — единый HTTP-клиент и заголовок пользователя.
- `frontend/src/types.ts` — типы данных frontend.
- `frontend/src/utils.ts` — форматирование цен, дат и путей изображений.
- `frontend/src/components/Layout.tsx` — шапка и экран входа.
- `frontend/src/pages/CatalogPage.tsx` — каталог, корзина и редактор товаров.
- `frontend/src/pages/OrdersPage.tsx` — список заказов и управление ими.

- `frontend/` — интерфейс, стили, логотип, favicon, заглушка и изображения товаров.
- `backend/` — API, модели БД, репозитории, сервисы, импортёр и Excel-файлы в `import_data/`.

## Запуск backend

Перед первым запуском откройте `backend/config.toml` и укажите данные своей PostgreSQL-базы. Это единственный файл настроек для API и скриптов.

Из каталога `backend/` активируйте своё виртуальное окружение и запустите:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Проверка API: `http://127.0.0.1:8000/health`.

## Запуск frontend

Из каталога `frontend/`:

```bash
npm install
npm run dev
```

Проверка production-сборки: `npm run build`.

По умолчанию frontend обращается к `http://127.0.0.1:8000`. При необходимости задайте `VITE_API_URL`.

## Дубли категорий

Перед очисткой уже существующей базы сделайте резервную копию PostgreSQL. Затем из каталога `backend/` выполните:

```bash
python -m scripts.dedupe_categories
```

Скрипт объединяет категории и подкатегории с одинаковыми названиями (без учёта регистра и лишних пробелов) и сохраняет связи товаров. Повторный импорт с `--reset` для этого не нужен.

## Импорт Excel

Из каталога `backend/`:

```bash
python -m scripts.import_data
```

Не используйте `--reset`, если не хотите удалить существующие данные перед повторным импортом.


## Изображения и размеры товаров

Изображения товаров хранятся в `backend/data/products/` (настраивается через `storage_dir`); исходные 31 изображения из комплекта также скопированы туда. Новые изображения, загруженные менеджером через форму товара, сохраняются в эту папку и раздаются backend по `/media/products/...`. Форма принимает JPG, PNG, WEBP и GIF размером до 10 МБ. Для загрузки требуется `python-multipart`.

Размер в редакторе остатков вводится текстом. Backend ищет существующий размер без учёта регистра и лишних пробелов; если такого значения нет, создаёт запись `sizes`, затем создаёт или обновляет остаток для товара.

Если база уже была создана со старым типом даты, один раз выполни в PostgreSQL:

```sql
ALTER TABLE orders
ALTER COLUMN order_date TYPE TIMESTAMP WITHOUT TIME ZONE
USING order_date AT TIME ZONE 'UTC';
```
