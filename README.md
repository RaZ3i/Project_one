# Платформа репетиторства MVP

Платформа индивидуальных занятий, где ученики просматривают репетиторов, бронируют свободные слоты и присоединяются к урокам по внешним ссылкам на встречи (Zoom / Google Meet). Репетиторы управляют профилями, слотами и URL встреч для уроков.

**Стек:** FastAPI + PostgreSQL + React (Vite + TypeScript + Tailwind). Один сервис Railway обслуживает API и статический фронтенд.

## Возможности

| Роль | Возможности |
|------|-------------|
| **Ученик** | Регистрация, просмотр репетиторов, бронирование слотов, просмотр уроков, переход по ссылкам на встречи |
| **Репетитор** | Профиль (предметы, био), управление слотами доступности, просмотр уроков, настройка URL встреч |
| **Общее** | JWT-аутентификация, статусы уроков: `scheduled` / `completed` / `cancelled` |

## Структура проекта

```
Project_one/
├── backend/          # FastAPI-приложение, Alembic
├── frontend/         # Vite + React + TypeScript
├── docker-compose.yml
├── Dockerfile        # Многоэтапная сборка (frontend + backend)
├── railway.toml
└── README.md
```

## Локальная разработка

### Требования

- Docker (для Postgres) или локальный PostgreSQL
- Python 3.12+
- Node.js 20+

### 1. Запуск PostgreSQL

```bash
docker compose up -d
```

Подключение по умолчанию: `postgresql+asyncpg://tutoring:tutoring@localhost:5432/tutoring`

### 2. Бэкенд

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# Применить миграции
alembic upgrade head

# Опционально: заполнить демо-данными
python -m scripts.seed

# Запустить API
uvicorn app.main:app --reload --port 8000
```

Переменные окружения (опционально `.env` в `backend/`):

| Переменная | Значение по умолчанию |
|----------|---------|
| `DATABASE_URL` | `postgresql+asyncpg://tutoring:tutoring@localhost:5432/tutoring` |
| `SECRET_KEY` | ключ для разработки (смените в production) |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:8000` |

### 3. Фронтенд

```bash
cd frontend
npm install
npm run dev
```

Откройте http://localhost:5173 — Vite проксирует `/api` на бэкенд.

Сборка фронтенда в `backend/static` (production-раскладка):

```bash
npm run build
```

Затем всё обслуживается через FastAPI на http://localhost:8000.

### Демо-аккаунты (после seed)

| Email | Пароль | Роль |
|-------|----------|------|
| `anna.tutor@example.com` | `password123` | Tutor |
| `petr.tutor@example.com` | `password123` | Tutor |
| `student@example.com` | `password123` | Student |

## API-эндпоинты

| Метод | Эндпоинт | Доступ |
|--------|----------|--------|
| GET | `/api/health` | public |
| POST | `/api/auth/register` | public |
| POST | `/api/auth/login` | public |
| GET | `/api/auth/me` | auth |
| GET | `/api/tutors` | public |
| GET | `/api/tutors/{id}` | public |
| PUT | `/api/tutors/me/profile` | tutor |
| GET | `/api/slots?tutor_id=` | public |
| POST | `/api/slots` | tutor |
| DELETE | `/api/slots/{id}` | tutor |
| POST | `/api/lessons` | student |
| GET | `/api/lessons/me` | auth |
| PATCH | `/api/lessons/{id}` | student/tutor |

## Деплой на Railway

1. Загрузите репозиторий на GitHub и создайте проект в Railway.
2. Добавьте плагин **PostgreSQL**.
3. Добавьте веб-сервис из репозитория. В **Settings → Root Directory** оставьте `/` (корень репозитория). Не указывайте `backend/` — Dockerfile копирует `frontend/` и `backend/` из корня; при root `backend/` сборка падает с `COPY frontend/ ... not found`.
4. Сборка идёт через `Dockerfile` в корне (`railway.toml` задаёт `builder = DOCKERFILE`).
5. Задайте переменные для веб-сервиса:
   - `DATABASE_URL` = `${{Postgres.DATABASE_URL}}` (автоматически конвертируется в asyncpg)
   - `SECRET_KEY` = случайная строка из 32+ символов
   - `CORS_ORIGINS` = ваш домен Railway (или `*` для демо)
6. Сгенерируйте домен в разделе Networking.

На бесплатном плане отключите **multi-region** (оставьте один регион, без реплик) — иначе деплой может не пройти.

Многоэтапная Docker-сборка компилирует React-приложение и копирует его в `backend/static`. FastAPI обслуживает SPA с fallback на `index.html`.

**Проверка работоспособности:** `GET /api/health` → `{"status":"ok"}`

## Лицензия

MIT
