# coffee-shop-backend-test-assignment

## Конфигурация
Создайте файл `.env` в корне проекта:
```
TOKEN=XXXXXXX
ADMIN_ID=XXXXXXX
ADMIN_USERNAME=XXXXXXX

DB_ENGINE=postgresql+psycopg
DB_USER=coffee
DB_PSWD=coffee
DB_DB=coffee
DB_HOST=db
DB_PORT=5432
DB_ECHO=True

BACKEND_PORT=8080
BACKEND_URL=http://back:8000
```

## Запуск
```bash
docker compose up -d --build
#или
docker-compose up -d --build
```

    OpenAPI DOC: http://127.0.0.1:${BACKEND_PORT}

## Недочёты
1. Не красиво возвращаю данные методами бд
2. Тайп хинты не везде точные
3. Иногда падает `httpx.ConnectError: All connection attempts failed`. Надо просто повторить попытку.