# «Чудо Обувь»

Веб-приложение для каталога обуви, оформления заказов и управления товарами и заказами.

## 1. Технологии

- Backend: Python, FastAPI, SQLModel, SQLAlchemy, Psycopg.
- База данных: PostgreSQL.
- Frontend: React, TypeScript, Vite.
- Импорт исходных данных: Excel (`.xlsx`).

## 2. Структура проекта

Ожидаемая структура:

```text
chudo_obuv_project/
├── backend/
│   ├── main.py
│   ├── config.toml
│   ├── requirements.txt
│   ├── api/
│   ├── model/
│   ├── repositories/
│   ├── services/
│   ├── db/
│   ├── scripts/
│   └── import_data/
└── frontend/
    ├── package.json
    ├── index.html
    └── src/
```

Команды ниже рассчитаны на то, что `main.py` находится в `backend/`.

## 3. Что установить

Установи Python (лучше 3.12 или 3.13, если зависимости не проверены на более новых версиях), Node.js LTS с npm и PostgreSQL.

Проверь установку:

```bash
python --version
node --version
npm --version
psql --version
```

На некоторых системах Python вызывается командой `python3`.

## 4. Запуск PostgreSQL и создание базы

Проверь службу:

```bash
sudo systemctl status postgresql
```

Если она остановлена:

```bash
sudo systemctl start postgresql
```

Проверь порт:

```bash
pg_isready -h localhost -p 5432
```

Если роль и база ещё не существуют, создай их. Открой консоль PostgreSQL:

```bash
sudo -u postgres psql
```

Выполни, заменив пароль на свой:

```sql
CREATE ROLE chudo_user WITH LOGIN PASSWORD 'replace_with_your_password';
CREATE DATABASE chudo_obuv OWNER chudo_user;
```

Выход:

```sql
\q
```

Если база или роль уже существуют, не создавай их повторно и не удаляй имеющиеся данные.

## 5. Настройка `backend/config.toml`

В `backend/config.toml` укажи свои параметры PostgreSQL. Пример:

```toml
db_conn = "postgresql+psycopg://chudo_user:replace_with_your_password@localhost:5432/chudo_obuv"
storage_dir = "./data"
```

Используй фактические имя пользователя, пароль и имя базы. Если пароль содержит символы `@`, `:`, `/` или `#`, их может потребоваться URL-кодировать в строке подключения.

Не публикуй файл с реальным паролем в открытом репозитории.

## 6. Установка backend-зависимостей

Перейди в backend:

```bash
cd /путь/к/chudo_obuv_project/backend
```

Рекомендуется отдельное виртуальное окружение:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Если виртуальное окружение уже создано в корне проекта (`chudo_obuv_project/.venv`), активируй его из `backend/` так:

```bash
source ../.venv/bin/activate
```

Используй то окружение, куда устанавливаешь зависимости. Не устанавливай пакеты в один Python, а сервер не запускай из другого.

Если `requirements.txt` отсутствует, можно установить основной набор вручную:

```bash
python -m pip install fastapi "uvicorn[standard]" sqlmodel "psycopg[binary]" openpyxl python-multipart
```

Проверь импорт:

```bash
python -c "import fastapi, sqlmodel, sqlalchemy, psycopg; print('Зависимости установлены')"
```

## 7. Импорт Excel-данных

Если импортные файлы предусмотрены заданием, они обычно размещаются в `backend/import_data/`. В этой версии проекта ожидаются файлы примерно с такими именами:

```text
Users_import.xlsx
Products_import.xlsx
Sizes_import.xlsx
Stock_Items_import.xlsx
Orders_import.xlsx
```

Проверь реальные имена файлов и заголовки столбцов по коду `scripts/import_data.py`.

Если импортёр реализован как Python-модуль, запускай его из `backend/`:

```bash
python -m scripts.import_data
```

Перед запуском изучи доступные параметры скрипта. Не используй опцию сброса (`--reset`), если нужно сохранить данные. Перед повторным импортом сделай резервную копию базы.

