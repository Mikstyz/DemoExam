# Чудо Обувь

Учебный веб-магазин обуви. Backend написан на Python и FastAPI, данные хранятся в PostgreSQL. Frontend сделан на обычных HTML, CSS и JavaScript: Node.js, npm, React и сборщик для запуска не нужны.

## Возможности

- каталог с поиском, фильтрами по категории и подкатегории, сортировкой по цене;
- карточки товаров с размерами, остатками и автоматической скидкой, если она предусмотрена backend;
- вход по логину из базы данных;
- корзина и оформление заказа с проверкой остатков на сервере;
- просмотр своих заказов;
- функции менеджера и администратора: редактирование товаров, загрузка изображений, изменение остатков и удаление заказов;
- функции администратора: изменение даты заказа, количества в позиции и удаление позиции заказа.

## Требования

- Python 3.12 или 3.13 рекомендуется;
- PostgreSQL;
- pip.

Node.js и npm не используются.

## 1. Настроить PostgreSQL

Убедись, что служба запущена:

```bash
sudo systemctl status postgresql
sudo systemctl start postgresql
pg_isready -h localhost -p 5432
```

Если база и роль ещё не созданы, открой консоль PostgreSQL:

```bash
sudo -u postgres psql
```

Затем создай роль и базу, подставив собственный пароль:

```sql
CREATE ROLE chudo_user WITH LOGIN PASSWORD 'your_password';
CREATE DATABASE chudo_obuv OWNER chudo_user;
\q
```

Если база или роль уже существуют, не создавай их повторно и не удаляй данные.

## 2. Настроить подключение

Открой `backend/config.toml` и укажи свои параметры:

```toml
db_conn = "postgresql+psycopg://chudo_user:your_password@localhost:5432/chudo_obuv"
storage_dir = "./data"
```

В архиве пароль намеренно заменён заглушкой. Приложение не запустится до настройки `db_conn`. Не публикуй конфигурацию с настоящим паролем.

Если пароль содержит `@`, `:`, `/` или `#`, специальные символы в URL могут потребовать кодирования.

## 3. Установить backend

В первом терминале:

```bash
cd /путь/к/chudo_obuv_project/backend
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Если виртуальное окружение уже лежит в корне проекта (`chudo_obuv_project/.venv`), активируй его вместо создания нового:

```bash
source ../.venv/bin/activate
```

Проверить зависимости:

```bash
python -c "import fastapi, sqlmodel, psycopg; print('Зависимости установлены')"
```

## 4. Импортировать данные

Исходные Excel-файлы должны находиться в `backend/import_data/`. В комплекте проекта используются:

- `Users_import.xlsx`
- `Products_import.xlsx`
- `Sizes_import.xlsx`
- `Stock_Items_import.xlsx`
- `Orders_import.xlsx`

Перед импортом проверь структуру файлов. Затем из `backend/` запусти:

```bash
python -m scripts.import_data
```

Не используй параметры сброса данных, если нужно сохранить существующие записи. Перед повторным импортом рекомендуется сделать резервную копию базы.

## 5. Запустить приложение

Из папки `backend/`, с активированным виртуальным окружением:

```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Важно:** `main.py` находится в `backend/`. Запуск Uvicorn из корня проекта приводит к ошибке `Could not import module "main"`.

Открой в браузере:

- сайт: http://127.0.0.1:8000/
- проверка сервера: http://127.0.0.1:8000/health
- документация API: http://127.0.0.1:8000/docs

Backend одновременно отдаёт HTML, CSS, JavaScript и изображения. Второй сервер для фронтенда не нужен.

## Обычный запуск после установки

1. Запусти PostgreSQL, если он остановлен: `sudo systemctl start postgresql`.
2. Открой терминал в `backend/`.
3. Активируй окружение: `source .venv/bin/activate` (либо `source ../.venv/bin/activate`, если окружение в корне).
4. Запусти `python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000`.
5. Открой http://127.0.0.1:8000/.

## Частые ошибки

### `Could not import module "main"`

Uvicorn, скорее всего, запущен не из `backend/`. Перейди в `backend/` и запусти команду из раздела выше. Если ошибка сохраняется, смотри полный traceback: причиной может быть ошибка импорта или настройки.

### `В config.toml остались шаблонные USER:PASSWORD`

Открой `backend/config.toml` и замени заглушку реальными данными PostgreSQL.

### `connection refused` на порту 5432

PostgreSQL не запущен или не слушает этот порт:

```bash
sudo systemctl status postgresql
sudo systemctl start postgresql
pg_isready -h localhost -p 5432
```

### `role does not exist`

Имя пользователя в `db_conn` не совпадает с ролью PostgreSQL.

### `password authentication failed`

Проверь пароль в `config.toml` и правила подключения PostgreSQL.

### `ModuleNotFoundError`

Установи зависимости в том же окружении, из которого запускаешь сервер:

```bash
python -m pip install -r requirements.txt
```

### Сайт открылся, но каталог пустой

Проверь, что импортированы исходные Excel-файлы, сервер подключён к правильной базе и API отвечает на `http://127.0.0.1:8000/api/products`.

### Изменения модели не появились в старой базе

`SQLModel.metadata.create_all()` создаёт отсутствующие таблицы, но не обновляет существующую структуру. Для изменений существующей схемы нужна миграция. Не удаляй базу без резервной копии.

## Резервная копия

```bash
pg_dump -h localhost -p 5432 -U chudo_user -d chudo_obuv -F c -f chudo_obuv_backup.dump
```

Перед сбросом данных, повторным импортом или изменением схемы сначала сохрани резервную копию.

## Как изменять интерфейс

- `frontend/index.html` — базовая HTML-структура;
- `frontend/style.css` — оформление, сетки, цвета и мобильная версия;
- `frontend/app.js` — загрузка данных, действия пользователя и отрисовка страниц;
- `backend/api/` — API-маршруты;
- `backend/services/` — бизнес-логика;
- `backend/model/` — модели базы данных.

После изменения HTML, CSS или JavaScript обнови страницу в браузере. Сборка фронтенда не требуется.

## Важное замечание по авторизации

Текущий backend учебного проекта использует вход по логину без пароля и передаёт ID пользователя через `X-User-ID`. Это удобно для демонстрации, но не подходит для реального магазина без полноценной аутентификации и проверки сессий.


## Структура фронтенда без Node.js

Фронтенд использует нативные ES-модули браузера. Сборка не требуется.

```text
frontend/
├── index.html
├── style.css
├── css/
│   ├── tokens.css
│   ├── base.css
│   └── components.css
├── js/
│   ├── app.js
│   └── views/
│       └── screens.js
└── public/
    └── images/
```

Для изменения внешнего вида начни с `frontend/css/`. Разметка экранов находится в `frontend/js/views/screens.js`, обработка событий и запросы к API — в `frontend/js/app.js`.

## Упрощённая структура кода

Во фронтенде нет сборщика и стороннего UI-фреймворка. Код разделён по назначению:

- `frontend/js/app.js` — состояние приложения и обработчики действий пользователя.
- `frontend/js/api.js` — запросы к FastAPI и обработка HTTP-ответов.
- `frontend/js/utils.js` — форматирование, роли, экранирование текста и пути изображений.
- `frontend/js/views/screens.js` — разметка экранов.
- `frontend/style.css` подключает стили из `frontend/css/`.

В backend общие списки ролей находятся в `backend/api/deps.py`, чтобы категории, товары и заказы использовали одинаковые правила доступа. Модели, маршруты и импорт данных оставлены отдельными для удобства изменений.
