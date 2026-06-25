#!/bin/sh
set -e

echo "PORT=${PORT:-8000}"

if [ -n "$DATABASE_URL" ]; then
  DB_HOST=$(printf '%s' "$DATABASE_URL" | sed -E 's#^[^:]+://([^@/]+@)?([^:/]+).*#\2#')
  DB_NAME=$(printf '%s' "$DATABASE_URL" | sed -E 's#^.*/([^/?]+)(\?.*)?$#\1#')
  MASKED=$(printf '%s' "$DATABASE_URL" | sed -E 's#(://)[^:@/]+(:[^@/]+)?@#://***:***@#')
  echo "DATABASE_URL host: ${DB_HOST} database: ${DB_NAME}"
  echo "DATABASE_URL (masked): ${MASKED}"
else
  echo "DATABASE_URL is not set"
fi

alembic upgrade head
echo "Alembic OK"

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