## 8. Запуск backend

**Запускай Uvicorn из каталога `backend/`, а не из корня проекта.** Иначе Python может не найти `main.py`.

```bash
cd /путь/к/chudo_obuv_project/backend
source .venv/bin/activate
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Если `.venv` находится в корне проекта, используй `source ../.venv/bin/activate`.

После запуска доступны:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

Swagger UI доступен, если документация не отключена в приложении.

## 9. Запуск frontend

Открой второй терминал:

```bash
cd /путь/к/chudo_obuv_project/frontend
npm install
npm run dev
```

Открой адрес, который Vite напечатает в терминале. Обычно это `http://localhost:5173`, но порт может отличаться, если он занят.

Если `npm run dev` отсутствует, проверь раздел `scripts` в `frontend/package.json`.

## 10. Обычный порядок запуска

1. Запусти PostgreSQL:

   ```bash
   sudo systemctl start postgresql
   ```

2. В первом терминале запусти backend из `backend/`:

   ```bash
   cd /путь/к/chudo_obuv_project/backend
   source .venv/bin/activate
   python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

   Если окружение лежит в корне проекта, используй `source ../.venv/bin/activate`.

3. Во втором терминале запусти frontend:

   ```bash
   cd /путь/к/chudo_obuv_project/frontend
   npm run dev
   ```

Оба терминала с приложением должны оставаться открытыми.

## 11. Частые ошибки

### `Could not import module "main"`

Чаще всего Uvicorn запущен не из `backend/` или в самом `main.py` есть ошибка импорта:

```bash
cd /путь/к/chudo_obuv_project/backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Если ошибка повторяется, изучи полный traceback: настоящая причина обычно указана выше строки `Could not import module "main"`.

### `ModuleNotFoundError: No module named 'sqlmodel'`

Зависимости установлены не в то окружение:

```bash
which python
python -m pip --version
python -m pip install -r requirements.txt
python -c "import sqlmodel; print(sqlmodel.__version__)"
```

### `connection refused` на `localhost:5432`

PostgreSQL не запущен или не слушает порт:

```bash
sudo systemctl status postgresql
sudo systemctl start postgresql
pg_isready -h localhost -p 5432
```

### `role "..." does not exist`

Пользователь в `config.toml` не совпадает с существующей ролью PostgreSQL. Проверь `db_conn`.

### `password authentication failed`

Проверь пароль и правила аутентификации PostgreSQL.

### `database "..." does not exist`

Создай базу данных или исправь имя базы в `db_conn`.

### Frontend не загружает данные или выдаёт `fetch` error

1. Убедись, что backend работает.
2. Открой `http://127.0.0.1:8000/docs`.
3. Проверь адрес API в настройках frontend.
4. Посмотри ошибки в браузере во вкладках **Console** и **Network**.
5. Если браузер сообщает об ошибке CORS, проверь CORS-настройки backend.

### Изменения моделей не отражаются в PostgreSQL

`SQLModel.metadata.create_all()` создаёт отсутствующие таблицы, но не обновляет структуру уже существующих. Для изменения схемы нужна миграция или аккуратное пересоздание базы. Не удаляй базу без резервной копии.

## 12. Резервное копирование базы

Перед импортом, сбросом данных или изменением схемы можно сохранить базу так:

```bash
pg_dump -h localhost -p 5432 -U chudo_user -d chudo_obuv -F c -f chudo_obuv_backup.dump
```

Восстановление выполняется через `pg_restore` в подходящую базу. Не восстанавливай поверх нужных данных без понимания последствий.

## 13. Полезные адреса

| Назначение | Адрес |
|---|---|
| Frontend | `http://localhost:5173` (проверь вывод Vite) |
| Backend API | `http://127.0.0.1:8000` |
| Swagger UI | `http://127.0.0.1:8000/docs` |
| OpenAPI JSON | `http://127.0.0.1:8000/openapi.json` |

Точный адрес frontend всегда указан в терминале после запуска Vite.
